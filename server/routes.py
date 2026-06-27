import csv
import io
import os
from datetime import datetime, timezone, timedelta

from flask import Blueprint, Response, jsonify, render_template, request

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
from .options import ALERT_TYPE_OPTIONS, EVENT_TYPE_OPTIONS, SEVERITY_OPTIONS
from .humanize_query import run_humanize_log


app_bp = Blueprint("main", __name__)
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

@app_bp.route("/")
def index():
    return dashboard()


@app_bp.route("/api/events", methods=["POST"])
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


@app_bp.route("/dashboard")
def dashboard():
    event_type = request.args.get("event_type", "")
    severity = request.args.get("severity", "")
    hostname = request.args.get("hostname", "")
    data = get_dashboard_data(event_type=event_type, severity=severity, hostname=hostname)

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

    return render_template(
        "dashboard.html",
        **data,
        event_type=event_type,
        severity=severity,
        hostname=hostname,
        event_type_options=EVENT_TYPE_OPTIONS,
        severity_options=SEVERITY_OPTIONS,
    )


@app_bp.route("/events")
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

    return render_template(
        "events.html",
        rows=formatted_rows,
        event_type=event_type,
        severity=severity,
        hostname=hostname,
        event_type_options=EVENT_TYPE_OPTIONS,
        severity_options=SEVERITY_OPTIONS,
    )


@app_bp.route("/alerts")
def alerts():
    alert_type = request.args.get("alert_type", "")
    severity = request.args.get("severity", "")
    hostname = request.args.get("hostname", "")
    formatted_rows = []
    for row in get_alerts(alert_type=alert_type, severity=severity, hostname=hostname):
        item = dict(row)
        item["display_timestamp"] = format_timestamp(item["timestamp"])
        formatted_rows.append(item)

    return render_template(
        "alerts.html",
        rows=formatted_rows,
        alert_type=alert_type,
        severity=severity,
        hostname=hostname,
        alert_type_options=ALERT_TYPE_OPTIONS,
        severity_options=SEVERITY_OPTIONS,
    )


@app_bp.route("/export/events")
def export_events():
    rows = get_events()
    csv_data = build_csv(
        rows,
        ["id", "timestamp", "hostname", "source", "event_type", "severity", "message", "raw_log"],
    )
    write_report("events.csv", csv_data)
    return csv_response(csv_data, "events.csv")


@app_bp.route("/export/alerts")
def export_alerts():
    rows = get_alerts()
    csv_data = build_csv(
        rows,
        ["id", "event_id", "timestamp", "alert_type", "severity", "description"],
    )
    write_report("alerts.csv", csv_data)
    return csv_response(csv_data, "alerts.csv")


@app_bp.route("/report/summary")
def report_summary():
    data = get_report_summary_data()
    report_text = build_report_summary(data)
    write_report("report_summary.txt", report_text)

    return Response(
        report_text,
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment; filename=report_summary.txt"},
    )


@app_bp.route("/api/<int:event_id>/explain", methods=["GET"])
def explain_event(event_id):
    result = run_humanize_log(event_id)
    return jsonify(result)


@app_bp.route("/events/<int:event_id>/explain", methods=["GET"])
def explain_event_page(event_id):
    result = run_humanize_log(event_id)
    return render_template("event_explanation.html", result=result)

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
    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(os.path.join(REPORT_DIR, filename), "w", encoding="utf-8", newline="") as f:
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
