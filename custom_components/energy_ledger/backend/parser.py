from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from zoneinfo import ZoneInfo

from pypdf import PdfReader

PARSER_VERSION = "geni-si-v3"


class ParseReview(ValueError):
    pass


class ParseReject(ValueError):
    pass


def decimal_si(value: str) -> Decimal:
    return Decimal(value.strip().replace(".", "").replace(",", "."))


def money_micro(value: str) -> int:
    return int((decimal_si(value) * 1_000_000).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def normalize(text: str) -> str:
    return text.replace("\xa0", " ").replace("\u202f", " ").replace("\r", "")


def match(pattern: str, text: str, flags: int = 0, review: bool = True) -> re.Match:
    result = re.search(pattern, text, flags)
    if result is None:
        exc = ParseReview if review else ParseReject
        raise exc(f"required field missing: {pattern}")
    return result


def page_total(page: str) -> int:
    values = re.findall(r"(?m)^Skupaj\s+(-?\d[\d.]*,\d{2})\s*$", page)
    if not values:
        raise ParseReview("meter subtotal missing")
    # A page may contain both estimated and actual settlement sections.
    return sum(money_micro(value) for value in values)


@dataclass(frozen=True)
class ParsedInvoice:
    supplier: str
    invoice_number: str
    period_start: str
    period_end: str
    peak_wh: int
    offpeak_wh: int
    electricity_wh: int
    blocks_wh: dict[str, int | None]
    electricity_net_micro_eur: int
    gas_millim3: int | None
    gas_wh: int | None
    gas_net_micro_eur: int | None
    net_micro_eur: int
    vat_basis_points: int
    vat_micro_eur: int
    gross_micro_eur: int
    informative_excess_micro_eur: int | None
    parser_version: str = PARSER_VERSION

    def to_dict(self) -> dict:
        return asdict(self)


def parse_geni_pages(pages: list[str], timezone_name: str = "UTC") -> ParsedInvoice:
    if len(pages) < 2:
        raise ParseReview("GEN-I invoice must contain summary and electricity pages")
    pages = [normalize(p) for p in pages]
    all_text = "\n".join(pages)
    if "GEN-I" not in all_text or "RAČUN" not in all_text.upper():
        raise ParseReview("unsupported supplier/template")
    summary, electricity = pages[0], pages[1]
    gas_page = next((p for p in pages[2:] if "ZEMELJSKI PLIN" in p.upper()), None)
    invoice_number = match(r"Račun\s+številka:\s*(IR\d+)", all_text, re.I).group(1)
    period = match(r"(\d{2})\.\s*(\d{2})\.\s*(\d{4})\s*[-–]\s*(\d{2})\.\s*(\d{2})\.\s*(\d{4})", electricity)
    start_date = datetime(int(period.group(3)), int(period.group(2)), int(period.group(1)), tzinfo=ZoneInfo(timezone_name))
    inclusive_end = datetime(int(period.group(6)), int(period.group(5)), int(period.group(4)), tzinfo=ZoneInfo(timezone_name))
    if inclusive_end < start_date or (inclusive_end - start_date).days > 62:
        raise ParseReject("invalid invoice period")
    end_exclusive = inclusive_end + timedelta(days=1)
    peak = int(match(r"Energija[^\S\n]+VT[^\n]*[^\S\n]+(\d+)[^\S\n]*$", electricity, re.M).group(1))
    offpeak = int(match(r"Energija[^\S\n]+MT[^\n]*[^\S\n]+(\d+)[^\S\n]*$", electricity, re.M).group(1))
    blocks: dict[str, int | None] = {str(i): None for i in range(1, 6)}
    for number, quantity in re.findall(r"Prevzeta EE za časovni blok\s+([1-5])[^\n]*?\s(\d+)\s+kWh", electricity):
        blocks[number] = int(quantity) * 1000
    total_wh = (peak + offpeak) * 1000
    block_values = [v for v in blocks.values() if v is not None]
    if block_values and sum(block_values) != total_wh:
        raise ParseReject("electricity block sum mismatch")
    electricity_net = page_total(electricity)
    net = money_micro(match(r"(\d[\d.]*,\d{2})\s*€\s*Skupaj vsa merilna mesta", summary).group(1))
    vat_match = match(r"(\d[\d.]*,\d{2})\s*€\s*Znesek DDV\s*\(stopnja\s*(\d+[,.]\d+)\s*%\)", summary)
    vat = money_micro(vat_match.group(1))
    vat_bp = int((decimal_si(vat_match.group(2)) * 100).quantize(Decimal("1")))
    gross = money_micro(match(r"(\d[\d.]*,\d{2})\s*€\s*Skupaj znesek računa z DDV", summary).group(1))
    gas_millim3 = gas_wh = gas_net = None
    if gas_page:
        gas_values = re.findall(
            r"OD\s+(?:\d{2}\.\s*\d{2}\.\s*\d{4}).*?DO\s+(?:\d{2}\.\s*\d{2}\.\s*\d{4})\s+([\d.]+)\s+([\d.]+)\s+(\d+)\s+([\d,]+)\s+([\d,]+)\s+(\d+)",
            gas_page,
            re.S,
        )
        if not gas_values:
            raise ParseReview("gas meter quantities missing")
        gas_millim3 = sum(int(values[2]) for values in gas_values) * 1000
        gas_wh = sum(int(values[5]) for values in gas_values) * 1000
        gas_net = page_total(gas_page)
    expected_net = electricity_net + (gas_net or 0)
    if expected_net != net:
        raise ParseReject("meter subtotals do not equal invoice net")
    if abs((net + vat) - gross) > 10_000:
        raise ParseReject("invoice VAT arithmetic mismatch")
    informative = re.search(r"Informativna presežna obr\. moč[^\n]*\s(-?\d[\d.]*,\d{2,5})\s*$", electricity, re.M)
    return ParsedInvoice(
        supplier="GEN-I", invoice_number=invoice_number,
        period_start=start_date.astimezone(timezone.utc).isoformat(),
        period_end=end_exclusive.astimezone(timezone.utc).isoformat(),
        peak_wh=peak*1000, offpeak_wh=offpeak*1000, electricity_wh=total_wh,
        blocks_wh=blocks, electricity_net_micro_eur=electricity_net,
        gas_millim3=gas_millim3, gas_wh=gas_wh, gas_net_micro_eur=gas_net,
        net_micro_eur=net, vat_basis_points=vat_bp, vat_micro_eur=vat,
        gross_micro_eur=gross,
        informative_excess_micro_eur=money_micro(informative.group(1)) if informative else None,
    )


def parse_geni_pdf(path: Path, timezone_name: str = "UTC") -> ParsedInvoice:
    reader = PdfReader(str(path))
    if reader.is_encrypted or len(reader.pages) > 50:
        raise ParseReview("encrypted PDFs and invoices over 50 pages require manual review")
    pages = [page.extract_text() or "" for page in reader.pages]
    if not any(p.strip() for p in pages):
        raise ParseReview("native text missing; OCR review required")
    return parse_geni_pages(pages, timezone_name)


def parse_invoice_pdf(path: Path, timezone_name: str = "UTC") -> ParsedInvoice:
    """Dispatch a supported native-text invoice to its supplier parser."""
    reader = PdfReader(str(path))
    if reader.is_encrypted or len(reader.pages) > 50:
        raise ParseReview("encrypted PDFs and invoices over 50 pages require manual review")
    pages = [page.extract_text() or "" for page in reader.pages]
    if not any(page.strip() for page in pages):
        raise ParseReview("native text missing; OCR review required")
    text = "\n".join(pages).upper()
    if "GEN-I" in text:
        return parse_geni_pages(pages, timezone_name)
    raise ParseReview("unsupported invoice supplier/template")
