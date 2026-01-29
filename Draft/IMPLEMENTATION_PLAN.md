# Implementation Plan - 実装ロードマップ

## 📋 概要

このドキュメントは、**ステップ 1 から 6** までの実装計画を詳しく説明します。

各ステップは **2-5 日で完了** できるように設計されています。

---

## 🏗️ 全体フロー図

```
【ステップ 1】
環境構築 + NewsAPI 連携
  目標：NewsAPI から記事が取得できる
  期間：2-3 日
  成果物：記事 JSON が表示される
  
          ↓
          
【ステップ 2】
Claude API で要約生成
  目標：要約文が日本語で生成される
  期間：2 日
  成果物：複数記事の要約が生成できる
  
          ↓
          
【ステップ 3】
HTML 生成 + ローカルテスト
  目標：HTML がブラウザで表示される
  期間：2-3 日
  成果物：新聞風デザイン HTML が生成される
  
          ↓
          
【ステップ 4】
Notion + Markdown 出力
  目標：Notion に自動投稿、Markdown 保存
  期間：2-3 日
  成果物：複数出力形式に対応
  
          ↓
          
【ステップ 5】
スコアリング・フィルタリング・詳細ロジック
  目標：「本当に大事なニュース」だけが表示
  期間：3-5 日
  成果物：複雑なロジック実装完了
  
          ↓
          
【ステップ 6】
GitHub Actions 設定 + 本番環境デプロイ
  目標：毎朝 6 時に自動実行、iPad で閲覧可能
  期間：2-3 日
  成果物：完全自動化システム完成
```

---

## ✅ ステップ 1：環境構築 + NewsAPI 連携

### 目標
```
✅ Python 環境が整備される
✅ 必要なライブラリがインストールされる
✅ NewsAPI から記事が取得できる
✅ 取得した記事がターミナルに表示される
```

### 実装内容

#### 1-1. Windows に Python をインストール
詳細は **SETUP_WINDOWS.md** を参照してください。

確認コマンド：
```bash
python --version
# 出力例：Python 3.11.0

pip --version
# 出力例：pip 23.0.1
```

#### 1-2. プロジェクトフォルダ作成

```bash
# フォルダ作成
mkdir news-automation-system
cd news-automation-system

# Git 初期化
git init

# 仮想環境作成
python -m venv venv

# 仮想環境有効化（Windows）
venv\Scripts\activate

# 確認（プロンプトに (venv) が表示される）
```

#### 1-3. 依存ライブラリのインストール

```bash
# requirements.txt を作成
pip install requests
pip install python-dotenv
pip install pytest

# インストール確認
pip list
```

#### 1-4. NewsAPI キーの取得

- https://newsapi.org に登録
- API キー を取得
- `.env` ファイルに保存

```bash
# .env ファイル作成
NEWSAPI_KEY=your_api_key_here
```

#### 1-5. NewsAPI データ取得コード実装

```python
# src/data_sources/newsapi_source.py

import requests
import os
from datetime import datetime

class NewsAPISource:
    """
    NewsAPI からニュース記事を取得するクラス
    """
    
    def __init__(self):
        self.api_key = os.getenv('NEWSAPI_KEY')
        self.base_url = 'https://newsapi.org/v2/everything'
    
    def fetch_articles(self, keyword: str, language: str = 'ja') -> list:
        """
        キーワードでニュース記事を検索
        
        パラメータ：
            keyword (str): 検索キーワード（例："AI"）
            language (str): 言語（デフォルト：日本語）
        
        戻り値：
            list: 記事のリスト
        """
        
        params = {
            'q': keyword,
            'language': language,
            'sortBy': 'publishedAt',
            'apiKey': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # HTTP エラーがあれば例外を発生
            
            data = response.json()
            articles = data.get('articles', [])
            
            print(f"✅ {keyword} : {len(articles)} 件取得")
            return articles
        
        except requests.exceptions.RequestException as e:
            print(f"❌ エラーが発生しました：{e}")
            return []
```

#### 1-6. テスト実装

```python
# tests/test_newsapi_source.py

import pytest
from src.data_sources.newsapi_source import NewsAPISource

def test_newsapi_fetch():
    """
    NewsAPI からデータが取得できるか確認
    """
    source = NewsAPISource()
    articles = source.fetch_articles('AI')
    
    # 記事が取得されているか
    assert len(articles) > 0
    
    # 記事に必要なフィールドがあるか
    assert 'title' in articles[0]
    assert 'url' in articles[0]
    assert 'publishedAt' in articles[0]
```

### テスト実行

```bash
# テスト実行
pytest tests/test_newsapi_source.py -v

# 出力例：
# test_newsapi_fetch PASSED [100%]
# ========== 1 passed in 1.23s ==========
```

### 成果物

```
news-automation-system/
├── src/
│   └── data_sources/
│       └── newsapi_source.py
├── tests/
│   └── test_newsapi_source.py
├── requirements.txt
├── .env
└── venv/
```

### ✅ チェックリスト

- [ ] Python がインストールされた
- [ ] プロジェクトフォルダが作成された
- [ ] 仮想環境が有効化されている
- [ ] 依存ライブラリがインストールされた
- [ ] NewsAPI キーが取得できた
- [ ] NewsAPI から記事が取得できる
- [ ] テストが成功した

---

## ✅ ステップ 2：Claude API で要約生成

### 目標
```
✅ Claude API が呼び出せる
✅ ニュース記事を日本語で要約できる
✅ 複数記事を効率的に処理できる
```

### 実装内容

#### 2-1. Claude API キーの取得

- Claude.ai にログイン
- Settings → API Keys で新しいキーを生成
- `.env` に追加

```bash
CLAUDE_API_KEY=sk-ant-...
```

#### 2-2. Claude クライアント実装

```python
# src/llm/claude_client.py

import anthropic
import os

class ClaudeClient:
    """
    Claude API を使って要約生成するクラス
    """
    
    def __init__(self):
        self.api_key = os.getenv('CLAUDE_API_KEY')
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    async def summarize(self, text: str, max_tokens: int = 200) -> str:
        """
        テキストを要約する
        
        パラメータ：
            text (str): 要約する元テキスト
            max_tokens (int): 最大トークン数
        
        戻り値：
            str: 生成された要約
        """
        
        prompt = f"""
次のニュース記事を、簡潔な日本語で2-3文の要約にしてください。

記事：
{text}

要約：
"""
        
        try:
            message = self.client.messages.create(
                model="claude-opus-4-5-20251101",
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            summary = message.content[0].text
            return summary.strip()
        
        except Exception as e:
            print(f"❌ Claude API エラー：{e}")
            return ""
```

#### 2-3. テスト実装

```python
# tests/test_claude_client.py

import pytest
from src.llm.claude_client import ClaudeClient

@pytest.mark.asyncio
async def test_claude_summarize():
    """
    Claude が要約を生成できるか確認
    """
    client = ClaudeClient()
    
    text = """
    OpenAI は本日、次世代言語モデル「GPT-5」をプレビュー公開しました。
    従来の GPT-4 比で推論精度が 35% 向上し、複雑な数学問題やコード生成でも高い精度を実現しています。
    3 月の正式リリースが予定されています。
    """
    
    summary = await client.summarize(text)
    
    # 要約が生成されているか
    assert len(summary) > 0
    
    # 日本語が含まれているか
    assert any('\u3000' <= c <= '\u9fff' for c in summary)
```

### ステップ 2 の成果物

```
news-automation-system/
├── src/
│   ├── llm/
│   │   └── claude_client.py
│   └── data_sources/
│       └── newsapi_source.py
├── tests/
│   ├── test_claude_client.py
│   └── test_newsapi_source.py
└── requirements.txt（anthropic を追加）
```

### ✅ チェックリスト

- [ ] Claude API キーが取得できた
- [ ] Claude クライアント実装した
- [ ] 要約生成テストが成功した
- [ ] 複数記事の要約が生成できる

---

## ✅ ステップ 3：HTML 生成 + ローカルテスト

### 目標
```
✅ 新聞風デザイン HTML が生成される
✅ ブラウザで表示できる
✅ ローカルテストが可能
```

### 実装内容

#### 3-1. HTML 生成クラス実装

```python
# src/outputs/html_generator.py

class HTMLGenerator:
    """
    UniversalArticle を HTML に変換するクラス
    """
    
    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>Jun's News Digest - {date}</title>
        <!-- スタイルシート（PROJECT_OVERVIEW.md の HTML サンプルを参照） -->
        <style>
        ...
        </style>
    </head>
    <body>
        ...
    </body>
    </html>
    """
    
    @staticmethod
    def generate(articles: list, date: str) -> str:
        """
        記事リストを HTML に変換
        
        パラメータ：
            articles (list): UniversalArticle のリスト
            date (str): 日付（例："2026-01-29"）
        
        戻り値：
            str: 生成された HTML
        """
        # HTML テンプレートに記事を埋め込む
        # （詳細は実装時に）
        pass
```

#### 3-2. テスト実装

```python
# tests/test_html_generator.py

def test_html_generation():
    """
    HTML が正しく生成されるか確認
    """
    articles = [
        UniversalArticle(
            id="test1",
            title="Test Article",
            source_url="https://example.com",
            source_name="Example",
            published_at=datetime.now(),
            fetched_at=datetime.now()
        )
    ]
    
    html = HTMLGenerator.generate(articles, "2026-01-29")
    
    # HTML が生成されている
    assert len(html) > 100
    
    # 必要な要素が含まれている
    assert "<html" in html
    assert "Test Article" in html
```

### ✅ チェックリスト

- [ ] HTML 生成クラスを実装した
- [ ] テストが成功した
- [ ] ブラウザで表示できる

---

## ✅ ステップ 4：Notion + Markdown 出力

### 目標
```
✅ Notion に自動投稿できる
✅ Markdown ファイルが生成される
✅ 複数出力形式に対応
```

### 実装内容

#### 4-1. Notion API 設定

詳細は **NOTION_SETUP.md**（別途作成）を参照。

#### 4-2. Markdown 生成

```python
# src/outputs/markdown_generator.py

class MarkdownGenerator:
    """
    UniversalArticle を Markdown に変換
    """
    
    @staticmethod
    def generate(articles: list, date: str) -> str:
        """
        記事を Markdown に変換
        """
        markdown = f"# ニュースダイジェスト {date}\n\n"
        
        for article in articles:
            markdown += f"## {article.title}\n"
            markdown += f"- **要約**：{article.summary}\n"
            markdown += f"- **ソース**：[{article.source_name}]({article.source_url})\n"
            markdown += f"- **スコア**：{article.relevance_score}\n\n"
        
        return markdown
```

### ✅ チェックリスト

- [ ] Notion API キーが取得できた
- [ ] Notion に投稿できる
- [ ] Markdown ファイルが生成される

---

## ✅ ステップ 5：スコアリング・フィルタリング

### 目標
```
✅ 記事を重要度でスコアリング
✅ 低品質記事を除外
✅ 重複検出
✅ ランキング表示
```

### 実装内容

詳細は **LOGIC_DETAILED.md** を参照。

---

## ✅ ステップ 6：GitHub Actions + 本番環境

### 目標
```
✅ 毎朝 6 時に自動実行
✅ GitHub Pages で配置
✅ iPad で閲覧可能
```

### 実装内容

詳細は **GITHUB_ACTIONS_SETUP.md** を参照。

---

## 📚 全体テスト戦略

| ステップ | テスト対象 | テスト方法 |
|--------|----------|----------|
| 1 | NewsAPI 連携 | `pytest tests/test_newsapi_source.py` |
| 2 | Claude API | `pytest tests/test_claude_client.py` |
| 3 | HTML 生成 | `pytest tests/test_html_generator.py` |
| 4 | 出力機能 | `pytest tests/test_outputs.py` |
| 5 | スコアリング | `pytest tests/test_scorer.py` |
| 全体 | 統合テスト | `pytest tests/test_integration.py` |

---

## 🎯 実装時のベストプラクティス

### **エラーハンドリング**
```python
try:
    result = do_something()
except SomeException as e:
    print(f"❌ エラー：{e}")
    # ログに記録、または別の処理へ
```

### **ロギング**
```python
import logging

logger = logging.getLogger(__name__)

logger.info("✅ 処理が完了しました")
logger.warning("⚠️ 警告：...")
logger.error("❌ エラーが発生しました")
```

### **テストの実行**
```bash
# 全テスト実行
pytest tests/ -v

# 特定のテスト実行
pytest tests/test_newsapi_source.py -v

# カバレッジ確認
pytest tests/ --cov=src
```

---

**次は SETUP_WINDOWS.md を読んでください！**
