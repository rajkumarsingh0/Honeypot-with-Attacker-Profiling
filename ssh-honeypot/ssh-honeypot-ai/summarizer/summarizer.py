import os
import sys
import time
import json
import mysql.connector
from dotenv import load_dotenv
from google import genai

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "llm_fallback"))

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

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

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """You are a SOC analyst writing a short attacker profile summary based on an SSH honeypot session.
Given the session's commands, classifications, and any persistence events, respond ONLY with valid JSON:
{
  "summary": "<3-4 sentence plain-English summary of what the attacker did and their apparent goal>",
  "skill_level": "low|medium|high",
  "intent": "recon|automated_bot|persistence|data_theft|resource_hijack|unknown",
  "risk_score": <integer 1-10>
}
"""


def get_finished_sessions(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.id AS session_id
        FROM sessions s
        LEFT JOIN session_summaries ss ON ss.session_id = s.id
        WHERE s.endtime IS NOT NULL AND ss.id IS NULL
    """)
    rows = cursor.fetchall()
    cursor.close()
    return rows


def get_session_data(conn, session_id):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT input FROM input WHERE session=%s ORDER BY timestamp ASC", (session_id,))
    commands = [r["input"] for r in cursor.fetchall()]

    cursor.execute("SELECT label, mitre_id, mitre_name FROM classifications WHERE session_id=%s", (session_id,))
    classifications = cursor.fetchall()

    cursor.execute("SELECT persistence_type, detail FROM persistence_events WHERE session_id=%s", (session_id,))
    persistence = cursor.fetchall()

    cursor.close()
    return commands, classifications, persistence


def summarize_session(session_id, commands, classifications, persistence, retries=3):
    context = {
        "session_id": session_id,
        "commands": commands,
        "classifications": classifications,
        "persistence_events": persistence,
    }
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-flash-lite-latest",
                contents=f"{SYSTEM_PROMPT}\n\nSession data:\n{json.dumps(context, default=str)}"
            )
            text = response.text.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            if "429" in str(e) and attempt < retries - 1:
                wait = 15 * (attempt + 1)
                print(f"[summarizer] Rate limited, waiting {wait}s...", flush=True)
                time.sleep(wait)
                continue
            return {"summary": f"Error generating summary: {e}", "skill_level": "unknown", "intent": "unknown", "risk_score": 0}


def save_summary(conn, session_id, result):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO session_summaries (session_id, summary, skill_level, intent, risk_score)
        VALUES (%s, %s, %s, %s, %s)
    """, (session_id, result["summary"], result["skill_level"], result["intent"], result["risk_score"]))
    conn.commit()
    cursor.close()


def main():
    read_conn = mysql.connector.connect(**READ_DB_CONFIG)
    read_conn.autocommit = True
    write_conn = mysql.connector.connect(**WRITE_DB_CONFIG)

    print("Starting session summarizer loop... (Ctrl+C to stop)")
    try:
        while True:
            sessions = get_finished_sessions(read_conn)
            for s in sessions:
                sid = s["session_id"]
                commands, classifications, persistence = get_session_data(read_conn, sid)
                if not commands:
                    continue
                result = summarize_session(sid, commands, classifications, persistence)
                save_summary(write_conn, sid, result)
                print(f"[summarizer] {sid} -> {result['intent']} (risk {result['risk_score']}) - {result['summary'][:60]}...")
                time.sleep(4)  # stay under free-tier rate limits
            time.sleep(10)
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        read_conn.close()
        write_conn.close()


if __name__ == "__main__":
    main()
