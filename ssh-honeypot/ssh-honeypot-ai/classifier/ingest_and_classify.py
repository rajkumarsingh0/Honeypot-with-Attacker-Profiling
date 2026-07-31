import os
import sys
import time
import mysql.connector
from dotenv import load_dotenv
from pipeline import classify_command

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "file_monitor"))
from persistence_rules import detect_persistence

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# NOTE: DB_USER in .env is cowrie_ro (read-only) -- we need a separate
# write-capable connection just for the classifications table.
WRITE_DB_CONFIG = dict(DB_CONFIG)
WRITE_DB_CONFIG["user"] = "cowrie"
WRITE_DB_CONFIG["password"] = os.getenv("DB_WRITE_PASSWORD")

POLL_INTERVAL = 5  # seconds


def get_unclassified_inputs(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT i.id AS input_id, i.session AS session_id, i.input AS command
        FROM input i
        LEFT JOIN classifications c ON c.input_id = i.id
        WHERE c.id IS NULL
        ORDER BY i.id ASC
    """)
    rows = cursor.fetchall()
    cursor.close()
    return rows


def save_classification(conn, row, result):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO classifications
        (session_id, input_id, command, label, severity, confidence, layer, mitre_id, mitre_name, reasoning)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        row["session_id"], row["input_id"], row["command"],
        result.get("label"), result.get("severity"), result.get("confidence"),
        result.get("layer"), result.get("mitre_id"), result.get("mitre_name"),
        result.get("reasoning"),
    ))
    conn.commit()
    cursor.close()


def save_persistence_event(conn, session_id, persistence_type, detail):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO persistence_events (session_id, event_type, persistence_type, detail)
        VALUES (%s, %s, %s, %s)
    """, (session_id, "command", persistence_type, detail))
    conn.commit()
    cursor.close()


def main():
    read_conn = mysql.connector.connect(**DB_CONFIG)
    read_conn.autocommit = True
    write_conn = mysql.connector.connect(**WRITE_DB_CONFIG)

    print("Starting classification loop... (Ctrl+C to stop)")
    try:
        while True:
            rows = get_unclassified_inputs(read_conn)
            for row in rows:
                result = classify_command(row["command"])
                save_classification(write_conn, row, result)
                print(f"[{result['layer']}] {row['command']} -> {result['label']} ({result.get('mitre_id')})")

                persistence = detect_persistence(row["command"])
                if persistence:
                    save_persistence_event(
                        write_conn, row["session_id"],
                        persistence["persistence_type"], persistence["matched_command"]
                    )
                    print(f"[PERSISTENCE] {row['session_id']} -> {persistence['persistence_type']}")
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        read_conn.close()
        write_conn.close()


if __name__ == "__main__":
    main()
