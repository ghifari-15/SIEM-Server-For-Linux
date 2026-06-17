import csv
import io
import os
from datetime import datetime

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

    event_id = insert_event(event)
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
    return render_template_string(DASHBOARD_TEMPLATE, **get_dashboard_data())


@main_bp.route("/events")
def events():
    event_type = request.args.get("event_type", "")
    severity = request.args.get("severity", "")
    hostname = request.args.get("hostname", "")
    rows = get_events(event_type=event_type, severity=severity, hostname=hostname)
    return render_template_string(EVENTS_TEMPLATE, rows=rows, hostname=hostname)


@main_bp.route("/alerts")
def alerts():
    return render_template_string(ALERTS_TEMPLATE, rows=get_alerts())


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
