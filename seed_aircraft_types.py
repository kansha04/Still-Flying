import csv
from pprint import pprint
import psycopg2
from config import get_config
from insert import insert_aircraft_type

from connect import connect

config = get_config()
conn = connect(config)

if conn:
    try:
        with open('aircraft_types.csv', newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=";")
            for row in reader:
                insert_aircraft_type(
                    row["Manufacturer"], 
                    row["Aircraft Type"], 
                    row["Variants"], 
                    row["ICAO"], 
                    conn=conn
                )
        # Commit all changes at once
        conn.commit()
        print("Successfully seeded aircraft types.")
    except Exception as e:
        # If anything goes wrong, roll back any partial changes
        conn.rollback()
        print(f"Error during seeding: {e}")
    finally:
        conn.close()

