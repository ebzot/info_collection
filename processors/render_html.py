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
    total_articles = len(articles)
    it_count = sum(1 for article in articles if article.get("category") == "it")
    game_count = sum(1 for article in articles if article.get("category") == "game")

    cards = []
    for article in articles:
        category = escape(article.get("category") or "other")
        source = escape(article.get("source") or "Unknown")
        title = escape(article.get("title") or "No title")
        url = escape(article.get("url") or "#")
        published_at = escape(article.get("published_at") or article.get("fetched_at") or "")
        summary = escape(article.get("summary") or "")
        tags = "".join(f'<span class="tag">{escape(tag)}</span>' for tag in article.get("tags", []))
        category_label = "IT" if category == "it" else "ゲーム" if category == "game" else category

        cards.append(
            f"""
            <article class="card" data-category="{category}">
              <div class="card-header">
                <span class="category-badge category-{category}">{category_label}</span>
                <span class="source-badge">{source}</span>
              </div>
              <h2>{title}</h2>
              <p class="meta">{published_at}</p>
              <p class="summary">{summary}</p>
              <div class="tags">{tags}</div>
              <div class="actions">
                <a class="read-more" href="{url}" target="_blank" rel="noopener noreferrer">原文を開く</a>
              </div>
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
    :root {{
      --bg: #f8fafc;
      --panel: #ffffff;
      --text: #0f172a;
      --muted: #64748b;
      --line: #e2e8f0;
      --primary: #2563eb;
      --primary-soft: #dbeafe;
      --it-bg: #dbeafe;
      --it-text: #1d4ed8;
      --game-bg: #ede9fe;
      --game-text: #7c3aed;
      --shadow: 0 10px 25px rgba(15, 23, 42, 0.08);
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: linear-gradient(180deg, #eff6ff 0%, var(--bg) 180px);
      color: var(--text);
    }}

    header {{
      padding: 40px 20px 28px;
      background: transparent;
    }}

    .hero {{
      max-width: 1100px;
      margin: 0 auto;
      background: rgba(255, 255, 255, 0.82);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.8);
      border-radius: 24px;
      padding: 28px;
      box-shadow: var(--shadow);
    }}

    .hero h1 {{
      margin: 0 0 8px;
      font-size: clamp(1.8rem, 3vw, 2.6rem);
    }}

    .hero p {{
      margin: 0;
      color: var(--muted);
      line-height: 1.6;
    }}

    .stats {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 20px;
    }}

    .stat {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 16px;
    }}

    .stat-label {{
      display: block;
      font-size: 0.9rem;
      color: var(--muted);
      margin-bottom: 6px;
    }}

    .stat-value {{
      font-size: 1.5rem;
      font-weight: 700;
    }}

    main {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 0 20px 40px;
    }}

    .controls {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
      margin-bottom: 20px;
      background: rgba(255, 255, 255, 0.84);
      border: 1px solid rgba(255, 255, 255, 0.8);
      border-radius: 20px;
      padding: 14px;
      box-shadow: var(--shadow);
    }}

    .search {{
      flex: 1 1 240px;
      min-width: 220px;
      padding: 12px 14px;
      border-radius: 12px;
      border: 1px solid var(--line);
      font-size: 0.95rem;
    }}

    .filter-group {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}

    .filter-button {{
      border: 1px solid var(--line);
      background: white;
      color: var(--text);
      border-radius: 999px;
      padding: 10px 14px;
      font-size: 0.92rem;
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .filter-button:hover,
    .filter-button.active {{
      background: var(--primary);
      color: white;
      border-color: var(--primary);
    }}

    .articles-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 18px;
    }}

    .card {{
      display: flex;
      flex-direction: column;
      gap: 12px;
      background: rgba(255, 255, 255, 0.92);
      border: 1px solid rgba(255, 255, 255, 0.9);
      border-radius: 20px;
      padding: 20px;
      box-shadow: var(--shadow);
      min-height: 260px;
    }}

    .card-header {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      align-items: center;
    }}

    .category-badge,
    .source-badge,
    .tag {{
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 0.78rem;
      font-weight: 600;
    }}

    .category-it {{
      background: var(--it-bg);
      color: var(--it-text);
    }}

    .category-game {{
      background: var(--game-bg);
      color: var(--game-text);
    }}

    .source-badge {{
      background: #f1f5f9;
      color: #334155;
    }}

    .card h2 {{
      margin: 0;
      font-size: 1.08rem;
      line-height: 1.5;
    }}

    .meta {{
      margin: 0;
      color: var(--muted);
      font-size: 0.88rem;
    }}

    .summary {{
      margin: 0;
      color: #1e293b;
      line-height: 1.75;
      flex: 1;
    }}

    .tags {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      min-height: 24px;
    }}

    .tag {{
      background: #eef2ff;
      color: #4338ca;
    }}

    .actions {{
      margin-top: auto;
    }}

    .read-more {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 10px 14px;
      border-radius: 12px;
      background: var(--primary);
      color: white;
      text-decoration: none;
      font-weight: 600;
    }}

    .empty {{
      display: none;
      text-align: center;
      color: var(--muted);
      padding: 28px 16px;
    }}

    @media (max-width: 720px) {{
      header {{
        padding: 24px 14px 20px;
      }}

      .hero,
      .controls,
      .card {{
        border-radius: 18px;
      }}

      main {{
        padding: 0 14px 28px;
      }}

      .stats {{
        grid-template-columns: 1fr;
      }}

      .articles-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <div class=\"hero\">
      <h1>info_collection</h1>
      <p>IT / ゲーム関連ニュースを自動収集し、要約して一覧できるダッシュボードです。</p>
      <div class=\"stats\">
        <div class=\"stat\">
          <span class=\"stat-label\">総記事数</span>
          <span class=\"stat-value\">{total_articles}</span>
        </div>
        <div class=\"stat\">
          <span class=\"stat-label\">IT</span>
          <span class=\"stat-value\">{it_count}</span>
        </div>
        <div class=\"stat\">
          <span class=\"stat-label\">ゲーム</span>
          <span class=\"stat-value\">{game_count}</span>
        </div>
      </div>
    </div>
  </header>
  <main>
    <div class=\"controls\">
      <input id=\"search\" class=\"search\" type=\"search\" placeholder=\"タイトル・要約・タグで検索\">
      <div class=\"filter-group\">
        <button class=\"filter-button active\" data-filter=\"all\">すべて</button>
        <button class=\"filter-button\" data-filter=\"it\">IT</button>
        <button class=\"filter-button\" data-filter=\"game\">ゲーム</button>
      </div>
    </div>
    <section id=\"articles\" class=\"articles-grid\">
      {''.join(cards)}
    </section>
    <p id=\"empty\" class=\"empty\">条件に一致する記事がありません。</p>
  </main>
  <script>
    const search = document.getElementById('search');
    const buttons = [...document.querySelectorAll('.filter-button')];
    const cards = [...document.querySelectorAll('.card')];
    const empty = document.getElementById('empty');
    let currentFilter = 'all';

    function update() {{
      const term = search.value.trim().toLowerCase();
      let visibleCount = 0;

      cards.forEach(card => {{
        const category = card.dataset.category;
        const matchesFilter = currentFilter === 'all' || category === currentFilter;
        const text = card.innerText.toLowerCase();
        const matchesSearch = !term || text.includes(term);
        const visible = matchesFilter && matchesSearch;
        card.style.display = visible ? '' : 'none';
        if (visible) visibleCount += 1;
      }});

      empty.style.display = visibleCount === 0 ? 'block' : 'none';
    }}

    search.addEventListener('input', update);
    buttons.forEach(button => button.addEventListener('click', () => {{
      buttons.forEach(item => item.classList.remove('active'));
      button.classList.add('active');
      currentFilter = button.dataset.filter;
      update();
    }}));
  </script>
</body>
</html>
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
