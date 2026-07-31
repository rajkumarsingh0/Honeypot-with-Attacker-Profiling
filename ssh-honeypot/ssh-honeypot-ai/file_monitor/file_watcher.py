import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import mysql.connector
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# NOTE: update this path if Cowrie is installed somewhere other than
# /home/cowrie/cowrie on your machine.
DOWNLOADS_PATH = "/home/cowrie/cowrie/var/lib/cowrie/downloads"

WRITE_DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "database": os.getenv("DB_NAME"),
    "user": "cowrie",
    "password": os.getenv("DB_WRITE_PASSWORD"),
}


def log_event(event_type, persistence_type, detail, session_id="unknown"):
    conn = mysql.connector.connect(**WRITE_DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO persistence_events (session_id, event_type, persistence_type, detail)
        VALUES (%s, %s, %s, %s)
    """, (session_id, event_type, persistence_type, detail))
    conn.commit()
    cursor.close()
    conn.close()


class DownloadHandler(FileSystemEventHandler):
    def _handle(self, path):
        try:
            filename = os.path.basename(path)
            print(f"[file_watcher] New file dropped: {filename}", flush=True)
            log_event("file_download", "malware_upload", f"File saved: {filename}")
        except Exception as e:
            print(f"[file_watcher] ERROR in handler: {e}", flush=True)

    def on_moved(self, event):
        # Cowrie writes to a tmp file first, then renames it to its final
        # SHA256-hash filename -- we only want to log the final file.
        if not event.is_directory:
            self._handle(event.dest_path)


def main():
    event_handler = DownloadHandler()
    observer = Observer()
    observer.schedule(event_handler, DOWNLOADS_PATH, recursive=False)
    observer.start()
    print(f"Watching {DOWNLOADS_PATH} for new files... (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
