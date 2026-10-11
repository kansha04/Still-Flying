import csv
import psycopg2
from psycopg2.extras import execute_values
from config import get_config
from connect import connect

def create_staging_tables(conn, schema_file='migrations/opensky_staging.sql'):
    """Ensures raw staging tables exist before loading."""
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    with conn.cursor() as cur:
        cur.execute(schema_sql)
    conn.commit()
    print("✓ Staging tables initialized successfully.")

def load_opensky_aircraft(conn, file_path='aircraft-database-complete-2025-08.csv', batch_size=5000):
    """
    Streams and bulk loads OpenSky aircraft database CSV into raw_opensky_aircraft.
    """
    query = """
        INSERT INTO raw_opensky_aircraft (
            icao24, timestamp, acars, adsb, built,
            category_description, country, engines, first_flight_date, first_seen,
            icao_aircraft_class, line_number, manufacturer_icao, manufacturer_name, model,
            modes, next_reg, notes, operator, operator_callsign,
            operator_iata, operator_icao, owner, prev_reg, reg_until,
            registered, registration, sel_cal, serial_number, status,
            typecode, vdl
        ) VALUES %s
    """
    print(f"Loading {file_path} into raw_opensky_aircraft...")
    with open(file_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=',', quotechar="'")
        next(reader)  # Skip CSV header

        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE raw_opensky_aircraft;")
            batch = []
            total_loaded = 0

            for row in reader:
                if not row or len(row) < 32:
                    continue
                # Extract the 32 defined columns and strip surrounding whitespace
                cleaned_row = [field.strip() for field in row[:32]]
                batch.append(cleaned_row)

                if len(batch) >= batch_size:
                    execute_values(cur, query, batch)
                    total_loaded += len(batch)
                    batch.clear()

            if batch:
                execute_values(cur, query, batch)
                total_loaded += len(batch)

    print(f"✓ Completed raw_opensky_aircraft ({total_loaded:,} rows).")


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
        load_opensky_aircraft(conn, file_path='aircraft-database-complete-2025-08.csv')

        conn.commit()
        print("Successfully staged OpenSky data.")
    except Exception as e:
        conn.rollback()
        print(f"Error occurred during staging. Rolling back transaction: {e}")
    finally:
        conn.close()


if __name__ == '__main__':
    main()
