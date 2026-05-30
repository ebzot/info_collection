import json
import os
from html import escape
from typing import Any


def ensure_parent(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def write_json(path: str, articles: list[dict[str, Any]]) -> None:
    ensure_parent(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)


def render_index_html(path: str, articles: list[dict[str, Any]]) -> None:
    ensure_parent(path)
    cards = []
    for article in articles:
        tags = "".join(f'<span class="tag">{escape(tag)}</span>' for tag in article.get("tags", []))
        cards.append(
            f"""
            <article class=\"card\" data-category=\"{escape(article['category'])}\">
              <h2><a href=\"{escape(article['url'])}\" target=\"_blank\" rel=\"noopener noreferrer\">{escape(article['title'])}</a></h2>
              <p class=\"meta\">{escape(article['source'])} / {escape(article.get('published_at') or article.get('fetched_at') or '')}</p>
              <p class=\"summary\">{escape(article.get('summary') or '')}</p>
              <div class=\"tags\">{tags}</div>
            </article>
            """.strip()
        )

    html = f"""<!DOCTYPE html>
<html lang=\"ja\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>info_collection</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; background: #f5f7fb; color: #1a1a1a; }}
    header {{ padding: 24px; background: #111827; color: white; }}
    main {{ max-width: 960px; margin: 0 auto; padding: 24px; }}
    .controls {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; }}
    input, button {{ padding: 10px 12px; border-radius: 8px; border: 1px solid #cbd5e1; }}
    button {{ cursor: pointer; background: white; }}
    .card {{ background: white; border-radius: 12px; padding: 16px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
    .card h2 {{ margin-top: 0; font-size: 1.1rem; }}
    .card a {{ color: #1d4ed8; text-decoration: none; }}
    .meta {{ color: #64748b; font-size: 0.9rem; }}
    .summary {{ line-height: 1.6; }}
    .tags {{ display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px; }}
    .tag {{ background: #e2e8f0; color: #334155; padding: 4px 8px; border-radius: 999px; font-size: 0.8rem; }}
  </style>
</head>
<body>
  <header>
    <h1>info_collection</h1>
    <p>IT / ゲーム関連ニュースの自動収集・要約</p>
  </header>
  <main>
    <div class=\"controls\">
      <input id=\"search\" type=\"search\" placeholder=\"キーワード検索\">
      <button data-filter=\"all\">すべて</button>
      <button data-filter=\"it\">IT</button>
      <button data-filter=\"game\">ゲーム</button>
    </div>
    <section id=\"articles\">
      {''.join(cards)}
    </section>
  </main>
  <script>
    const search = document.getElementById('search');
    const buttons = [...document.querySelectorAll('button[data-filter]')];
    const cards = [...document.querySelectorAll('.card')];
    let currentFilter = 'all';

    function update() {{
      const term = search.value.toLowerCase();
      cards.forEach(card => {{
        const category = card.dataset.category;
        const matchesFilter = currentFilter === 'all' || category === currentFilter;
        const text = card.innerText.toLowerCase();
        const matchesSearch = !term || text.includes(term);
        card.style.display = matchesFilter && matchesSearch ? '' : 'none';
      }});
    }}

    search.addEventListener('input', update);
    buttons.forEach(button => button.addEventListener('click', () => {{
      currentFilter = button.dataset.filter;
      update();
    }}));
  </script>
</body>
</html>
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
