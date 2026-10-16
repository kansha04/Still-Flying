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

## Where things stand
**Built so far:**
- Core schema: `aircraft_types`, `operators`, `airframes`, `status_events`
- 50 curated aircraft types, seeded into `aircraft_types`
- Staging tables and loaders for FAA `MASTER`, `ACFTREF` and `DEREG`, and the OpenSky aircraft database

**Next up:**
- The transform step (`pipeline/`): match the staged records to my aircraft types, then fill `operators`, `airframes` and `status_events`
- Deciding how to handle aircraft that appear in both the FAA and OpenSky data
- A website (`web/`) where people can search a type and see which airframes still exist

