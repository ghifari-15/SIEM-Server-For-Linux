import csv
import io
import os
from datetime import datetime, timezone, timedelta

from flask import Blueprint, Response, jsonify, render_template_string, request

from .analyzer import analyze_event
from .config import REPORT_DIR
from .repositories import (
    REQUIRED_EVENT_FIELDS,
    get_alerts,
    get_dashboard_data,
    get_events,
    get_report_summary_data,
    insert_alert,
    insert_event,
)
from .templates import ALERTS_TEMPLATE, DASHBOARD_TEMPLATE, EVENTS_TEMPLATE


main_bp = Blueprint("main", __name__)
WIB = timezone(timedelta(hours=7))


def format_timestamp(value):
    if not value:
        return "-"
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        local_dt = dt.astimezone(WIB)
        return local_dt.strftime("%d-%m-%Y %H:%M:%S")
    except ValueError:
        return value

@main_bp.route("/")
def index():
    return dashboard()


@main_bp.route("/api/events", methods=["POST"])
def receive_event():
    event = request.get_json()

    if not event:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400

    for field in REQUIRED_EVENT_FIELDS:
        if field not in event:
            return jsonify({"status": "error", "message": f"Missing field: {field}"}), 400

    event_id, created = insert_event(event)
    if not created:
        return jsonify({
            "status": "duplicate",
            "message": "Event already exists",
            "event_id": event_id,
            "alerts_generated": 0,
        })

    alerts = analyze_event(event)

    for alert in alerts:
        insert_alert(event_id, alert)

    return jsonify({
        "status": "success",
        "message": "Event received",
        "event_id": event_id,
        "alerts_generated": len(alerts),
    })


@main_bp.route("/dashboard")
def dashboard():
    data = get_dashboard_data()

    formatted_events = []
    for row in data["latest_events"]:
        item = dict(row)
        item["display_timestamp"] = format_timestamp(item["timestamp"])
        formatted_events.append(item)

    data["latest_events"] = formatted_events

    formatted_alerts = []
    for row in data["latest_alerts"]:
        item = dict(row)
        item["display_timestamp"] = format_timestamp(item["timestamp"])
        formatted_alerts.append(item)

    data["latest_alerts"] = formatted_alerts

    return render_template_string(DASHBOARD_TEMPLATE, **data)


@main_bp.route("/events")
def events():
    event_type = request.args.get("event_type", "")
    severity = request.args.get("severity", "")
    hostname = request.args.get("hostname", "")
    rows = get_events(event_type=event_type, severity=severity, hostname=hostname)

    formatted_rows = []
    for row in rows:
        item = dict(row)
        item["display_timestamp"] = format_timestamp(item["timestamp"])
        formatted_rows.append(item)

    return render_template_string(EVENTS_TEMPLATE, rows=formatted_rows, hostname=hostname)


@main_bp.route("/alerts")
def alerts():
    formatted_rows = []
    for row in get_alerts():
        item = dict(row)
        item["display_timestamp"] = format_timestamp(item["timestamp"])
        formatted_rows.append(item)

    return render_template_string(ALERTS_TEMPLATE, rows=formatted_rows)


@main_bp.route("/export/events")
def export_events():
    rows = get_events()
    csv_data = build_csv(
        rows,
        ["id", "timestamp", "hostname", "source", "event_type", "severity", "message", "raw_log"],
    )
    write_report("events.csv", csv_data)
    return csv_response(csv_data, "events.csv")


@main_bp.route("/export/alerts")
def export_alerts():
    rows = get_alerts()
    csv_data = build_csv(
        rows,
        ["id", "event_id", "timestamp", "alert_type", "severity", "description"],
    )
    write_report("alerts.csv", csv_data)
    return csv_response(csv_data, "alerts.csv")


@main_bp.route("/report/summary")
def report_summary():
    data = get_report_summary_data()
    report_text = build_report_summary(data)
    write_report("report_summary.txt", report_text)

    return Response(
        report_text,
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment; filename=report_summary.txt"},
    )


def build_csv(rows, fields):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(fields)

    for row in rows:
        writer.writerow([row[field] for field in fields])

    return output.getvalue()


def csv_response(csv_data, filename):
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def write_report(filename, content):
    with open(os.path.join(REPORT_DIR, filename), "w") as f:
        f.write(content)


def build_report_summary(data):
    lines = [
        "SIEM Report Summary",
        "===================",
        "",
        f"Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Total Events: {data['total_events']}",
        f"Total Alerts: {data['total_alerts']}",
        "",
        "Event Type Summary:",
    ]

    for row in data["event_summary"]:
        lines.append(f"- {row['event_type']}: {row['total']}")

    lines.append("")
    lines.append("Alert Severity Summary:")

    for row in data["severity_summary"]:
        lines.append(f"- {row['severity']}: {row['total']}")

    return "\n".join(lines)
