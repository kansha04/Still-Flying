# Hero Types

## 1. McDonnell Douglas DC-10
In `raw_opensky_aircraft` the model is usually noted as `DC-10-XX`, for example, 'DC-10-40' sometimes also followed by an 'F'(freight) or 'I'(intercontinental). `typecode` is generally consistent as 'DC10'.
*Additional Quirk:* The `DC10` typecode in Opensky also heavily features upgraded or military variants like `MD-10-10F`, `MD-10-30F`, and the `KC-10A Extender`. In the FAA databases, there are only ~26 active DC-10 registrations but over 250 deregistered records.
## 2. Boeing 727
In `raw_opensky_aircraft` the model is usually noted as `727-2XX`, where XX is a customer code suffix added by Boeing. For example, '727-225' is a 727-200 made for Eastern Airlines. Customer code is generally followed by a feature modifier such as 'RE'(re-engined) or 'W'(winglets). `typecode` also consistent as 'B722'. Missing quite a few `built` values.
## 3. Airbus A310
Manufacturer ICAO is mostly consistent. In `raw_opensky_aircraft` the model is usually noted as `A210-XXX`. For example, 'A310-304'. Sometimes there is an 'Airbus' prefix included and a feature modifier suffix including 'MRTT', '24, 04', 'ET' or 'F'. Missing quite a few `registered` values. `typecode` is generally consistent. 
## 4. Vickers VC10
Only 4 found in the `raw_opensky_aircraft` dataset. Manufacturer ICAO is not listed in any database, only reference to mfr (manufacturer) is the name; `Vickers-armstrongs (actf) Ltd`. In `raw_opensky_aircraft` the model is usually noted as `VC10 K3` with only one exception being `VC10 TYPE 1151`. Registration is filled along with its `reg_until` (ex. `2029-01-31`) field which also appears in the `raw_faa_master` as `expiration_date` (ex. `20290131`)table however I think I prefer. Serial numbers also match across tables.
## 5. Mikoyan Gurevich MIG-21
Around 29 examples found in `raw_opensky_aircraft`. Mfr ICAO is consistent (`MIKOYAN`) as well as mfr name. The `model` has a few variants which are identified using feature identifiers like the other planes mentioned above. Examples include, `MIG-21 UM`, `MIG-21R` or `MiG-21 MF-75`. `registration` or in the `raw_faa_master` table's `n_number` is also very consistent adn matches. 



## 6. Lockheed L-1011 TriStar
Very sparse in the active databases. In `raw_opensky_aircraft`, there are only about 11 records mentioning L-1011 or TriStar (and only 7 under the `L101` typecode, with 100% of them missing the `built` field). The model formatting is usually `L-1011-XXX` (e.g., `L-1011-385-1`). In `raw_faa_master` there are only 4 active registrations, but significantly more (187) appear in the `raw_faa_dereg` deregistered table.

## 7. Boeing 747-200
In `raw_opensky_aircraft`, the 747-200 follows the same naming convention as the 727, using a Boeing customer code suffix as `747-2XX` (e.g., `747-251F`, `747-230F`, `747-281B`). Opensky models sometimes use a space instead of a hyphen (`747 251B`). The typecode is typically `B742`, which also notably covers military variants like the `E-4B` and `VC-25A` (Air Force One) and 16 records have a completely blank model string. In the FAA `raw_faa_master` table, there are only 5 active registrations, compared to 226 in `raw_faa_dereg`. 

## General Data Quirks & Missing Fields
*   **Missing Built/Registration Dates (Opensky):** Missing data is a significant issue in Opensky. For example, across all records, `built` is blank in ~73% of rows, `registered` is blank in ~90%, and `reg_until` is blank in ~51%.
*   **Missing Year of Mfr (FAA):** While much more complete, the FAA `raw_faa_master` table still has the `year_mfr` missing or blank in about 22% of its records.

> [!note] ICAO24 Hex Addresses
> In the `raw_opensky_aircraft` database these are found under the `icao24` columns and are always in lowercase (ex. a0bef1) however in the FAA databases these are found under the column `mode_s_code_hex` and are all in uppercase (ex. A0BEF1). This is likely a source-format convention. When doing PostgresQL JOINs will be best to standardize lowercase.
