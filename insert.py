import psycopg2
from config import get_config

def insert_aircraft_type(manufacturer, model, variant, icao_type_code, conn=None):
    """Insert a new aircraft type into the database"""
    sql = """INSERT INTO aircraft_types (manufacturer, model, variant, icao_type_code) 
             VALUES (%s, %s, %s, %s)
             ON CONFLICT (manufacturer, model) DO NOTHING"""

    # If a connection isn't provided, create a new one for this single operation
    if conn is None:
        config = get_config()
        try:
            with psycopg2.connect(**config) as new_conn:
                with new_conn.cursor() as cur:
                    cur.execute(sql, (manufacturer, model, variant, icao_type_code))
                    new_conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
    else:
        # Use the provided connection and cursor
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (manufacturer, model, variant, icao_type_code))
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)


