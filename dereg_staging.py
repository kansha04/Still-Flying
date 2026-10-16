import csv
import psycopg2
from psycopg2.extras import execute_values
from config import get_config
from connect import connect

def create_staging_tables(conn, schema_file='migrations/dereg_staging.sql'):
    """Ensures raw staging tables exist before loading."""
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    with conn.cursor() as cur:
        cur.execute(schema_sql)
    conn.commit()
    print("✓ Staging tables initialized successfully.")

def load_dereg(conn, file_path='FAA_data/DEREG.txt', batch_size=5000):
    """
    Streams and bulk loads DEREG.txt into raw_faa_dereg.
    """
    query = """
        INSERT INTO raw_faa_dereg (
            n_number, serial_number, mfr_mdl_code, status_code, name,
            street_mail, street2_mail, city_mail, state_abbrev_mail, zip_code_mail,
            eng_mfr_mdl, year_mfr, certification, region, county_mail,
            country_mail, air_worth_date, cancel_date, mode_s_code, indicator_group,
            exp_country, last_act_date, cert_issue_date, street_physical, street2_physical,
            city_physical, state_abbrev_physical, zip_code_physical, county_physical, country_physical,
            other_names_1, other_names_2, other_names_3, other_names_4, other_names_5,
            kit_mfr, kit_model, mode_s_code_hex
        ) VALUES %s
    """
    print(f"Loading {file_path} into raw_faa_dereg...")
    with open(file_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader)  # Skip CSV header

        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE raw_faa_dereg;")
            batch = []
            total_loaded = 0

            for row in reader:
                if not row or len(row) < 38:
                    continue
                # Extract the 38 defined columns and strip surrounding whitespace
                cleaned_row = [field.strip() for field in row[:38]]
                batch.append(cleaned_row)

                if len(batch) >= batch_size:
                    execute_values(cur, query, batch)
                    total_loaded += len(batch)
                    batch.clear()

            if batch:
                execute_values(cur, query, batch)
                total_loaded += len(batch)

    print(f"✓ Completed raw_faa_dereg ({total_loaded:,} rows).")


def main():
    config = get_config()
    conn = connect(config)

    if not conn:
        print("Database connection failed. Aborting staging process.")
        return

    try:
        # 1. Initialize / create staging tables if needed
        create_staging_tables(conn)

        # 2. Ingest data
        load_dereg(conn, file_path='FAA_data/DEREG.txt')

        conn.commit()
        print("Successfully staged FAA DEREG data.")
    except Exception as e:
        conn.rollback()
        print(f"Error occurred during staging. Rolling back transaction: {e}")
    finally:
        conn.close()


if __name__ == '__main__':
    main()
