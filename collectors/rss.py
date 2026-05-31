import requests
import feedparser
from bs4 import BeautifulSoup

MAX_ITEMS_PER_FEED = 5
REQUEST_TIMEOUT_SECONDS = 15
USER_AGENT = "info-collection-bot/1.0"


def html_to_text(value: str) -> str:
    if not value:
        return ""
    soup = BeautifulSoup(value, "html.parser")
    return soup.get_text(" ", strip=True)


def collect_feed(source: dict) -> list[dict]:
    articles = []

    try:
        print(f"fetching feed: {source['url']}")
        response = requests.get(
            source["url"],
            timeout=REQUEST_TIMEOUT_SECONDS,
            headers={"User-Agent": USER_AGENT},
        )
        response.raise_for_status()
        parsed = feedparser.parse(response.content)
    except Exception as exc:
        print(f"failed to fetch feed {source['name']}: {exc}")
        return articles

    for entry in parsed.entries[:MAX_ITEMS_PER_FEED]:
        try:
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
        except Exception as exc:
            print(f"failed to parse entry from {source['name']}: {exc}")

    print(f"collected {len(articles)} articles from {source['name']}")
    return articles
