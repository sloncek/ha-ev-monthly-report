# Sync the monthly ledger to Google Sheets with n8n

This optional export is designed for a dedicated spreadsheet tab such as `HA Sync`. It does not expose the integration's expense rows, notes, legacy imports, source hashes, audit data, invoice evidence, or entity identifiers. The endpoint is read-only and returns a schema-versioned monthly projection.

## Prerequisites

- Energy Ledger 0.4.3 or later (this export is not present in 0.4.2).
- n8n with a Google Sheets OAuth credential that can edit the target spreadsheet.
- A dedicated tab with the headers in `n8n/ha-energy-ledger-sync.json` / this document's workflow mapping. Do not point it at the source ledger tab.
- Network connectivity from n8n to Home Assistant. Use HTTPS or a private authenticated tunnel, including on a LAN; plain HTTP exposes the bearer token to anyone who can observe that network traffic.

## Configure Home Assistant

1. Create a random export secret locally, for example with `openssl rand -hex 32`.
2. In **Settings → Devices & services → Energy Ledger → Configure**, enter the value in **Google Sheets export token**. This value is stored as an integration option and is never part of the n8n workflow export.
3. The endpoint is `GET https://YOUR_HA_HOST/api/energy_ledger/sheet-export`, with `Authorization: Bearer YOUR_EXPORT_TOKEN`. An unset token disables access. The endpoint does not accept writes and does not grant general Home Assistant API access.

## Import and configure n8n

1. Import `n8n/ha-energy-ledger-sync.json` into n8n.
2. Edit the HTTP Request node URL to your Home Assistant URL and select/create an **HTTP Header Auth** credential with header `Authorization` and value `Bearer <export token>`. Keep the token in the credential store, never in node parameters or exported workflow JSON.
3. Edit the Google Sheets node to select the existing Google OAuth credential, target spreadsheet, and dedicated `HA Sync` tab. The workflow template intentionally has no spreadsheet ID or credential IDs.
4. Confirm the sheet has a `month` column; the workflow matches on that key and uses append-or-update, so reruns update the same month instead of duplicating rows.
5. Review n8n execution-data retention. The response is already allowlisted, but it still contains monthly household and reimbursement totals. Disable successful execution payload storage if you do not need it, and configure short retention for failures.
6. Test manually, inspect the rows, then activate the schedule.

The schedule is every 30 minutes by default. The export reports the latest monthly register state; reported financial snapshots remain immutable in Energy Ledger, while its pending home-energy delta can change. Blank/null values should remain blank in Sheets.

Use these exact headers in row 1 of the destination tab; automatic mapping depends on exact header names:

```text
month,status,odometer_km,monthly_distance_km,home_kwh,reimbursement_rate,home_reimbursement_eur,public_gross_eur,other_gross_eur,eligible_expenses_eur,monthly_eligible_eur,opening_balance_eur,requested_eur,reported_eur,closing_balance_eur,pending_home_delta_eur,pending_delta_verified,energy_complete,month_complete,source_quality,ready_to_report,public_energy_complete,current_home_kwh,current_source_quality,reported_at
```

## Exported columns

`month`, `status`, `odometer_km`, `monthly_distance_km`, `home_kwh`, `reimbursement_rate`, `home_reimbursement_eur`, `public_gross_eur`, `other_gross_eur`, `eligible_expenses_eur`, `monthly_eligible_eur`, `opening_balance_eur`, `requested_eur`, `reported_eur`, `closing_balance_eur`, `pending_home_delta_eur`, `pending_delta_verified`, `energy_complete`, `month_complete`, `source_quality`, `ready_to_report`, `public_energy_complete`, `current_home_kwh`, `current_source_quality`, `reported_at`.

The generic template contains no personal spreadsheet URL or ID, household location, HA/NAS address, bearer token, OAuth credential, invoice, or ledger rows. Do not add those values to this public repository when adapting it.
