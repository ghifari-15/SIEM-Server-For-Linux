import os
import sqlite3

from .config import DB_PATH, REPORT_DIR, SQL_PATH


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with open(SQL_PATH, "r") as f:
        sql_script = f.read()

    conn = get_db()
    conn.executescript(sql_script)
    conn.commit()
    conn.close()

    os.makedirs(REPORT_DIR, exist_ok=True)
