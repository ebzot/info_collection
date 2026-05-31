# info_collection

ITやゲームに関する情報を自動で収集・要約し、静的HTMLで閲覧できるようにするツールです。

## 概要

このリポジトリは、RSS フィードから IT / ゲーム関連ニュースを定期収集し、要約して SQLite に保存します。
保存したデータから `docs/index.html` と `docs/articles.json` を生成し、GitHub Pages で公開できるようにします。

## 公開ページ

GitHub Pages を有効にしている場合、公開ページは以下です。

- `https://ebzot.github.io/info_collection/`

## 構成

- `config/sources.yaml`: 収集対象の RSS フィード定義
- `collectors/rss.py`: RSS 収集処理
- `processors/summarizer.py`: OpenAI API による要約処理とフォールバック要約
- `processors/render_html.py`: HTML / JSON 出力
- `storage/sqlite_store.py`: SQLite 永続化
- `jobs/run_collection.py`: 収集ジョブ本体
- `.github/workflows/collect.yml`: 定期実行 / 手動実行ワークフロー
- `docs/index.html`: 公開用ページ
- `docs/articles.json`: 公開用データ

## セットアップ

### 1. Python 環境

- Python 3.11 推奨

### 2. 依存関係をインストール

```bash
pip install -r requirements.txt
```

### 3. OpenAI API を使う場合の設定

OpenAI 要約を使う場合は、環境変数 `OPENAI_API_KEY` を設定します。
未設定でもフォールバック要約で動作します。

#### ローカル実行

```bash
export OPENAI_API_KEY=your_api_key
python jobs/run_collection.py
```

#### GitHub Actions

GitHub Actions で OpenAI API を使う場合は、リポジトリの Secrets に次を登録します。

- `OPENAI_API_KEY`

そのうえで `.github/workflows/collect.yml` に次を設定します。

```yaml
jobs:
  collect:
    runs-on: ubuntu-latest
    env:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

OpenAI API を使わない場合は、上記 `env` を設定しなければフォールバック要約だけで動作します。

### 4. 実行結果

実行後、以下が生成・更新されます。

- `data/articles.db`
- `docs/articles.json`
- `docs/index.html`

## GitHub Actions

- 1日1回の定期実行
- `workflow_dispatch` による手動実行
- 収集結果をコミットして Pages 用ファイルを更新

## 現在の動作仕様

### 記事収集

- RSS から記事を取得
- 1フィードあたり最大5件を確認
- RSS 取得はタイムアウト付き
- フィード取得に失敗しても他のソースの処理は継続

### 要約

- 1回の実行で新規記事は最大5件まで処理
- OpenAI 要約は最大1件まで
- 残りはフォールバック要約を使用
- OpenAI API 失敗時は自動でフォールバック要約に切り替え

### 出力

- SQLite に保存
- `docs/articles.json` を更新
- `docs/index.html` を更新

## GitHub Pages 公開手順

1. リポジトリの **Settings** を開く
2. **Pages** を開く
3. **Source** に `Deploy from a branch` を選ぶ
4. **Branch** に `main` を選ぶ
5. **Folder** に `/docs` を選ぶ
6. 保存する

## 今後の拡張候補

- ソース追加
- 重複判定の高度化
- LLM による日次ダイジェスト生成
- ページUI改善
- Discord / Slack 通知
