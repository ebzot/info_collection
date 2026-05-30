import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    category TEXT NOT NULL,
    published_at TEXT,
    fetched_at TEXT NOT NULL,
    description TEXT,
    content TEXT,
    summary TEXT,
    importance TEXT,
    tags_json TEXT,
    summary_model TEXT
);
"""


def ensure_directory(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def connect_db(db_path: str) -> sqlite3.Connection:
    ensure_directory(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute(SCHEMA)
    conn.commit()
    return conn


def article_exists(conn: sqlite3.Connection, url: str) -> bool:
    cur = conn.execute("SELECT 1 FROM articles WHERE url = ? LIMIT 1", (url,))
    return cur.fetchone() is not None


def insert_article(conn: sqlite3.Connection, article: dict[str, Any], summary_data: dict[str, Any], summary_model: str) -> None:
    fetched_at = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """
        INSERT OR IGNORE INTO articles (
            url, title, source, category, published_at, fetched_at,
            description, content, summary, importance, tags_json, summary_model
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            article.get("url"),
            article.get("title"),
            article.get("source"),
            summary_data.get("category") or article.get("category"),
            article.get("published_at"),
            fetched_at,
            article.get("description"),
            article.get("content"),
            summary_data.get("summary"),
            summary_data.get("importance"),
            json.dumps(summary_data.get("tags", []), ensure_ascii=False),
            summary_model,
        ),
    )
    conn.commit()


def export_articles(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    cur = conn.execute(
        """
        SELECT title, url, source, category, published_at, fetched_at, summary, importance, tags_json
        FROM articles
        ORDER BY COALESCE(published_at, fetched_at) DESC
        """
    )

    rows = []
    for row in cur.fetchall():
        rows.append(
            {
                "title": row[0],
                "url": row[1],
                "source": row[2],
                "category": row[3],
                "published_at": row[4],
                "fetched_at": row[5],
                "summary": row[6],
                "importance": row[7],
                "tags": json.loads(row[8] or "[]"),
            }
        )
    return rows
