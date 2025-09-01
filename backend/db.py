import sqlite3, os
from datetime import datetime

DB_FILE = "ksai.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS crypto_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        query TEXT,
        pdf_path TEXT,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def log_report(session_id, query, pdf_path):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO crypto_reports (session_id, query, pdf_path, created_at) VALUES (?, ?, ?, ?)",
              (session_id, query, pdf_path, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_all_reports():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, session_id, query, pdf_path, created_at FROM crypto_reports ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows

# initialize DB at import
init_db()
