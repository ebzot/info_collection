import feedparser
from bs4 import BeautifulSoup


def html_to_text(value: str) -> str:
    if not value:
        return ""
    soup = BeautifulSoup(value, "html.parser")
    return soup.get_text(" ", strip=True)


def collect_feed(source: dict) -> list[dict]:
    parsed = feedparser.parse(source["url"])
    articles = []

    for entry in parsed.entries:
        summary = html_to_text(getattr(entry, "summary", ""))
        content = ""
        if getattr(entry, "content", None):
            content = html_to_text(entry.content[0].value)

        article = {
            "source": source["name"],
            "category": source["category"],
            "title": getattr(entry, "title", "").strip(),
            "url": getattr(entry, "link", "").strip(),
            "published_at": getattr(entry, "published", ""),
            "description": summary,
            "content": content,
        }

        if article["title"] and article["url"]:
            articles.append(article)

    return articles
