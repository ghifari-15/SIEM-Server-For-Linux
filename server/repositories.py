from datetime import datetime

from .database import get_db


REQUIRED_EVENT_FIELDS = [
    "timestamp",
    "hostname",
    "source",
    "event_type",
    "severity",
    "message",
    "raw_log",
]


def insert_event(event):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO events (
            timestamp, hostname, source, event_type, severity, message, raw_log
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        event.get("timestamp"),
        event.get("hostname"),
        event.get("source"),
        event.get("event_type"),
        event.get("severity"),
        event.get("message"),
        event.get("raw_log"),
    ))

    event_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return event_id


def insert_alert(event_id, alert):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO alerts (
            event_id, timestamp, alert_type, severity, description
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        event_id,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        alert["alert_type"],
        alert["severity"],
        alert["description"],
    ))

    conn.commit()
    conn.close()


def get_dashboard_data():
    conn = get_db()
    data = {
        "total_events": conn.execute("SELECT COUNT(*) AS total FROM events").fetchone()["total"],
        "total_alerts": conn.execute("SELECT COUNT(*) AS total FROM alerts").fetchone()["total"],
        "high_alerts": conn.execute("SELECT COUNT(*) AS total FROM alerts WHERE LOWER(TRIM(severity)) = 'high'").fetchone()["total"],
        "medium_alerts": conn.execute("SELECT COUNT(*) AS total FROM alerts WHERE LOWER(TRIM(severity)) = 'medium'").fetchone()["total"],
        "latest_events": conn.execute("SELECT * FROM events ORDER BY id DESC LIMIT 10").fetchall(),
        "latest_alerts": conn.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT 10").fetchall(),
    }
    conn.close()
    return data


def get_events(event_type="", severity="", hostname=""):
    query = "SELECT * FROM events WHERE 1=1"
    params = []

    if event_type:
        query += " AND event_type = ?"
        params.append(event_type)

    if severity:
        query += " AND severity = ?"
        params.append(severity)

    if hostname:
        query += " AND hostname LIKE ?"
        params.append(f"%{hostname}%")

    query += " ORDER BY id DESC"

    conn = get_db()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def get_alerts():
    conn = get_db()
    rows = conn.execute("SELECT * FROM alerts ORDER BY id DESC").fetchall()
    conn.close()
    return rows


def get_report_summary_data():
    conn = get_db()
    data = {
        "total_events": conn.execute("SELECT COUNT(*) AS total FROM events").fetchone()["total"],
        "total_alerts": conn.execute("SELECT COUNT(*) AS total FROM alerts").fetchone()["total"],
        "event_summary": conn.execute("""
            SELECT event_type, COUNT(*) AS total
            FROM events
            GROUP BY event_type
            ORDER BY total DESC
        """).fetchall(),
        "severity_summary": conn.execute("""
            SELECT LOWER(TRIM(severity)) AS severity, COUNT(*) AS total
            FROM alerts
            GROUP BY LOWER(TRIM(severity))
            ORDER BY total DESC
        """).fetchall(),
    }
    conn.close()
    return data
