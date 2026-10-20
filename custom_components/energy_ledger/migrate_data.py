"""Offline, lossless import of a legacy ledger; never copy API credentials.

Run only while Home Assistant and the legacy ledger workers are stopped:
python migrate_data.py /path/to/legacy/data /config/.storage/energy_ledger/ENTRY_ID
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile

# The old first migration additionally created an unused charger-event table.
_LEGACY_INITIAL = '43f1e39989c83fcd90ef6481edaba7f47784df2ff397d5c3b91be72725891cea'


def import_data(source_dir, destination):
    source_dir = Path(source_dir).resolve()
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError('Destination already exists; refusing to replace any ledger')
    if not (source_dir/'ledger.sqlite3').is_file():
        raise ValueError('Source ledger.sqlite3 is missing')
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.ledger-import-', dir=destination.parent))
    try:
        with sqlite3.connect((source_dir/'ledger.sqlite3').as_uri()+'?mode=ro', uri=True) as source:
            with sqlite3.connect(stage/'ledger.sqlite3') as target:
                source.backup(target)
        with sqlite3.connect(stage/'ledger.sqlite3') as connection:
            if connection.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise ValueError('Source database failed integrity verification')
            migrations = Path(__file__).parent/'backend'/'migrations'
            expected = {int(p.name.split('_')[0]): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in migrations.glob('[0-9][0-9][0-9]_*.sql')}
            for version, checksum in connection.execute('SELECT version,checksum FROM schema_migration').fetchall():
                if version == 1 and checksum == _LEGACY_INITIAL:
                    table = connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='zappi_event'").fetchone()
                    if table is None:
                        raise ValueError('Legacy schema fingerprint does not match its tables')
                    connection.execute('UPDATE schema_migration SET checksum=? WHERE version=1', (expected[1],))
                elif expected.get(version) != checksum:
                    raise ValueError(f'Unsupported schema checksum at migration {version}')
            for name in ('evidence', 'inbox', 'outbox', 'reports'):
                if (source_dir/name).exists():
                    shutil.copytree(source_dir/name, stage/name)
            for row_id, digest in connection.execute('SELECT id,sha256 FROM evidence').fetchall():
                file = stage/'evidence'/digest[:2]/digest
                if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest() != digest:
                    raise ValueError('An evidence file is missing or its checksum differs')
                connection.execute('UPDATE evidence SET storage_path=? WHERE id=?',
                    (str(destination/'evidence'/digest[:2]/digest), row_id))
            tables = [row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")]
            counts = {name: connection.execute('SELECT COUNT(*) FROM "'+name.replace('"','""')+'"').fetchone()[0] for name in tables}
        for path in stage.rglob('*'):
            os.chmod(path, 0o700 if path.is_dir() else 0o600)
        os.replace(stage, destination)
        return {'integrity': 'ok', 'table_row_counts': counts}
    finally:
        if stage.exists():
            shutil.rmtree(stage)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source_data_directory')
    parser.add_argument('destination_data_directory')
    args = parser.parse_args()
    print(json.dumps(import_data(args.source_data_directory, args.destination_data_directory)))
