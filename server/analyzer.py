ALERT_RULES = {
    "failed_ssh_login": {
        "alert_type": "Failed SSH Login",
        "severity": "medium",
        "description": "Terdeteksi percobaan login SSH yang gagal.",
    },
    "successful_ssh_login": {
        "alert_type": "Successful SSH Login",
        "severity": "low",
        "description": "Terdeteksi login SSH yang berhasil.",
    },
    "failed_sudo": {
        "alert_type": "Failed Sudo Attempt",
        "severity": "high",
        "description": "Terdeteksi percobaan sudo yang gagal.",
    },
    "user_created": {
        "alert_type": "User Account Created",
        "severity": "medium",
        "description": "Terdeteksi pembuatan akun user baru.",
    },
    "user_deleted": {
        "alert_type": "User Account Deleted",
        "severity": "medium",
        "description": "Terdeteksi penghapusan akun user.",
    },
    "package_installed": {
        "alert_type": "Package Installed",
        "severity": "low",
        "description": "Terdeteksi instalasi package pada endpoint.",
    },
    "service_started": {
        "alert_type": "Service Started",
        "severity": "low",
        "description": "Terdeteksi service berjalan.",
    },
    "service_stopped": {
        "alert_type": "Service Stopped",
        "severity": "high",
        "description": "Terdeteksi service berhenti.",
    },
    "file_created": {
        "alert_type": "File Created",
        "severity": "low",
        "description": "Terdeteksi pembuatan file.",
    },
    "file_modified": {
        "alert_type": "File Modified",
        "severity": "medium",
        "description": "Terdeteksi perubahan file.",
    },
    "file_deleted": {
        "alert_type": "File Deleted",
        "severity": "medium",
        "description": "Terdeteksi penghapusan file.",
    },
    "service_or_custom_log": {
        "alert_type": "Service and Custom Log",
        "severity": "medium",
        "description": "",
    },
}


def analyze_event(event):
    event_type = event.get("event_type", "").strip().lower()
    severity = event.get("severity", "").strip().lower()
    message = event.get("message", "").strip()
    raw_log = event.get("raw_log", "")

    if event_type == "service_or_custom_log":
        combined_log = f"{message} {raw_log}".upper()
        if ("SERVICE" in combined_log or "SYSTEMD" in combined_log) and ("STOP" in combined_log or "STOPPED" in combined_log or "FAILED" in combined_log):
            return [{
                "alert_type": "Service Stopped",
                "severity": severity if severity in ("low", "medium", "high") else "high",
                "description": message or "Terdeteksi service berhenti atau gagal.",
            }]
        if ("SERVICE" in combined_log or "SYSTEMD" in combined_log) and ("START" in combined_log or "STARTED" in combined_log):
            return [{
                "alert_type": "Service Started",
                "severity": severity if severity in ("low", "medium", "high") else "low",
                "description": message or "Terdeteksi service berjalan.",
            }]
        if "ERROR" in combined_log or "WARNING" in combined_log or "FAILED" in combined_log:
            return [{
                "alert_type": "Custom Application Error",
                "severity": severity if severity in ("low", "medium", "high") else "medium",
                "description": "Terdeteksi ERROR/WARNING pada custom application log.",
            }]
        return []

    alert = ALERT_RULES.get(event_type)
    if alert:
        return [alert]

    if severity in ("medium", "high"):
        return [{
            "alert_type": "Security Event",
            "severity": severity,
            "description": message or f"Terdeteksi event dengan severity {severity}.",
        }]

    return []
