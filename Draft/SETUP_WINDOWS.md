# Setup Guide for Windows - Windows セットアップガイド

## 🎯 このガイドの目的

Windows PC に Python 環境を整備し、プロジェクトを動かせるようにします。

**所要時間**：30-60 分

---

## ✅ ステップ 1：Python のインストール

### 1-1. Python ダウンロード

1. https://www.python.org/downloads/ にアクセス
2. 「Download Python 3.11」（または 3.12）をクリック
3. インストーラーを実行

### 1-2. インストーラー実行時の設定

⚠️ **重要**：以下のチェックボックスに必ず✅を入れてください

```
☑ Add Python 3.11 to PATH  ← 最重要！
☑ Install for all users
```

その他の設定はデフォルトで OK。

### 1-3. インストール確認

**ターミナル（コマンドプロンプト）を開く**

```bash
# Windows キー + R → "cmd" 入力 → Enter
```

**Python のバージョン確認**

```bash
python --version
# 出力例：Python 3.11.7

pip --version
# 出力例：pip 23.3.1 from ... (python 3.11)
```

もし「python コマンドが見つからない」エラーが出た場合：
- Python をアンインストール
- 再度インストール時に「Add Python 3.11 to PATH」に✅

---

## ✅ ステップ 2：プロジェクトフォルダ の作成

### 2-1. フォルダ作成

```bash
# デスクトップに作成する例
cd Desktop

# プロジェクトフォルダ作成
mkdir news-automation-system
cd news-automation-system
```

### 2-2. フォルダ構造確認

```bash
# 現在位置確認
cd  # 出力例：C:\Users\YourName\Desktop\news-automation-system
```

---

## ✅ ステップ 3：仮想環境（venv）の作成

### 3-1. 仮想環境の作成

```bash
# venv フォルダが作成される
python -m venv venv
```

**なぜ仮想環境？**
- プロジェクトごとにライブラリを分離
- PC 全体に影響しない
- 開発環境を汚さない

### 3-2. 仮想環境の有効化（Windows）

```bash
# Windows コマンドプロンプトの場合
venv\Scripts\activate

# PowerShell の場合
venv\Scripts\Activate.ps1
```

**確認**：プロンプトが以下のように変わる

```
(venv) C:\Users\YourName\Desktop\news-automation-system>
        ↑
    "(venv)" が付いている = 有効化されている
```

### 3-3. 仮想環境の無効化（後で必要になったら）

```bash
deactivate
```

---

## ✅ ステップ 4：依存ライブラリのインストール

### 4-1. requirements.txt を作成

プロジェクトフォルダに `requirements.txt` を作成（テキストエディタで）

```txt
# requirements.txt

# HTTP リクエスト（API 呼び出し用）
requests==2.31.0

# 環境変数読み込み（API キー管理用）
python-dotenv==1.0.0

# Claude API クライアント
anthropic==0.25.0

# OpenAI API クライアント（オプション）
openai==1.3.0

# Google Gemini API（オプション）
google-generativeai==0.3.0

# Notion API クライアント
notion-client==2.2.1

# テスト用
pytest==7.4.0
pytest-asyncio==0.23.0

# RSS パース用
feedparser==6.0.10

# ロギング・デバッグ用
colorama==0.4.6
```

### 4-2. ライブラリのインストール

```bash
# 仮想環境が有効化されていることを確認
# プロンプトに (venv) が表示されているか？

# requirements.txt からインストール
pip install -r requirements.txt
```

**出力例**：
```
Collecting requests==2.31.0
  Using cached requests-2.31.0-py3-none-any.whl
Installing collected packages: ...
Successfully installed ...
```

### 4-3. インストール確認

```bash
pip list

# 出力例：
# Package          Version
# ...................... ........
# anthropic        0.25.0
# requests         2.31.0
# python-dotenv    1.0.0
# ...
```

---

## ✅ ステップ 5：API キーの取得と設定

### 5-1. NewsAPI キー

1. https://newsapi.org に登録（メールアドレス + パスワード）
2. ログイン → Account
3. API Key をコピー

### 5-2. Claude API キー

1. https://console.anthropic.com にログイン
2. API Keys → Create Key
3. コピー

### 5-3. Notion Integration Token（後で設定）

1. https://www.notion.so/my-integrations にアクセス
2. Create new integration
3. Token をコピー

### 5-4. .env ファイルを作成

プロジェクトフォルダのルートに `.env` ファイルを作成

```bash
# .env

# API キー設定
NEWSAPI_KEY=your_newsapi_key_here
CLAUDE_API_KEY=sk-ant-your_claude_key_here
OPENAI_API_KEY=sk-your_openai_key_here（オプション）
GEMINI_API_KEY=your_gemini_key_here（オプション）

# Notion 設定（後で）
NOTION_DATABASE_ID=your_notion_db_id
NOTION_API_TOKEN=ntn_your_token_here

# 実行環境
ENVIRONMENT=development  # or production
```

**⚠️ 重要**：
- `.env` を Git にコミットしない（.gitignore に追加）
- API キーを人に見せない

### 5-5. .gitignore の作成

```bash
# .gitignore

.env
venv/
__pycache__/
*.pyc
.pytest_cache/
.DS_Store
```

---

## ✅ ステップ 6：フォルダ構造の作成

### 6-1. 以下の構造を手動で作成

```bash
news-automation-system/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── data_sources/
│   │   ├── __init__.py
│   │   └── newsapi_source.py
│   ├── llm/
│   │   ├── __init__.py
│   │   └── claude_client.py
│   ├── outputs/
│   │   ├── __init__.py
│   │   ├── html_generator.py
│   │   └── markdown_generator.py
│   └── utils/
│       ├── __init__.py
│       └── logger.py
│
├── tests/
│   ├── __init__.py
│   ├── test_newsapi_source.py
│   └── fixtures/
│       └── sample_data.json
│
├── docs/
│   ├── PROJECT_OVERVIEW.md
│   ├── DATA_MODEL.md
│   └── ... その他ドキュメント
│
├── news/
│   └── （出力ディレクトリ）
│
├── .env
├── .gitignore
├── requirements.txt
├── config.example.py
└── README.md
```

フォルダ作成コマンド：

```bash
# Windows の場合
mkdir src
mkdir src\data_sources
mkdir src\llm
mkdir src\outputs
mkdir src\utils
mkdir tests
mkdir tests\fixtures
mkdir docs
mkdir news

# Linux/Mac の場合（参考）
mkdir -p src/{data_sources,llm,outputs,utils}
mkdir -p tests/fixtures
mkdir docs
mkdir news
```

ファイル作成：

```bash
# __init__.py は空で OK
type nul > src\__init__.py
type nul > src\data_sources\__init__.py
type nul > src\llm\__init__.py
type nul > src\outputs\__init__.py
type nul > src\utils\__init__.py
type nul > tests\__init__.py
```

---

## ✅ ステップ 7：初期テストの実行

### 7-1. config.py の作成（テンプレート）

```python
# config.py

import os
from dotenv import load_dotenv

# .env ファイルを読み込む
load_dotenv()

# API キー
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')

# Notion
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN')

# 環境
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# ログ設定
LOG_LEVEL = 'INFO' if ENVIRONMENT == 'production' else 'DEBUG'

# ニュースキーワード
KEYWORDS = ['AI', '決算', '科学', 'モノづくり', 'ボードゲーム']
```

### 7-2. main.py の作成（スケルトン）

```python
# src/main.py

import sys
sys.path.insert(0, '.')

from config import NEWSAPI_KEY, CLAUDE_API_KEY
from src.data_sources.newsapi_source import NewsAPISource

async def main():
    """
    メイン処理
    """
    print("🚀 News Automation System を開始します")
    
    # NewsAPI から記事取得
    source = NewsAPISource()
    articles = source.fetch_articles('AI')
    
    print(f"✅ {len(articles)} 件の記事を取得しました")

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
```

### 7-3. テスト実行

```bash
# 仮想環境が有効か確認
# (venv) が付いているか？

# Python が動くか確認
python --version

# 簡単なテスト実行
python -c "print('✅ Python が動いています')"

# main.py を実行
python src/main.py
```

期待される出力：
```
🚀 News Automation System を開始します
✅ 20 件の記事を取得しました
```

---

## 🔧 トラブルシューティング

### Q. Python コマンドが見つからない

```bash
# Windows で python コマンドが認識されない場合
python --version
# 出力：'python' は認識されていません

# 解決法：
# 1. Python をアンインストール
# 2. 再インストール時に「Add Python 3.11 to PATH」に✅
# 3. ターミナルを再起動
```

### Q. venv が有効化されない

```bash
# エラー：文字列は予期された式です
venv\Scripts\activate

# 解決法：PowerShell の場合
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\Activate.ps1
```

### Q. pip install でエラー

```bash
# エラー：Could not find a version that satisfies the requirement

# 解決法：pip をアップデート
python -m pip install --upgrade pip
```

### Q. .env ファイルが読み込まれない

```python
# config.py で確認
from dotenv import load_dotenv
import os

load_dotenv(verbose=True)  # verbose=True で詳細表示
print(os.getenv('NEWSAPI_KEY'))  # None なら読み込まれていない
```

---

## ✅ チェックリスト

セットアップが完了したか確認：

- [ ] Python がインストールされた（`python --version` で確認）
- [ ] `pip` がインストールされた（`pip --version` で確認）
- [ ] プロジェクトフォルダが作成された
- [ ] 仮想環境が作成された（`venv\Scripts\activate` で有効化可能）
- [ ] requirements.txt がインストールされた
- [ ] API キーが取得できた（NewsAPI, Claude）
- [ ] `.env` ファイルが作成された
- [ ] フォルダ構造が作成された
- [ ] `python src/main.py` が実行できる

すべてチェック✅できたら、**IMPLEMENTATION_PLAN.md** でステップ 1 を始めてください！

---

**次は LOGIC_DETAILED.md を読んでください！**
