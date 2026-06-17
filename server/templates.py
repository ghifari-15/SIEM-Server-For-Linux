DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>SIEM Dashboard</title><style>
body { font-family: Arial, sans-serif; margin: 30px; background: #f4f4f4; }
.nav a { margin-right: 15px; text-decoration: none; color: #0056b3; }
.cards { display: flex; gap: 15px; margin-bottom: 25px; }
.card { background: white; padding: 20px; border-radius: 8px; min-width: 180px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
table { width: 100%; border-collapse: collapse; background: white; margin-bottom: 30px; }
th, td { padding: 10px; border: 1px solid #ccc; font-size: 14px; }
th { background: #222; color: white; }
</style></head>
<body>
<h1>SIEM Dashboard</h1>
<div class="nav">
    <a href="/dashboard">Dashboard</a>
    <a href="/events">Events</a>
    <a href="/alerts">Alerts</a>
    <a href="/export/events">Export Events CSV</a>
    <a href="/export/alerts">Export Alerts CSV</a>
    <a href="/report/summary">Report Summary</a>
</div>
<hr>
<div class="cards">
    <div class="card"><h3>Total Events</h3><h2>{{ total_events }}</h2></div>
    <div class="card"><h3>Total Alerts</h3><h2>{{ total_alerts }}</h2></div>
    <div class="card"><h3>High Alerts</h3><h2>{{ high_alerts }}</h2></div>
    <div class="card"><h3>Medium Alerts</h3><h2>{{ medium_alerts }}</h2></div>
</div>
<h2>Latest Events</h2>
<table>
    <tr><th>ID</th><th>Timestamp</th><th>Hostname</th><th>Source</th><th>Event Type</th><th>Severity</th><th>Message</th></tr>
    {% for e in latest_events %}
    <tr><td>{{ e.id }}</td><td>{{ e.timestamp }}</td><td>{{ e.hostname }}</td><td>{{ e.source }}</td><td>{{ e.event_type }}</td><td>{{ e.severity }}</td><td>{{ e.message }}</td></tr>
    {% endfor %}
</table>
<h2>Latest Alerts</h2>
<table>
    <tr><th>ID</th><th>Event ID</th><th>Timestamp</th><th>Alert Type</th><th>Severity</th><th>Description</th></tr>
    {% for a in latest_alerts %}
    <tr><td>{{ a.id }}</td><td>{{ a.event_id }}</td><td>{{ a.timestamp }}</td><td>{{ a.alert_type }}</td><td>{{ a.severity }}</td><td>{{ a.description }}</td></tr>
    {% endfor %}
</table>
</body>
</html>
"""

EVENTS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>SIEM Events</title><style>
body { font-family: Arial, sans-serif; margin: 30px; background: #f4f4f4; }
.nav a { margin-right: 15px; text-decoration: none; color: #0056b3; }
form { background: white; padding: 15px; margin-bottom: 20px; }
input, select, button { padding: 8px; margin-right: 8px; }
table { width: 100%; border-collapse: collapse; background: white; }
th, td { padding: 10px; border: 1px solid #ccc; font-size: 14px; }
th { background: #222; color: white; }
</style></head>
<body>
<h1>Events</h1>
<div class="nav"><a href="/dashboard">Dashboard</a><a href="/events">Events</a><a href="/alerts">Alerts</a></div>
<hr>
<form method="GET" action="/events">
    <input type="text" name="hostname" placeholder="hostname" value="{{ hostname }}">
    <select name="event_type">
        <option value="">All Event Types</option>
        <option value="failed_ssh_login">failed_ssh_login</option>
        <option value="successful_ssh_login">successful_ssh_login</option>
        <option value="failed_sudo">failed_sudo</option>
        <option value="user_created">user_created</option>
        <option value="user_deleted">user_deleted</option>
        <option value="package_installed">package_installed</option>
        <option value="service_started">service_started</option>
        <option value="service_stopped">service_stopped</option>
        <option value="file_created">file_created</option>
        <option value="file_modified">file_modified</option>
        <option value="file_deleted">file_deleted</option>
        <option value="custom_app_log">custom_app_log</option>
    </select>
    <select name="severity">
        <option value="">All Severity</option>
        <option value="low">low</option>
        <option value="medium">medium</option>
        <option value="high">high</option>
    </select>
    <button type="submit">Filter</button>
    <a href="/events">Reset</a>
</form>
<table>
    <tr><th>ID</th><th>Timestamp</th><th>Hostname</th><th>Source</th><th>Event Type</th><th>Severity</th><th>Message</th><th>Raw Log</th></tr>
    {% for e in rows %}
    <tr><td>{{ e.id }}</td><td>{{ e.timestamp }}</td><td>{{ e.hostname }}</td><td>{{ e.source }}</td><td>{{ e.event_type }}</td><td>{{ e.severity }}</td><td>{{ e.message }}</td><td>{{ e.raw_log }}</td></tr>
    {% endfor %}
</table>
</body>
</html>
"""

ALERTS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>SIEM Alerts</title><style>
body { font-family: Arial, sans-serif; margin: 30px; background: #f4f4f4; }
.nav a { margin-right: 15px; text-decoration: none; color: #0056b3; }
table { width: 100%; border-collapse: collapse; background: white; }
th, td { padding: 10px; border: 1px solid #ccc; font-size: 14px; }
th { background: #222; color: white; }
</style></head>
<body>
<h1>Alerts</h1>
<div class="nav"><a href="/dashboard">Dashboard</a><a href="/events">Events</a><a href="/alerts">Alerts</a></div>
<hr>
<table>
    <tr><th>ID</th><th>Event ID</th><th>Timestamp</th><th>Alert Type</th><th>Severity</th><th>Description</th></tr>
    {% for a in rows %}
    <tr><td>{{ a.id }}</td><td>{{ a.event_id }}</td><td>{{ a.timestamp }}</td><td>{{ a.alert_type }}</td><td>{{ a.severity }}</td><td>{{ a.description }}</td></tr>
    {% endfor %}
</table>
</body>
</html>
"""
