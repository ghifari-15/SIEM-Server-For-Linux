from flask import render_template, Blueprint, jsonify, request, Response
from micro_features import format_timestamp, csv_response, build_csv, write_report, build_report_summary
from .analyzer import analyze_event

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

@app_bp.route("/api/events/<int:event_id>/explain", methods=["GET"])
def explain_event_page(event_id):
    result = run_humanize_log(event_id)
    return render_template("event_explanation.html", result=result)


