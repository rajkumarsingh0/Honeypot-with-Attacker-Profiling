import os
import time
import geoip2.database
import geoip2.errors
import mysql.connector
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

GEOIP_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "geoip", "GeoLite2-City.mmdb")

READ_DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}
WRITE_DB_CONFIG = dict(READ_DB_CONFIG)
WRITE_DB_CONFIG["user"] = "cowrie"
WRITE_DB_CONFIG["password"] = os.getenv("DB_WRITE_PASSWORD")

reader = geoip2.database.Reader(GEOIP_DB_PATH)


def lookup_ip(ip):
    try:
        r = reader.city(ip)
        return {
            "country": r.country.name,
            "city": r.city.name,
            "latitude": r.location.latitude,
            "longitude": r.location.longitude,
        }
    except geoip2.errors.AddressNotFoundError:
        # Private/local IPs (127.0.0.1, 192.168.x.x) won't be in the DB - expected during local testing
        return {"country": "Local/Private", "city": None, "latitude": None, "longitude": None}
    except Exception as e:
        return {"country": f"Error: {e}", "city": None, "latitude": None, "longitude": None}


def get_unenriched_sessions(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.id AS session_id, s.ip
        FROM sessions s
        LEFT JOIN geoip_data g ON g.session_id = s.id
        WHERE g.id IS NULL
    """)
    rows = cursor.fetchall()
    cursor.close()
    return rows


def save_geoip(conn, session_id, ip, geo):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO geoip_data (session_id, ip, country, city, latitude, longitude)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (session_id, ip, geo["country"], geo["city"], geo["latitude"], geo["longitude"]))
    conn.commit()
    cursor.close()


def main():
    read_conn = mysql.connector.connect(**READ_DB_CONFIG)
    read_conn.autocommit = True
    write_conn = mysql.connector.connect(**WRITE_DB_CONFIG)

    print("Starting GeoIP enrichment loop... (Ctrl+C to stop)")
    try:
        while True:
            rows = get_unenriched_sessions(read_conn)
            for row in rows:
                geo = lookup_ip(row["ip"])
                save_geoip(write_conn, row["session_id"], row["ip"], geo)
                print(f"[geoip] {row['session_id']} ({row['ip']}) -> {geo['country']}, {geo['city']}")
            time.sleep(10)
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        read_conn.close()
        write_conn.close()
        reader.close()


if __name__ == "__main__":
    main()
