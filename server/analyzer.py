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
}


def analyze_event(event):
    event_type = event.get("event_type", "")
    raw_log = event.get("raw_log", "")

    if event_type == "custom_app_log":
        if "ERROR" in raw_log.upper() or "WARNING" in raw_log.upper():
            return [{
                "alert_type": "Custom Application Error",
                "severity": "medium",
                "description": "Terdeteksi ERROR/WARNING pada custom application log.",
            }]
        return []

    alert = ALERT_RULES.get(event_type)
    return [alert] if alert else []
