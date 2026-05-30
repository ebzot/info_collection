import os
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from collectors.rss import collect_feed
from processors.render_html import render_index_html, write_json
from processors.summarizer import MODEL_NAME, summarize_article
from storage.sqlite_store import article_exists, connect_db, export_articles, insert_article

DB_PATH = str(ROOT / "data" / "articles.db")
JSON_PATH = str(ROOT / "docs" / "articles.json")
HTML_PATH = str(ROOT / "docs" / "index.html")
SOURCES_PATH = ROOT / "config" / "sources.yaml"


def load_sources() -> list[dict]:
    with open(SOURCES_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config.get("sources", [])


def main() -> None:
    conn = connect_db(DB_PATH)
    new_count = 0

    for source in load_sources():
        for article in collect_feed(source):
            if article_exists(conn, article["url"]):
                continue
            summary_data = summarize_article(article)
            insert_article(conn, article, summary_data, MODEL_NAME)
            new_count += 1

    articles = export_articles(conn)
    write_json(JSON_PATH, articles)
    render_index_html(HTML_PATH, articles)
    print(f"completed: {new_count} new articles, {len(articles)} total articles")


if __name__ == "__main__":
    main()
