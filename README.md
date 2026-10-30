# Still-Flying?

## A short intro
In the past few months I've been binge-watching videos on aviation, both military and commercial, and one of them was about the DC10 and its infamous reputation. And while watching, I thought to myself, "Does this plane still fly passengers around?" This started a trend. When I discovered a certain older plane that itched that nerve, I would look up if any airframes still existed, leading me to this project.

The main purpose of this project is to showcase the history of aviation and help people find out if a certain plane still exists, where they can find it and maybe learn more about it.

## Project status

The project has completed the initial **data ingestion** phase (FAA active registrations, FAA deregistered records, and OpenSky aircraft datasets staged in Postgres) and is currently in the **data mapping & normalization** phase. Staged raw records are being analyzed and mapped into standardized aircraft types and variants before building the transform pipeline that will populate the core tables.

| Area | Status |
| --- | --- |
| Core schema (`aircraft_types`, `operators`, `airframes`, `status_events`) | Done (tables created) |
| Curated list of 50 aircraft types + seeding script | Done |
| FAA registry staging (`MASTER`, `ACFTREF`) | Done |
| OpenSky aircraft database staging | Done |
| FAA deregistered aircraft staging (`DEREG`) | Done |
| Data exploration notes on 7 "hero" types & quirks ([`DATA_NOTES.md`](docs/DATA_NOTES.md)) | Done |
| Model mapping dictionary ([`pipeline/mappings/type_map.csv`](pipeline/mappings/type_map.csv)) | In progress |
| Transform staging → core tables (`pipeline/`) | Next up |
| Website / search UI (`web/`) | Planned |

## Architecture

```
 FAA registry (.txt)          OpenSky aircraft DB (.csv)        aircraft_types.csv
  MASTER / ACFTREF / DEREG              │                              │
          │                             │                              │
  faa_staging.py               opensky_staging.py           seed_aircraft_types.py
  dereg_staging.py                      │                              │
          ▼                             ▼                              ▼
 ┌──────────────────────── PostgreSQL ────────────────────────────────────────┐
 │  Staging (all TEXT, truncated & reloaded each run)    Core schema          │
 │   raw_faa_master                                       aircraft_types  ◀── seeded
 │   raw_faa_acftref                                      operators           │
 │   raw_faa_dereg                                        airframes           │
 │   raw_opensky_aircraft        ── (pipeline/ & type_map) ▶ status_events    │
 └────────────────────────────────────────────────────────────────────────────┘
                                                              │
                                                     (planned) web UI
```

**Staging layer.** Each source gets a `raw_*` table where every column is `TEXT`, plus a `loaded_at` timestamp. Keeping everything as text means a blank field or a badly formatted date doesn't break the load; cleaning and type conversion are left to the transform step. Each loader script:

1. runs its `migrations/*_staging.sql` file (drop + recreate the table),
2. streams the source file with `csv.reader`, strips whitespace, and skips short/blank rows,
3. bulk-inserts in batches of 5,000 rows using `psycopg2.extras.execute_values`,
4. commits once at the end, or rolls back the whole load on error.

**Core schema** (`migrations/initial_schema.sql`):

- `aircraft_types` — manufacturer, model, variant, ICAO type code; unique on `(manufacturer, model)`.
- `operators` — name, country, ICAO/IATA codes.
- `airframes` — one row per physical aircraft: registration, ICAO24 hex, serial number, build date; references a type and an operator. Indexed on `icao24_hex`, `registration` and `type_id`.
- `status_events` — status history for an airframe (status, when, source, notes), so changes over time are kept rather than overwritten.

Only `aircraft_types` is populated so far.

## Data sources

| Source | Files | Loaded into |
| --- | --- | --- |
| [FAA Releasable Aircraft Registry](https://www.faa.gov/licenses_certificates/aircraft_certification/aircraft_registry/releasable_aircraft_download) | `FAA_data/MASTER.txt` | `raw_faa_master` |
| | `FAA_data/ACFTREF.txt` | `raw_faa_acftref` |
| | `FAA_data/DEREG.txt` | `raw_faa_dereg` |
| | `DEALER`, `DOCINDEX`, `ENGINE`, `RESERVED` | not used yet |
| [OpenSky Network aircraft database](https://opensky-network.org/datasets/metadata/) (Aug 2025 snapshot) | `aircraft-database-complete-2025-08.csv` | `raw_opensky_aircraft` |
| Hand-curated list | `aircraft_types.csv` (`;`-delimited, 50 types) | `aircraft_types` |

The data files are large (the FAA `MASTER` and `DEREG` files and the OpenSky CSV are each 100 MB+) and need to be downloaded separately.

## Repository layout

```
config.py                 # reads Postgres connection settings from database.ini
connect.py                # opens a psycopg2 connection
insert.py                 # insert helper for aircraft_types
seed_aircraft_types.py    # loads aircraft_types.csv into aircraft_types
faa_staging.py            # loads MASTER + ACFTREF into raw_faa_* tables
opensky_staging.py        # loads the OpenSky CSV into raw_opensky_aircraft
dereg_staging.py          # loads DEREG into raw_faa_dereg
pipeline/
  mappings/
    type_map.csv          # maps raw FAA/OpenSky models to canonical type codes & variants
migrations/
  initial_schema.sql      # core tables + indexes
  faa_staging.sql         # raw_faa_master, raw_faa_acftref
  opensky_staging.sql     # raw_opensky_aircraft
  dereg_staging.sql       # raw_faa_dereg
  test script.sql         # exploration / scratch queries (e.g. 727 model patterns)
queries/
  faa_master_acftref_join.sql  # reference join of MASTER to ACFTREF (run manually)
docs/
  writeup.md              # day-by-day project write-up
  DATA_NOTES.md           # notes on 7 hero types, record counts, and raw data quirks
web/                      # reserved for the web UI / search app
```

## Running it

Requirements: Python 3 and a PostgreSQL database.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Create `database.ini` in the project root (it is git-ignored):

```ini
[postgresql]
host=...
port=5432
database=...
user=...
password=...
```

Then, from the project root:

```bash
psql -f migrations/initial_schema.sql   # create core tables (drops existing ones!)
python seed_aircraft_types.py           # seed the 50 aircraft types
python faa_staging.py                   # stage FAA MASTER + ACFTREF
python opensky_staging.py               # stage OpenSky aircraft DB
python dereg_staging.py                 # stage FAA DEREG
```

Every staging script drops and recreates its tables, so re-running it replaces the previous load.
