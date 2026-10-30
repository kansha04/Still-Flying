
-- OpenSky
SELECT DISTINCT 'opensky' AS source, 'manufacturername' AS raw_mfr, model AS raw_mdl
FROM raw_opensky_aircraft
WHERE model ILIKE '%727%' OR typecode IN ('B721', 'B722');

-- FAA ACFTREF
SELECT DISTINCT 'faa' AS source, mfr AS raw_mfr, model AS raw_mdl
FROM raw_faa_acftref
WHERE model ILIKE '%727%';