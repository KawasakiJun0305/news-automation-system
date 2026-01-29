# AI News Daily 🗞️

NewsAPI + Claude + GitHub Pages による自動ニュース配信システム

## 🎯 機能

- **NewsAPI** からAI関連ニュースを自動取得
- **Claude (Sonnet 4.5)** で日本語要約を生成
- **新聞風デザイン** のHTMLで配信
- **GitHub Actions** で毎日自動実行
- **GitHub Pages** で公開
- **Notion** データベースに保存（予定）

## 📁 プロジェクト構造

```
news-automation-system/
├── .github/
│   └── workflows/
│       └── news-automation.yml    # GitHub Actions ワークフロー
├── src/
│   ├── data_sources/
│   │   └── newsapi_source.py      # NewsAPI クライアント
│   ├── llm/
│   │   └── claude_client.py       # Claude API クライアント
│   ├── models/
│   │   └── universal_article.py   # 統一データモデル
│   └── outputs/
│       └── html_generator.py      # HTML生成
├── scripts/
│   └── generate_news.py           # ニュース生成スクリプト
├── docs/                          # GitHub Pages 公開フォルダ
│   ├── index.html                 # トップページ
│   └── news_YYYYMMDD.html         # 日別ニュース
├── examples/                      # テストスクリプト
│   ├── integration_test.py
│   └── test_html_generation.py
└── tests/                         # ユニットテスト
```

## 🚀 セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/YOUR_USERNAME/news-automation-system.git
cd news-automation-system
```

### 2. 依存関係をインストール

```bash
pip install -r requirements.txt
```

### 3. 環境変数を設定

`.env` ファイルを作成して、APIキーを設定：

```bash
NEWSAPI_KEY=your_newsapi_key_here
CLAUDE_API_KEY=your_claude_api_key_here
```

### 4. ローカルでテスト

```bash
# 統合テスト
python examples/integration_test.py

# HTML生成テスト
python examples/test_html_generation.py

# ニュース生成（docs/ フォルダに保存）
python scripts/generate_news.py
```

## 🌐 GitHub Pages 公開設定

### 1. リポジトリ設定

1. GitHubリポジトリの **Settings** > **Pages** に移動
2. **Source** を "Deploy from a branch" に設定
3. **Branch** を `main` / `docs` に設定
4. **Save** をクリック

### 2. Secrets 設定

GitHub Actions で使用する環境変数を設定：

1. リポジトリの **Settings** > **Secrets and variables** > **Actions** に移動
2. **New repository secret** をクリック
3. 以下のシークレットを追加：
   - `NEWSAPI_KEY`: NewsAPI のAPIキー
   - `CLAUDE_API_KEY`: Claude のAPIキー

### 3. GitHub Actions 実行

GitHub Actions は以下のタイミングで実行されます：

- **毎日 午前9時（JST）** に自動実行
- **手動実行** も可能（Actions タブから "Run workflow" をクリック）

### 4. サイトURL

GitHub Pages のURLは以下の形式になります：

```
https://YOUR_USERNAME.github.io/news-automation-system/
```

## 📊 データフロー

```
┌─────────────┐
│  NewsAPI    │  記事取得（英語）
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ UniversalArticle    │  統一フォーマットに変換
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Claude Sonnet 4.5  │  日本語要約生成
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  HTML Generator     │  新聞風デザインで生成
└──────┬──────────────┘
       │
       ├─────────────────────────┐
       │                         │
       ▼                         ▼
┌─────────────┐          ┌──────────────┐
│ GitHub Pages│          │    Notion    │
│  (公開サイト) │          │ (データベース) │
└─────────────┘          └──────────────┘
```

## 🎨 デザイン

- **フォント**: Playfair Display（新聞風）
- **レイアウト**: トップニュース + グリッド表示
- **レスポンシブ**: モバイル対応
- **言語**: 英語記事 → 日本語要約

## 🧪 テスト

```bash
# ユニットテスト
pytest tests/

# 統合テスト
python examples/integration_test.py
```

## 📝 ライセンス

MIT License

## 🤝 貢献

プルリクエスト歓迎！

## 📧 お問い合わせ

Issue を作成してください。
