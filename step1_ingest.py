#!/usr/bin/env python
"""
Minimal example of a data ingestion script for structured note research.

This script fetches a sample article from CAIS and parses basic metadata
such as the article title and publication date.  It stores the results
in a local SQLite database.  In a production system you would extend
this script to loop over multiple sources, parse more detailed
information (e.g., coupon rates, product types), and run on a schedule.
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime

ARTICLE_URL = "https://www.caisgroup.com/articles/what-are-contingent-yield-notes"
DB_PATH = "data.db"


def fetch_article(url: str) -> tuple[str, str]:
    """Fetch an HTML page and return its title and publication date.

    Args:
        url: URL of the article to fetch.

    Returns:
        A tuple of (title, publication_date_str). If the date cannot be
        found, the current date is used instead.
    """
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract the page's title
    title_tag = soup.find("title")
    title = title_tag.text.strip() if title_tag else url

    # Attempt to find a publication date. CAIS articles often have a
    # date inside a tag with the attribute data-base-heading="Article".
    date_str = None
    for meta in soup.find_all("time"):
        # Many articles use a <time datetime="YYYY-MM-DD"> element
        datetime_attr = meta.get("datetime")
        if datetime_attr and len(datetime_attr) >= 10:
            date_str = datetime_attr[:10]
            break

    # Fallback to current date if not found
    if not date_str:
        date_str = datetime.utcnow().strftime("%Y-%m-%d")

    return title, date_str


def init_db(db_path: str) -> sqlite3.Connection:
    """Initialize the SQLite database and return a connection."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            title TEXT,
            publication_date TEXT,
            fetched_at TEXT
        )
        """
    )
    conn.commit()
    return conn


def save_article(conn: sqlite3.Connection, url: str, title: str, pub_date: str) -> None:
    """Insert or update an article record in the database."""
    cursor = conn.cursor()
    fetched_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        """
        INSERT INTO articles (url, title, publication_date, fetched_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(url) DO UPDATE SET
            title=excluded.title,
            publication_date=excluded.publication_date,
            fetched_at=excluded.fetched_at
        """,
        (url, title, pub_date, fetched_at),
    )
    conn.commit()


def main() -> None:
    conn = init_db(DB_PATH)
    title, pub_date = fetch_article(ARTICLE_URL)
    save_article(conn, ARTICLE_URL, title, pub_date)
    print(f"Fetched '{title}' published {pub_date} and stored in database.")


if __name__ == "__main__":
    main()