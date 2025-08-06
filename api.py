"""
Serverless API for Vercel using FastAPI.

This module exposes two endpoints that read from the SQLite database
created by the ingestion script.  When deployed on Vercel, the
`vercel.json` configuration will route all requests to this file and
use the Python runtime to execute it as a serverless function.

Endpoints:

  GET /            – Return a list of all articles.
  GET /{article_id} – Return a single article by its numeric ID.

The SQLite database path is relative to the project root and
should already exist in the repository (``data.db``).  If the
database doesn't exist or the ``articles`` table is empty, the
endpoints will return empty results.

Note: FastAPI serialises dataclasses/pydantic models to JSON, which
makes it suitable for API responses in a serverless environment.
"""

from __future__ import annotations

import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# Path to the SQLite database.  When running on Vercel the working
# directory is the project root, so ``data.db`` should be located
# alongside this ``server`` directory.
DB_PATH = "data.db"


class Article(BaseModel):
    """Data model for an article record."""

    id: int
    url: str
    title: str
    publication_date: str
    fetched_at: str


def get_db_connection() -> sqlite3.Connection:
    """Open a new SQLite connection and return it."""
    return sqlite3.connect(DB_PATH)


app = FastAPI(title="Structured Notes Research API", version="0.1")


@app.get("/")
def list_articles() -> list[Article]:
    """Return all stored articles ordered by most recently ingested first."""
    conn = get_db_connection()
    cursor = conn.cursor()
    rows = cursor.execute(
        "SELECT id, url, title, publication_date, fetched_at FROM articles ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [Article(id=row[0], url=row[1], title=row[2], publication_date=row[3], fetched_at=row[4]) for row in rows]


@app.get("/{article_id}")
def get_article(article_id: int) -> Article:
    """Return a single article by its numeric ID.

    Raises:
        HTTPException: If no article with the given ID exists.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT id, url, title, publication_date, fetched_at FROM articles WHERE id=?",
        (article_id,),
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Article not found")
    return Article(id=row[0], url=row[1], title=row[2], publication_date=row[3], fetched_at=row[4])