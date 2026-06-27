from flask import Response
from datetime import datetime, timezone, timedelta
from config import REPORT_DIR
import os
import csv
import io
import os

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
    

def build_csv(rows, fields):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(fields)

    for row in rows:
        values = []
        for field in fields:
            values.append(row[field])
        writer.writerow(values)

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
