import asyncio
import io
import json
import socket
import sqlite3
from datetime import datetime
from pathlib import Path

import pytest
from pypdf import PdfWriter

from custom_components.energy_ledger.local import LocalLedgerClient, LedgerError
from custom_components.energy_ledger.backend.worker import process_once


def client(tmp_path, timezone='Europe/Ljubljana'):
    return LocalLedgerClient(tmp_path, {'timezone': timezone, 'vehicle_name': 'Test EV'})


def test_local_reports_need_no_network_socket_and_persist(tmp_path, monkeypatch):
    def reject_network(*args, **kwargs):
        raise AssertionError('A local ledger must not connect to a server')
    monkeypatch.setattr(socket.socket, 'connect', reject_network)
    first = client(tmp_path)
    assert first.request('GET', '/api/v1/months')['months']
    first.request('POST', '/api/v1/months/2026-03/reimbursement-rate',
                  json={'rate_eur_per_kwh': '0.25'})
    first.request('POST', '/api/v1/months/2026-03/home-usage', json={
        'energy_wh': 10000, 'source': 'synthetic-test', 'quality': 'complete',
        'detail': {'month_complete': True},
    })
    report = client(tmp_path).request('GET', '/api/v1/months/2026-03/register')
    assert report['home_kwh'] == '10.000'
    assert report['home_reimbursement_eur'] == '2.50'
    assert not list(tmp_path.glob('*token*'))


def test_month_end_expenses_idempotency_and_reported_snapshot(tmp_path):
    ledger = client(tmp_path)
    payload = {'month': '2026-03', 'date': '2026-03-12', 'kind': 'PUBLIC',
               'provider': 'Synthetic charger', 'gross_eur': '12.34', 'eligible': True,
               'energy_kwh': '20', 'idempotency_key': 'expense-test'}
    first = ledger.request('POST', '/api/v1/register/expense', json=payload)
    second = ledger.request('POST', '/api/v1/register/expense', json=payload)
    assert first == second
    assert len(ledger.request('GET', '/api/v1/months/2026-03/register')['expenses']) == 1
    with pytest.raises(LedgerError) as error:
        ledger.request('POST', '/api/v1/register/expense', json={**payload, 'gross_eur': '15.00'})
    assert error.value.status == 409
    ledger.request('POST', '/api/v1/months/2026-03/home-usage', json={
        'energy_wh': 1000, 'source': 'test', 'quality': 'complete', 'detail': {'month_complete': True}})
    ledger.request('POST', '/api/v1/months/2026-03/reimbursement-rate', json={'rate_eur_per_kwh': '0.25'})
    ledger.request('POST', '/api/v1/months/2026-03/reported', json={'amount_eur': '12.59', 'idempotency_key': 'report-test'})
    with pytest.raises(LedgerError) as error:
        ledger.request('POST', '/api/v1/months/2026-03/reported', json={'amount_eur': '1.00', 'idempotency_key': 'different-report'})
    assert error.value.status == 409


def test_invoice_upload_is_validated_and_processed_locally(tmp_path):
    ledger = client(tmp_path)
    with pytest.raises(LedgerError) as error:
        ledger.request('POST', '/api/v1/invoices', files={'file': ('test.pdf', b'not a PDF', 'application/pdf')},
                       headers={'Idempotency-Key': 'bad-pdf'})
    assert error.value.status == 415
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    stream = io.BytesIO()
    writer.write(stream)
    body = stream.getvalue()
    kwargs = {'files': {'file': ('synthetic.pdf', body, 'application/pdf')},
              'headers': {'Idempotency-Key': 'synthetic-pdf'}}
    result = ledger.request('POST', '/api/v1/invoices', **kwargs)
    assert ledger.request('POST', '/api/v1/invoices', **kwargs)['job_id'] == result['job_id']
    assert process_once(tmp_path/'inbox', tmp_path/'outbox', 'Europe/Ljubljana') == 1
    ledger.request('GET', '/api/v1/months/2026-03/summary')
    job = ledger.request('GET', '/api/v1/invoice-jobs/' + result['job_id'])
    assert job['state'] == 'REVIEW'
    assert job['progress']['terminal'] is True


def test_instance_timezone_isolation_and_legacy_database_import(tmp_path):
    first = client(tmp_path/'one', 'Europe/Ljubljana')
    db = first.app.state.ledger_db
    db.ensure_month('2026-03')
    with db.connect() as connection:
        row = connection.execute("SELECT period_start_utc FROM month_revision WHERE year_month='2026-03'").fetchone()
    assert row[0].startswith('2026-02-28T23:00:00')
    # SQLite's backup API models a migration from the former backend.
    (tmp_path/'two').mkdir()
    with sqlite3.connect(db.path) as source, sqlite3.connect(tmp_path/'two'/'ledger.sqlite3') as target:
        source.backup(target)
    restored = client(tmp_path/'two', 'Europe/Ljubljana')
    assert restored.app.state.ledger_db.migration_status()['ok'] is True
    utc = client(tmp_path/'utc', 'UTC')
    utc.request('GET', '/api/v1/months/2026-03/summary')
    with utc.app.state.ledger_db.connect() as connection:
        row = connection.execute("SELECT period_start_utc FROM month_revision WHERE year_month='2026-03'").fetchone()
    assert row[0].startswith('2026-03-01T00:00:00')
    assert first.request('GET', '/api/v1/months/2026-03/summary')['month'] == '2026-03'


def test_engine_lifecycle_and_invalid_inputs(tmp_path):
    ledger = client(tmp_path)
    async def run():
        await ledger.async_start()
        await asyncio.sleep(0.02)
        await ledger.async_stop()
    asyncio.run(run())
    with pytest.raises(LedgerError) as error:
        ledger.request('GET', '/api/v1/months/invalid/summary')
    assert error.value.status == 422
    with pytest.raises(LedgerError):
        ledger.request('POST', '/api/v1/months/2026-03/odometer', json={'odometer_km': -1, 'observed_at': 'invalid'})


def test_offline_import_preserves_history_and_refuses_overwrite(tmp_path):
    from custom_components.energy_ledger.migrate_data import import_data
    source = client(tmp_path/'source')
    source.request('POST', '/api/v1/months/2026-03/reimbursement-rate', json={'rate_eur_per_kwh': '0.27'})
    source.request('POST', '/api/v1/months/2026-03/home-usage', json={
        'energy_wh': 123000, 'source': 'synthetic', 'quality': 'complete', 'detail': {'month_complete': True}})
    before = source.request('GET', '/api/v1/months/2026-03/register')
    destination = tmp_path/'imported'
    result = import_data(tmp_path/'source', destination)
    assert result['integrity'] == 'ok'
    assert client(destination).request('GET', '/api/v1/months/2026-03/register') == before
    with pytest.raises(ValueError, match='already exists'):
        import_data(tmp_path/'source', destination)
    assert source.request('GET', '/api/v1/months/2026-03/register') == before


def test_offline_import_accepts_only_known_legacy_schema(tmp_path):
    from custom_components.energy_ledger.migrate_data import import_data, _LEGACY_INITIAL
    source = client(tmp_path/'source')
    with source.app.state.ledger_db.transaction() as connection:
        connection.execute('CREATE TABLE zappi_event (id INTEGER PRIMARY KEY)')
        connection.execute('UPDATE schema_migration SET checksum=? WHERE version=1', (_LEGACY_INITIAL,))
    import_data(tmp_path/'source', tmp_path/'imported')
    assert client(tmp_path/'imported').app.state.ledger_db.migration_status()['ok'] is True
    with source.app.state.ledger_db.transaction() as connection:
        connection.execute("UPDATE schema_migration SET checksum='unrecognized' WHERE version=1")
    with pytest.raises(ValueError, match='Unsupported schema checksum'):
        import_data(tmp_path/'source', tmp_path/'rejected')
    assert not (tmp_path/'rejected').exists()


def test_offline_import_includes_uncheckpointed_wal(tmp_path):
    from custom_components.energy_ledger.migrate_data import import_data
    source = client(tmp_path/'source')
    # Keep a reader open so the committed record remains in the WAL.
    hold = sqlite3.connect(source.app.state.ledger_db.path)
    hold.execute('PRAGMA journal_mode=WAL')
    hold.execute('SELECT * FROM ev_reimbursement_rate').fetchall()
    source.request('POST', '/api/v1/months/2026-03/reimbursement-rate', json={'rate_eur_per_kwh': '0.31'})
    assert Path(str(source.app.state.ledger_db.path)+'-wal').exists()
    import_data(tmp_path/'source', tmp_path/'imported')
    assert client(tmp_path/'imported').request('GET', '/api/v1/months/2026-03/register')['reimbursement_rate'] == '0.31'
    hold.close()
