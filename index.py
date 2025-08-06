"""
Serverless FastAPI app for Vercel.

This module exposes a FastAPI application that lists articles stored
in a SQLite database and returns individual articles by ID. When
deployed on Vercel, it can handle all incoming requests routed to
``/api`` or the site root depending on the configuration in
``vercel.json``.

Endpoints:

  GET /          – Return a list of all articles.
  GET /{id}      – Return a single article by numeric ID.

The SQLite database (``data.db``) should be located in the root
directory of the repository. If it is absent or the ``articles``
table is empty, the API will return empty results gracefully.

This file lives in the ``api`` directory because Vercel’s Python
runtime automatically treats every file in ``api`` as a serverless
function, exposing it under the path ``/api``. We also provide
rewrite rules in ``vercel.json`` to route all paths (including ``/``)
to this module so the API can serve the entire domain.
"""

from __future__ import annotations

import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DB_PATH = "data.db"


class Article(BaseModel):
    """Data model representing an article record."""

    id: int
    url: str
    title: str
    publication_date: str
    fetched_at: str


def get_db_connection() -> sqlite3.Connection:
    """Open a new SQLite connection and return it."""
    return sqlite3.connect(DB_PATH)


app = FastAPI(title="Structured Notes Research API", version="0.2")


@app.get("/")
def list_articles() -> list[Article]:
    """Return all stored articles, newest first."""
    conn = get_db_connection()
    cursor = conn.cursor()
    rows = cursor.execute(
        "SELECT id, url, title, publication_date, fetched_at "
        "FROM articles ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [Article(id=row[0], url=row[1], title=row[2], publication_date=row[3], fetched_at=row[4]) for row in rows]


@app.get("/{article_id}")
def get_article(article_id: int) -> Article:
    """Return a single article by its numeric ID or raise 404."""
    conn = get_db_connection()
    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT id, url, title, publication_date, fetched_at "
        "FROM articles WHERE id=?",
        (article_id,),
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Article not found")
    return Article(id=row[0], url=row[1], title=row[2], publication_date=row[3], fetched_at=row[4])