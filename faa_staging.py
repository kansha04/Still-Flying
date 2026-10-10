import csv
import psycopg2
from psycopg2.extras import execute_values
from config import get_config
from connect import connect

def create_staging_tables(conn, schema_file='migrations/faa_staging.sql'):
    """Ensures raw staging tables exist before loading."""
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    with conn.cursor() as cur:
        cur.execute(schema_sql)
    conn.commit()
    print("✓ Staging tables initialized successfully.")

def load_acftref(conn, file_path='FAA_data/ACFTREF.txt', batch_size=5000):
    """
    Streams and bulk loads ACFTREF.txt into raw_faa_acftref.
    """
    query = """
        INSERT INTO raw_faa_acftref (
            code, mfr, model, type_acft, type_eng, ac_cat,
            build_cert_ind, no_eng, no_seats, ac_weight, speed,
            tc_data_sheet, tc_data_holder
        ) VALUES %s
    """
    print(f"Loading {file_path} into raw_faa_acftref...")
    with open(file_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader)  # Skip CSV header

        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE raw_faa_acftref;")
            batch = []
            total_loaded = 0

            for row in reader:
                if not row or len(row) < 13:
                    continue
                # Extract the 13 defined columns and strip surrounding whitespace
                cleaned_row = [field.strip() for field in row[:13]]
                batch.append(cleaned_row)

                if len(batch) >= batch_size:
                    execute_values(cur, query, batch)
                    total_loaded += len(batch)
                    batch.clear()

            if batch:
                execute_values(cur, query, batch)
                total_loaded += len(batch)

    print(f"✓ Completed raw_faa_acftref ({total_loaded:,} rows).")


def load_master(conn, file_path='FAA_data/MASTER.txt', batch_size=5000):
    """
    Streams and bulk loads MASTER.txt into raw_faa_master.
    """
    query = """
        INSERT INTO raw_faa_master (
            n_number, serial_number, mfr_mdl_code, eng_mfr_mdl, year_mfr,
            type_registrant, name, street, street2, city, state, zip_code,
            region, county, country, last_action_date, cert_issue_date,
            certification, type_aircraft, type_engine, status_code, mode_s_code,
            fract_owner, air_worth_date, other_names_1, other_names_2,
            other_names_3, other_names_4, other_names_5, expiration_date,
            unique_id, kit_mfr, kit_model, mode_s_code_hex
        ) VALUES %s
    """
    print(f"Loading {file_path} into raw_faa_master...")
    with open(file_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader)  # Skip CSV header

        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE raw_faa_master;")
            batch = []
            total_loaded = 0

            for row in reader:
                if not row or len(row) < 34:
                    continue
                # Extract the 34 defined columns and strip surrounding whitespace
                cleaned_row = [field.strip() for field in row[:34]]
                batch.append(cleaned_row)

                if len(batch) >= batch_size:
                    execute_values(cur, query, batch)
                    total_loaded += len(batch)
                    batch.clear()

            if batch:
                execute_values(cur, query, batch)
                total_loaded += len(batch)

    print(f"✓ Completed raw_faa_master ({total_loaded:,} rows).")


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
        load_acftref(conn, file_path='FAA_data/ACFTREF.txt')
        load_master(conn, file_path='FAA_data/MASTER.txt')

        conn.commit()
        print("Successfully staged all FAA data.")
    except Exception as e:
        conn.rollback()
        print(f"Error occurred during staging. Rolling back transaction: {e}")
    finally:
        conn.close()


if __name__ == '__main__':
    main()