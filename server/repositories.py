from datetime import datetime, timezone

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

    existing = cursor.execute("""
        SELECT id
        FROM events
        WHERE timestamp = ?
          AND hostname = ?
          AND source = ?
          AND event_type = ?
          AND message = ?
          AND COALESCE(raw_log, '') = COALESCE(?, '')
        LIMIT 1
    """, (
        event.get("timestamp"),
        event.get("hostname"),
        event.get("source"),
        event.get("event_type"),
        event.get("message"),
        event.get("raw_log"),
    )).fetchone()

    if existing:
        conn.close()
        return existing["id"], False

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
    return event_id, True


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
        datetime.now(timezone.utc).isoformat(),
        alert["alert_type"],
        alert["severity"],
        alert["description"],
    ))

    conn.commit()
    conn.close()


def get_dashboard_data(event_type="", severity="", hostname=""):
    conn = get_db()
    event_query = "SELECT * FROM events WHERE 1=1"
    event_params = []

    if event_type:
        event_query += " AND event_type = ?"
        event_params.append(event_type)

    if severity:
        event_query += " AND LOWER(TRIM(severity)) = ?"
        event_params.append(severity.strip().lower())

    if hostname:
        event_query += " AND hostname LIKE ?"
        event_params.append(f"%{hostname}%")

    filtered_event_ids_query = event_query.replace("SELECT *", "SELECT id")
    alert_filter = f"event_id IN ({filtered_event_ids_query})"
    data = {
        "total_events": conn.execute(event_query.replace("SELECT *", "SELECT COUNT(*) AS total"), event_params).fetchone()["total"],
        "total_alerts": conn.execute(f"SELECT COUNT(*) AS total FROM alerts WHERE {alert_filter}", event_params).fetchone()["total"],
        "high_alerts": conn.execute(f"SELECT COUNT(*) AS total FROM alerts WHERE LOWER(TRIM(severity)) = 'high' AND {alert_filter}", event_params).fetchone()["total"],
        "medium_alerts": conn.execute(f"SELECT COUNT(*) AS total FROM alerts WHERE LOWER(TRIM(severity)) = 'medium' AND {alert_filter}", event_params).fetchone()["total"],
        "latest_events": conn.execute(event_query + " ORDER BY id DESC LIMIT 10", event_params).fetchall(),
        "latest_alerts": conn.execute(f"SELECT * FROM alerts WHERE {alert_filter} ORDER BY id DESC LIMIT 10", event_params).fetchall(),
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
        query += " AND LOWER(TRIM(severity)) = ?"
        params.append(severity.strip().lower())

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
