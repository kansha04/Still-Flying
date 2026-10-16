-- Reference query: join current FAA registrations to their make/model record.
-- Not part of any migration; run manually after faa_staging.py has loaded the raw tables.

SELECT
    m.n_number,
    r.mfr AS manufacturer,
    r.model,
    r.type_acft
FROM raw_faa_master m
         JOIN raw_faa_acftref r
              ON TRIM(m.mfr_mdl_code) = TRIM(r.code);
