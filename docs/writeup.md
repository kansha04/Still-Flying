# Still Flying Write Up

Hi there! I will be writing my first code write-up, which will be detailing the journey of this project and the decisions that went into each feature and piece of code.

## Week 1
On **day 1** I did the main project setup, which consisted of setting up the repo, the python environment and all the required libraries along with creating a Postgres database on Supabase (got stopped a little later).

**Day 2** was a day of learning where I read up on some aviation data basics such as ICAO type designators and ICAO24 Hex Addresses; it was actually quite cool to see how planes are identified as it's not as simple as just taking the ICAO type designator as that can cover many variants. For example, a Boeing 737-8 has an ICAO type designator of **B738**; however, both the passenger and freight variants carry this ICAO. Apart from that day 2 also consisted of creating a curated list of 50 different aircraft types in a seeding file.

**Day 3** I started building the first schema, it took a bit of time as I was still learning normalization at school, however, I ended up with four main tables; `aircraft_types` which would be seeded with the 50 types from yesterday's list, `airframes`, `operators` and `status_events` to keep history.
