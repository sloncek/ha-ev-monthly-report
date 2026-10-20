# Energy Ledger — EV Monthly Report

A standalone Home Assistant integration for monthly home EV charging, reimbursement records and mileage forecasts.

**Install it through HACS. No additional Docker container, add-on, API server or external database is required.** The reporting engine, SQLite storage, PDF parser and sidebar panel run inside Home Assistant. Required Python libraries are installed automatically by Home Assistant.

## Features

- Monthly home charging energy from a Recorder energy statistic that you select.
- Your own reimbursement rate, public charging and other manually entered expenses.
- Reported amounts and carry-forward balances, with reported months preserved as snapshots.
- Odometer readings from a sensor you select, with manual month-end entry when needed.
- Mileage forecasts based on this installation's own monthly readings; optional mileage allowance and contract end month.
- Optional native-text GEN-I PDF invoice import and Moj Elektro reconciliation.

The integration is vehicle-neutral. It does not log in to a car manufacturer's cloud. Install the relevant vehicle and charger integrations separately and select their sensors.

## Installation

Requires **Home Assistant 2026.9 or newer**, Recorder and HACS.

1. Open **HACS → ⋮ → Custom repositories**.
2. Add `https://github.com/sloncek/ha-ev-monthly-report` with type **Integration**.
3. Find **EV Monthly Report**, open it and select **Download**.
4. Restart Home Assistant.
5. Open **Settings → Devices & services → Add integration → Energy Ledger**.
6. Enter a vehicle name, time zone, odometer sensor entity and home charging energy statistic ID. Sensor mappings are optional during setup and can be changed later.

The sidebar report panel is installed with the integration. There is no separate JavaScript resource to copy or configure. The report panel and setup support English and Slovenian. The panel follows each Home Assistant user’s language setting, with English as the fallback for other languages. Numbers and timestamps follow the user’s formatting preferences. Changing the language updates the panel without clearing unfinished inputs.

## Choose the right sensors

- **Odometer:** an entity whose value is the vehicle's odometer in kilometres. Only observations received on the last day of the local calendar month count as automatic month-end readings. Otherwise enter the missing month-end reading manually.
- **Home charging energy:** a Recorder statistic measuring this EV's charging energy in kWh. It must have valid hourly cumulative `sum` statistics, normally from a `total` or `total_increasing` sensor. Whole-house energy is not a substitute for charging energy.
- **Time zone:** the local time zone used for month boundaries, for example `Europe/Ljubljana`.

Missing history remains missing. The integration does not invent zero consumption or borrow another vehicle's history. A forecast needs at least three consecutive valid monthly distances.

## Settings and daily use

Open the integration's **Configure** dialog to update the sensor mappings, time zone, optional mileage allowance and contract end month (`YYYY-MM`). A mileage allowance of `0` disables the configured plan.

In the sidebar report, select a month and enter your reimbursement rate, public charging or other expenses. Mark a month as reported only after you have actually submitted that amount. The integration prepares text for your email; it does not send email or submit a claim.

Reported months keep their original snapshots. Later energy corrections appear as a pending difference. Reimbursement rates and eligibility rules are user-supplied; the integration does not include a default employer tariff.

## Optional PDF invoices and Moj Elektro

PDF parsing runs locally inside Home Assistant's executor. The parser currently supports a limited native-text GEN-I invoice layout. Scans, encrypted PDFs, invoices over 50 pages and unsupported layouts require manual review. Uploads are limited to 15 MiB; your HA HTTP limit may be lower. Check every parsed result before using it.

Moj Elektro is optional. In **Configure**, enter both your usage point and your own Moj Elektro API token to enable reconciliation. Leave both fields empty to keep it disabled. Only this optional feature contacts the Moj Elektro API; ordinary reports and forecasts are local.

## Storage, access and backups

Data is stored under:

```text
/config/.storage/energy_ledger/<config-entry-id>/
```

This contains `ledger.sqlite3`, invoice evidence and import state. Include it in your Home Assistant backups. The public repository contains code and synthetic tests, not your ledger, invoices, tokens or vehicle history.

The report panel and its HTTP views require a Home Assistant administrator. Integration sensors are normal HA entities and follow your installation's usual entity visibility. Do not expose sensitive report entities to users who should not see them.

## Migrating from the former Docker version

Version `0.4.0` uses local storage and no longer uses the old backend URL or its read/write/signing credentials. The configuration entry keeps its identity, entity mappings and selected month. **The old external database must be imported separately before starting the standalone version.** Updating the integration alone does not transfer the old database.

1. Back up the old backend data, installed integration and HA configuration.
2. Download the new integration through HACS, but do not restart it yet.
3. Stop Home Assistant and the old API/parser workers so there is a stable migration boundary.
4. Run the bundled offline importer in a Python environment that can read both paths:

   ```sh
   python /config/custom_components/energy_ledger/migrate_data.py \
     /path/to/old/backend/data \
     /config/.storage/energy_ledger/CONFIG_ENTRY_ID
   ```

   Replace the paths and entry ID. The importer takes a SQLite backup, verifies integrity, checks known schema fingerprints and evidence hashes, and copies the evidence and import files. It refuses to replace an existing destination and leaves the source untouched.
5. Set your vehicle name, time zone and sensor mappings in the existing entry. If you used Moj Elektro, transfer its settings separately. The data importer does not copy credentials.
6. Start Home Assistant, verify the old months and reported amounts, then keep the old backend stopped. Retain the old data and backup until you have verified the migration.

The legacy Docker source remains available in Git history and tag `v0.3.0` for rollback.

## Development

GitHub is the main source. Work in a branch and submit a pull request. A NAS mirror should pull from GitHub; avoid automatic force-push mirrors in both directions.

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest
npm ci --ignore-scripts
npm test
node --check custom_components/energy_ledger/www/energy_ledger_panel.js
```

Tests use synthetic data and exercise local operation without network sockets, persistence, idempotency, reported snapshots, PDF validation, migration and time-zone isolation. HACS and Hassfest validation run in GitHub Actions.
