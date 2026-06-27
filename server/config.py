import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "siem.db")
SQL_PATH = os.path.join(BASE_DIR, "database.sql")
REPORT_DIR = os.path.join(BASE_DIR, "reports")
HOST = os.getenv("SIEM_HOST", "0.0.0.0")
PORT = int(os.getenv("SIEM_PORT", "5000"))
DEBUG = os.getenv("SIEM_DEBUG", "1") == "1"


LLM_API_KEY=os.environ.get("LLM_API_KEY", "")
LLM_MODEL="XiaomiMiMo/MiMo-V2.5"
