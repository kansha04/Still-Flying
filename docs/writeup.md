# Still Flying Write Up

Hi there! I will be writing my first code write-up, which will be detailing the journey of this project and the decisions that went into each feature and piece of code.

## Week 1
On **day 1** I did the main project setup, which consisted of setting up the repo, the python environment and all the required libraries along with creating a Postgres database on Supabase (got stopped a little later).

**Day 2** was a day of learning where I read up on some aviation data basics such as ICAO type designators and ICAO24 Hex Addresses; it was actually quite cool to see how planes are identified as it's not as simple as just taking the ICAO type designator as that can cover many variants. For example, a Boeing 737-8 has an ICAO type designator of **B738**; however, both the passenger and freight variants carry this ICAO. Apart from that day 2 also consisted of creating a curated list of 50 different aircraft types in a seeding file.

**Day 3** I started building the first schema, it took a bit of time as I was still learning normalization at school, however, I ended up with four main tables; `aircraft_types` which would be seeded with the 50 types from yesterday's list, `airframes`, `operators` and `status_events` to keep history.

**Day 4** was about getting real data into the database. I wrote the plumbing to talk to Postgres: `config.py` reads the connection details from a `database.ini` file (kept out of git), `connect.py` opens the connection, and `insert.py` has an insert helper for `aircraft_types`. With that in place, `seed_aircraft_types.py` went from just printing the CSV to actually loading the 50 types, committing once at the end and rolling back if anything fails. I also added a unique constraint on `(manufacturer, model)` so running the seed twice doesn't create duplicates (`ON CONFLICT DO NOTHING`).

The bigger piece was the FAA Releasable Aircraft Registry. I set up a **staging layer**: raw `raw_faa_master` and `raw_faa_acftref` tables where every column is `TEXT`. The FAA files are full of blanks and padded fields, so storing everything as text means the load doesn't fall over on a bad date, and the cleaning can happen later. `faa_staging.py` creates the tables, streams each file and bulk-inserts it in batches of 5,000 rows with `execute_values`. `MASTER` (current registrations) links to `ACFTREF` (make/model reference) through the manufacturer-model code, and I wrote an example join for that (now in `queries/faa_master_acftref_join.sql`).

**Day 5** I added a second source, the OpenSky Network aircraft database (August 2025 snapshot). This one is worldwide rather than US-only and keys aircraft by their ICAO24 hex address, which is the same identifier the `airframes` table uses. `opensky_staging.py` follows the same pattern as the FAA loader and fills `raw_opensky_aircraft`. One gotcha: the OpenSky CSV quotes fields with single quotes, so the reader needs `quotechar="'"`.

## Week 2
**Day 6** I started on the FAA deregistered aircraft file (`DEREG.txt`). Since the whole point of the project is finding out whether a plane is *still* around, the record of aircraft that have been taken off the register (with a cancel date) matters as much as the current one. `dereg_staging.py` and `migrations/dereg_staging.sql` load it into `raw_faa_dereg` the same way as the other sources.

I also began exploring the staged OpenSky data for my "hero" types, the DC-10, the 727 and the A310, to see how they actually show up in the raw data (model naming, type codes, missing build years). Those notes are in [`DATA_NOTES.md`](DATA_NOTES.md) and will feed the matching rules for the transform step.

**Day 7-9** I started working on a mapping table to match the FAA data to the OpenSky data. I took an approach of hand-writing each model string to map them into the `aircraft_types` table (`pipeline/mappings/type_map.csv`).
The problem this solves is the FAA staging data has a lot of variation in the model names, for example:
```
MCDONNELL DOUGLAS  DC-10-10
MCDONNELL DOUGLAS  DC-10-30F
MCDONNELL DOUGLAS  DC-10-40
BOEING             DC-10-30
MCDONNELL DOUGLAS  MD-10-10F
LOCKHEED           L-1011-385-1
LOCKHEED           L-1011-385-3
```
A model might be part of a family, but using a simple string match is not enough. In this case an MD-10 is a converted DC-10. Another thing I noticed when mapping the DC-10 was that in the OpenSky data, many KC-10s (military air tankers) were still listed under the Air Mobility Command even though the USAF retired the plane in 2024. Understandably the data was from 2020 so the registries lagging behind is a problem that I hope to fix with ADS-B data down the line.

Another issue was Boeing. Boeing names their models like let’s say the 727-100 or 727-200 with a customer code and feature code as referenced in `DATA_NOTES.md`. This means a Boeing 727-100 could be listed as `727-22` (a 727-100 built for United Airlines), or a 727-200 could appear as `727-225` (built for Eastern Airlines), often appended with modifiers like `RE` (re-engined) or `W` (winglets). On the 747-200, strings vary between spaces and hyphens (`747 251B` vs `747-251B`), and some records have blank model strings entirely.

To make the data reliable, I expanded the research in [`DATA_NOTES.md`](DATA_NOTES.md) across seven "hero" aircraft types:
1. **McDonnell Douglas DC-10** (149 in OpenSky, 26 active FAA, 258 FAA deregistered)
2. **Boeing 727** (109 in OpenSky, 37 active FAA, 1,571 FAA deregistered)
3. **Airbus A310** (103 in OpenSky, 4 active FAA, 109 FAA deregistered)
4. **Vickers VC10** (4 in OpenSky, 0 FAA — UK military airframes)
5. **Mikoyan MiG-21** (29 in OpenSky, 23 active FAA, 21 FAA deregistered)
6. **Lockheed L-1011 TriStar** (7 in OpenSky, 4 active FAA, 187 FAA deregistered)
7. **Boeing 747-200** (56 in OpenSky, 7 active FAA, 238 FAA deregistered)

Looking at these counts highlighted just how vital the `DEREG` data is: for types like the 727, L-1011, and 747-200, the vast majority of historical airframes exist exclusively in deregistration records. I also documented key cross-source quirks, such as ICAO24 hex addresses being lowercase in OpenSky (`icao24`) and uppercase in FAA (`mode_s_code_hex`), as well as pervasive missing fields in OpenSky (such as ~73% missing `built` dates).

The curated mapping in `pipeline/mappings/type_map.csv` now maps raw manufacturer and model strings from both sources directly to normalized `type_code` and `variant` labels, forming the backbone for the upcoming transform pipeline.

## Where things stand

**Built so far:**
- **Core schema**: `aircraft_types`, `operators`, `airframes`, `status_events` defined in Postgres with proper indexing.
- **Seeded aircraft types**: 50 curated historical types seeded via `seed_aircraft_types.py`.
- **FAA staging pipeline**: Automated staging tables and loaders for `MASTER`, `ACFTREF`, and `DEREG` (`faa_staging.py`, `dereg_staging.py`).
- **OpenSky staging pipeline**: Complete staging table and batch loader for global aircraft records (`opensky_staging.py`).
- **Data analysis & notes**: Detailed breakdown of 7 hero types in `docs/DATA_NOTES.md`, including record counts across active and deregistered sets, known quirks, and identifier casing conventions.
- **Type mapping table**: Initial lookup table in `pipeline/mappings/type_map.csv` linking messy raw model strings to canonical aircraft types and variants.

**Next up:**
- Complete mapping coverage for the remaining variants of the hero types.
- Build the transform pipeline (`pipeline/`) to populate `operators`, `airframes`, and `status_events` from the staging tables.
- Implement deduplication and reconciliation logic for airframes appearing across both FAA and OpenSky databases.
- Develop the web UI (`web/`) to allow users to search for an aircraft type and track surviving airframes.
 