from openai import OpenAI
from dotenv import load_dotenv

from server.config import LLM_API_KEY, LLM_MODEL, DB_PATH
import sqlite3

load_dotenv()


SCHEMA_CONTEXT = """
Tabel events: id, timestamp, hostname, source, event_type, severity, message, raw_log
Tabel alerts: id, event_id, timestamp, alert_type, severity, description

Nilai event_type yang valid: failed_ssh_login, successful_ssh_login, failed_sudo,
user_created, user_deleted, package_installed, service_started, service_stopped,
file_created, file_modified, file_deleted

Nilai severity yang valid: low, medium, high
"""

def humanize_log(raw_log: str, event_type: str = "", severity: str = "", message: str = "") -> str:
    client = OpenAI(
        api_key=LLM_API_KEY,
        base_url="https://api.deepinfra.com/v1/openai"
        )

    response = client.chat.completions.create(
        model=LLM_MODEL,
        max_tokens=312,
        messages=[{
            "role": "user",
            "content": f"""Kamu adalah asisten keamanan server yang menjelaskan log kepada pengguna awam.

    Berikut adalah data log dari server:
    - Event Type : {event_type}
    - Severity   : {severity}
    - Message    : {message}
    - Raw Log    : {raw_log}

    Jelaskan log ini dalam Bahasa Indonesia yang mudah dipahami oleh orang yang tidak paham teknis.
    Gunakan analogi sehari-hari jika perlu.
    Sampaikan juga apakah ini berbahaya atau tidak, dan apa yang sebaiknya dilakukan admin.  

 
    NOTE: 
    - JANGAN GUNAKAN PENJELASAN DENGAN FORMAT LAIN, JELASKAN DI DALAM 1 PARAGRAF DENGAN SINGKAT, JELAS, DAN PADAT TANPA BERTELE-TELE (Maks 50 kata). 
    - Jangan gunakan Special Character 
    """

    
            }]
        )
    return response.choices[0].message.content

def run_humanize_log(event_id: int) -> dict:
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                e.id,
                e.event_type,
                e.severity,
                e.message,
                e.raw_log,
                a.alert_type,
                a.description AS alert_description
            FROM events e
            LEFT JOIN alerts a ON a.event_id = e.id
            WHERE e.id = ?
        """, (event_id,))

        row = cursor.fetchone()
        if not row:
            return {"error": f"Event dengan ID {event_id} tidak ditemukan."}
        
        explanation = humanize_log(
            raw_log=row["raw_log"] or "",
            event_type=row["event_type"] or "",
            severity=row["severity"] or "",
            message=row["message"] or ""
        )

        return {
            "event_id": row["id"],
            "event_type": row["event_type"],
            "severity": row["severity"],
            "alert_type": row["alert_type"],
            "alert_description": row["alert_description"],
            "explanation": explanation
        }

    except Exception as e:
        return {"error": str(e)}
    finally:
        if "conn" in locals():
            conn.close()


