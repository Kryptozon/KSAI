"""
Knowledge base utilities for KS‑AI backend.

This module provides a simple persistent knowledge base using SQLite. Text
documents uploaded via the API are stored in a `knowledge` table, and
queries against the knowledge base return relevant snippets based on
keyword matches. A helper for emailing PDF reports is also included for
convenience.

Functions:
    init_kb() -> None
        Initialise the SQLite database and create the knowledge table if it
        does not exist.

    add_to_kb(text: str) -> None
        Store raw text into the knowledge base. Each call inserts one row
        containing the entire string provided. If the string is empty the
        function simply returns.

    search_kb(query: str, limit: int = 3) -> str
        Search the knowledge base for entries containing any of the
        whitespace‑separated words in `query`. Returns up to `limit` rows
        concatenated together separated by blank lines. If no matches are
        found, an empty string is returned.

    send_email_report(file_path: str, subject: str = "KS‑AI Crypto Report") -> None
        Send a PDF report as an email attachment using SMTP credentials
        configured at the top of this module. This helper is duplicated in
        `tools.py` but is provided here to maintain compatibility with
        existing imports.
"""

from __future__ import annotations

import os
import sqlite3
import smtplib
import ssl
from typing import List
from email.message import EmailMessage

# ====================================================================
# Configuration for the knowledge base and email helper.
# --------------------------------------------------------------------

# Path to the SQLite database file used for storing knowledge entries.  You
# can change this to any other filename or absolute path as needed.  The
# database will be created automatically if it does not exist.
KB_DB_FILE = os.environ.get("KSAI_KB_DB", "knowledge.db")

# Email settings for sending reports.  These should be customised by the
# deployer.  Using environment variables allows secrets to be injected
# without committing them to version control.
ADMIN_EMAIL = os.environ.get("KSAI_ADMIN_EMAIL", "khaled.d4rensics@gmail.com")
SMTP_SERVER = os.environ.get("KSAI_SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("KSAI_SMTP_PORT", "465"))
SMTP_USER = os.environ.get("KSAI_SMTP_USER", "YOUR_GMAIL_ADDRESS")
SMTP_PASS = os.environ.get("KSAI_SMTP_PASS", "YOUR_APP_PASSWORD")


def init_kb() -> None:
    """Initialise the knowledge base.

    Creates the SQLite database and knowledge table if they do not already
    exist. This function is idempotent and may be called multiple times.
    """
    conn = sqlite3.connect(KB_DB_FILE)
    try:
        c = conn.cursor()
        # Create a simple table to store textual knowledge entries.  The
        # `content` column is lower‑cased when inserting to support
        # case‑insensitive search via `LIKE`. You could extend this table
        # with additional metadata (e.g. filename, tags, timestamps) if
        # needed.
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def add_to_kb(text: str) -> None:
    """Add a new text entry to the knowledge base.

    Args:
        text: Arbitrary text to store. The string will be stored as a
            single row in the `knowledge` table. Empty strings are ignored.
    """
    if not text:
        # Avoid inserting empty rows.
        return
    conn = sqlite3.connect(KB_DB_FILE)
    try:
        c = conn.cursor()
        # Store the content lower‑cased to allow case‑insensitive matches
        # using the `LIKE` operator when searching. If you prefer to
        # preserve case, remove the `.lower()` call and adjust search
        # accordingly.
        c.execute(
            "INSERT INTO knowledge (content) VALUES (?)",
            (text.strip().lower(),),
        )
        conn.commit()
    finally:
        conn.close()


def search_kb(query: str, limit: int = 3) -> str:
    """Search the knowledge base for relevant entries.

    Performs a simple keyword search across the `knowledge` table. Each
    whitespace‑separated token in `query` is used to construct a `LIKE`
    clause. Rows matching any of the tokens are returned up to the
    specified limit. Results are concatenated into a single string,
    separated by blank lines.

    Args:
        query: The search terms. Multiple words will be OR‑combined.
        limit: Maximum number of entries to include in the returned
            context.

    Returns:
        A string containing matching knowledge entries separated by
        blank lines. Returns an empty string if no matches are found or
        if the query is empty.
    """
    if not query:
        return ""
    # Normalise query to lower case for case‑insensitive comparison.
    words: List[str] = [w.strip().lower() for w in query.split() if w.strip()]
    if not words:
        return ""
    conn = sqlite3.connect(KB_DB_FILE)
    try:
        c = conn.cursor()
        # Build a dynamic WHERE clause. Each word generates a LIKE
        # expression. SQLite's OR operator is used to match any word.
        like_clauses = " OR ".join(["content LIKE ?"] * len(words))
        params: List[str] = [f"%{w}%" for w in words]
        # Limit the number of returned rows to avoid flooding the model with
        # too much context. You can adjust the limit via the function
        # parameter.
        c.execute(
            f"SELECT content FROM knowledge WHERE {like_clauses} LIMIT ?",
            (*params, limit),
        )
        rows = c.fetchall()
    finally:
        conn.close()
    # Flatten results and rejoin them. If no rows were found, return
    # an empty string.
    results = [row[0] for row in rows] if rows else []
    return "\n\n".join(results) if results else ""


def send_email_report(file_path: str, subject: str = "KS‑AI Crypto Report") -> None:
    """Send a PDF report as an email attachment.

    Args:
        file_path: Path to the PDF file to attach.
        subject: Optional subject line for the email.

    The SMTP credentials and recipient address are configured via
    module‑level constants. Errors are printed to stderr and do not
    propagate.
    """
    try:
        msg = EmailMessage()
        msg["From"] = SMTP_USER
        msg["To"] = ADMIN_EMAIL
        msg["Subject"] = subject
        msg.set_content(
            "A new crypto analysis report was generated. See attachment."
        )

        with open(file_path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="pdf",
                filename=os.path.basename(file_path),
            )

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print(f"✅ Report emailed silently to {ADMIN_EMAIL}")
    except Exception as e:  # noqa: BLE001
        # Log the exception to console. In a real application you might
        # integrate with a logging framework.
        print("❌ Email sending failed:", e)


# Initialise the knowledge base on module import. This ensures the
# database and table exist before any call to `add_to_kb` or
# `search_kb`.
init_kb()
