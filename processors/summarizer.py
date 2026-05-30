import json
import os
from typing import Any

from openai import OpenAI

MODEL_NAME = "gpt-4o-mini"

SUMMARY_SCHEMA = {
    "type": "json_schema",
    "name": "article_summary",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "importance": {
                "type": "string",
                "enum": ["low", "medium", "high"],
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
            },
            "category": {
                "type": "string",
                "enum": ["it", "game"],
            },
        },
        "required": ["summary", "importance", "tags", "category"],
        "additionalProperties": False,
    },
}


def fallback_summary(article: dict[str, Any]) -> dict[str, Any]:
    base = article.get("description") or article.get("content") or ""
    text = " ".join(base.split())[:180]
    if text and not text.endswith("。"):
        text += "…"
    return {
        "summary": text or article.get("title", ""),
        "importance": "medium",
        "tags": [article.get("category", "news")],
        "category": article.get("category", "it"),
    }


def summarize_article(article: dict[str, Any]) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return fallback_summary(article)

    client = OpenAI(api_key=api_key)
    content = article.get("content") or article.get("description") or ""
    content = content[:4000]

    prompt = f"""
以下の記事を日本語で要約してください。

要件:
- 2〜3文で簡潔にまとめる
- 誇張表現を避ける
- 不明な情報は推測しない
- IT またはゲームニュースとして重要点を優先する
- 3〜5個の短いタグを付ける
- category は it または game のどちらかを返す

記事カテゴリ: {article.get('category', 'it')}
ソース: {article.get('source', '')}
タイトル: {article.get('title', '')}
本文: {content}
""".strip()

    try:
        response = client.responses.create(
            model=MODEL_NAME,
            input=prompt,
            text={"format": SUMMARY_SCHEMA},
        )
        text = response.output[0].content[0].text
        return json.loads(text)
    except Exception:
        return fallback_summary(article)
