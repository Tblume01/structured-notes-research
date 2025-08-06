#!/usr/bin/env python
"""
Simple FastAPI server that exposes the ingested articles stored in the
SQLite database.  This demonstrates Phase 2 of the roadmap: an API layer.

Run the server with:

    uvicorn api_server:app --reload --port 8000

Then access http://localhost:8000/articles to see the stored articles.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

DB_PATH = "data.db"

app = FastAPI(title="Structured Notes Research API", version="0.1")


class Article(BaseModel):
    id: int
    url: str
    title: str
    publication_date: str
    fetched_at: str


def get_db_connection():
    return sqlite3.connect(DB_PATH)


@app.get("/articles", response_model=list[Article])
def list_articles():
    """Return all stored articles."""
    conn = get_db_connection()
    cursor = conn.cursor()
    rows = cursor.execute(
        "SELECT id, url, title, publication_date, fetched_at FROM articles ORDER BY id DESC"
    ).fetchall()
    conn.close()
    articles = [Article(id=row[0], url=row[1], title=row[2], publication_date=row[3], fetched_at=row[4]) for row in rows]
    return articles


@app.get("/articles/{article_id}", response_model=Article)
def get_article(article_id: int):
    """Return a single article by ID."""
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