#!/usr/bin/env python
"""
Example alert script that scans the SQLite database for new articles.
In a production environment this could be extended to send emails or
Slack notifications.
"""

import sqlite3
from pathlib import Path

DB_PATH = "data.db"
STATE_PATH = Path("alert_state.txt")


def get_last_alerted_id() -> int:
    """Read the last alerted article ID from a state file."""
    if STATE_PATH.exists():
        try:
            return int(STATE_PATH.read_text().strip())
        except ValueError:
            return 0
    return 0


def set_last_alerted_id(article_id: int) -> None:
    STATE_PATH.write_text(str(article_id))


def check_for_new_articles():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    last_id = get_last_alerted_id()
    rows = cursor.execute(
        "SELECT id, title FROM articles WHERE id > ? ORDER BY id", (last_id,)
    ).fetchall()
    if rows:
        for row in rows:
            article_id, title = row
            print(f"ALERT: New article ingested: {title} (ID {article_id})")
            set_last_alerted_id(article_id)
    else:
        print("No new articles since last check.")
    conn.close()


if __name__ == "__main__":
    check_for_new_articles()