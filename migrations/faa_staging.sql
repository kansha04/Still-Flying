DROP TABLE IF EXISTS raw_faa_master;
-- Store all data as TEXT to minimize pipeline failures due to unexpected blanks or invalid date formats

CREATE TABLE raw_faa_master (
                                n_number TEXT,
                                serial_number TEXT,
                                mfr_mdl_code TEXT,
                                eng_mfr_mdl TEXT,
                                year_mfr TEXT,
                                type_registrant TEXT,
                                name TEXT,
                                street TEXT,
                                street2 TEXT,
                                city TEXT,
                                state TEXT,
                                zip_code TEXT,
                                region TEXT,
                                county TEXT,
                                country TEXT,
                                last_action_date TEXT,
                                cert_issue_date TEXT,
                                certification TEXT,
                                type_aircraft TEXT,
                                type_engine TEXT,
                                status_code TEXT,
                                mode_s_code TEXT,
                                fract_owner TEXT,
                                air_worth_date TEXT,
                                other_names_1 TEXT,
                                other_names_2 TEXT,
                                other_names_3 TEXT,
                                other_names_4 TEXT,
                                other_names_5 TEXT,
                                expiration_date TEXT,
                                unique_id TEXT,
                                kit_mfr TEXT,
                                kit_model TEXT,
                                mode_s_code_hex TEXT,
                                loaded_at TIMESTAMPTZ DEFAULT NOW()
);

DROP TABLE IF EXISTS raw_faa_acftref;
CREATE TABLE raw_faa_acftref (
                                 code TEXT,
                                 mfr TEXT,
                                 model TEXT,
                                 type_acft TEXT,
                                 type_eng TEXT,
                                 ac_cat TEXT,
                                 build_cert_ind TEXT,
                                 no_eng TEXT,
                                 no_seats TEXT,
                                 ac_weight TEXT,
                                 speed TEXT,
                                 tc_data_sheet TEXT,
                                 tc_data_holder TEXT,
                                 loaded_at TIMESTAMPTZ DEFAULT NOW() -- save as current time
);


SELECT
    m.n_number,
    r.mfr AS manufacturer,
    r.model,
    r.type_acft
FROM raw_faa_master m
         JOIN raw_faa_acftref r
              ON TRIM(m.mfr_mdl_code) = TRIM(r.code);