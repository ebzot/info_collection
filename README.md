# info_collection

ITやゲームに関する情報を自動で収集・要約し、静的HTMLで閲覧できるようにするツールです。

## 概要

このリポジトリは、RSS フィードから IT / ゲーム関連ニュースを定期収集し、OpenAI API で要約したうえで SQLite に保存します。
保存したデータから `docs/index.html` と `docs/articles.json` を生成し、あとから一覧で確認できるようにします。

## 構成

- `config/sources.yaml`: 収集対象の RSS フィード定義
- `collectors/rss.py`: RSS 収集処理
- `processors/summarizer.py`: OpenAI API による要約処理
- `processors/render_html.py`: HTML / JSON 出力
- `storage/sqlite_store.py`: SQLite 永続化
- `jobs/run_collection.py`: 収集ジョブ本体
- `.github/workflows/collect.yml`: 定期実行 / 手動実行ワークフロー

## セットアップ

### 1. Python 環境

- Python 3.11 推奨

### 2. 依存関係をインストール

```bash
pip install -r requirements.txt
```

### 3. GitHub Secrets を設定

GitHub Actions で OpenAI API を使うため、リポジトリの Secrets に次を登録します。

- `OPENAI_API_KEY`

### 4. ローカル実行

```bash
export OPENAI_API_KEY=your_api_key
python jobs/run_collection.py
```

実行後、以下が生成されます。

- `data/articles.db`
- `docs/articles.json`
- `docs/index.html`

## GitHub Actions

- 1日1回の定期実行
- `workflow_dispatch` による手動実行

## 要約仕様

- OpenAI Responses API を利用
- 日本語で 2〜3 文の簡潔な要約を生成
- `summary`, `importance`, `tags`, `category` を構造化出力
- API 失敗時は description / 本文先頭を使った簡易要約にフォールバック

## 現在の前提

- 収集元は RSS 中心
- 保存先は SQLite
- 表示は静的 HTML
- 公開用データは JSON も生成

## 今後の拡張候補

- ソース追加
- 重複判定の高度化
- LLM による日次ダイジェスト生成
- GitHub Pages 公開
- Discord / Slack 通知
