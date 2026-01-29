# ER 図・DB 設計書 - Database Design Document

## 📋 ドキュメント情報

```
プロジェクト名：Digest Daily
バージョン：1.0
作成日：2026-01-29
対象データベース：SQLite（開発）/ PostgreSQL（将来）
```

---

## 1️⃣ データベース概要

### 1.1 使用技術

```
【開発・本番】
- SQLite：ローカル開発用、本番環境での簡易用途
  ファイル：articles_archive.db

【将来】
- PostgreSQL：複数ユーザー化時に対応予定
```

### 1.2 データ保持期間

```
articles テーブル：7 日間（記事取得後）
articles_archive テーブル：90 日間（アーカイブ）
ログテーブル：30 日間（保持）
```

---

## 2️⃣ ER 図（エンティティ・リレーションシップ）

```
┌─────────────────────┐
│   articles          │
│  (今日の記事)       │
├─────────────────────┤
│ id (PK)             │
│ title               │
│ summary             │
│ source_url          │
│ source_name         │
│ category            │
│ relevance_score     │
│ published_at        │
│ fetched_at          │
│ keywords (JSON)     │
│ created_at          │
└─────────────────────┘
        │
        │ 1:N
        │
┌─────────────────────┐
│ articles_archive    │
│ (過去記事履歴)      │
├─────────────────────┤
│ id (PK)             │
│ article_id (FK)     │
│ archive_date        │
│ stats               │
└─────────────────────┘


┌─────────────────────┐
│ daily_reports       │
│ (日次レポート)      │
├─────────────────────┤
│ report_date (PK)    │
│ total_articles      │
│ avg_score           │
│ generated_at        │
└─────────────────────┘
```

---

## 3️⃣ テーブル定義

### 3.1 articles テーブル（メインテーブル）

**目的**：毎日取得したニュース記事を保存

```sql
CREATE TABLE articles (
    -- 【主キー・識別情報】
    id TEXT PRIMARY KEY,
    
    -- 【記事コンテンツ】
    title TEXT NOT NULL,
    summary TEXT,
    source_url TEXT NOT NULL,
    
    -- 【メタデータ】
    source_name TEXT NOT NULL,
    source_type TEXT,  -- "newsapi" | "rss" | "edinet" | "arxiv"
    
    -- 【カテゴリ・タグ】
    category TEXT,  -- "AI" | "決算" | "科学" | "モノづくり" | "ボードゲーム"
    keywords TEXT,  -- JSON 形式：["AI", "企業"]
    
    -- 【スコア】
    relevance_score INTEGER,  -- 0-100
    credibility_score INTEGER,  -- 0-100
    
    -- 【日時情報】
    published_at DATETIME,  -- 記事公開日時
    fetched_at DATETIME,    -- システム取得日時
    
    -- 【管理フィールド】
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT 0,  -- ユーザーが読んだか
    is_starred BOOLEAN DEFAULT 0,  -- ブックマーク
    
    -- 【オプション】
    authors TEXT,  -- JSON 形式：["著者1", "著者2"]
    language TEXT DEFAULT 'ja',
    notes TEXT  -- ユーザーメモ
);

-- 【インデックス】
CREATE INDEX IF NOT EXISTS idx_category ON articles(category);
CREATE INDEX IF NOT EXISTS idx_published_at ON articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_relevance_score ON articles(relevance_score DESC);
CREATE INDEX IF NOT EXISTS idx_source_type ON articles(source_type);
CREATE INDEX IF NOT EXISTS idx_created_at ON articles(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_category_date ON articles(category, published_at DESC);
```

**行数目安**：
```
毎日 50 件 × 7 日 = 350 件（毎週クリア）
ディスク容量：約 5-10 MB
```

---

### 3.2 articles_archive テーブル（アーカイブ）

**目的**：過去記事の履歴を長期保存

```sql
CREATE TABLE articles_archive (
    -- 【主キー】
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 【記事データ】
    article_id TEXT NOT NULL,
    title TEXT NOT NULL,
    category TEXT,
    relevance_score INTEGER,
    
    -- 【日付】
    published_at DATETIME,
    archived_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- 【メタデータ】
    source_name TEXT,
    keywords TEXT  -- JSON
);

-- 【インデックス】
CREATE INDEX IF NOT EXISTS idx_archive_category ON articles_archive(category);
CREATE INDEX IF NOT EXISTS idx_archive_date ON articles_archive(archived_at DESC);
CREATE INDEX IF NOT EXISTS idx_archive_score ON articles_archive(relevance_score DESC);
```

**保持期間**：90 日（古いデータは定期削除）

```sql
-- 90日以上前のデータを削除（毎月 1 回実行）
DELETE FROM articles_archive
WHERE archived_at < datetime('now', '-90 days');
```

---

### 3.3 daily_reports テーブル（日次レポート）

**目的**：毎日の集計統計情報を保存

```sql
CREATE TABLE daily_reports (
    -- 【主キー】
    report_date DATE PRIMARY KEY,
    
    -- 【統計情報】
    total_articles INTEGER,
    avg_score REAL,
    max_score INTEGER,
    min_score INTEGER,
    
    -- 【カテゴリ別統計】
    ai_count INTEGER DEFAULT 0,
    finance_count INTEGER DEFAULT 0,
    science_count INTEGER DEFAULT 0,
    manufacturing_count INTEGER DEFAULT 0,
    boardgame_count INTEGER DEFAULT 0,
    
    -- 【処理情報】
    processing_time_seconds INTEGER,
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 【インデックス】
CREATE INDEX IF NOT EXISTS idx_report_date ON daily_reports(report_date DESC);
```

---

### 3.4 api_usage テーブル（API 使用履歴）

**目的**：API コスト・パフォーマンス追跡

```sql
CREATE TABLE api_usage (
    -- 【主キー】
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- 【API 情報】
    api_name TEXT NOT NULL,  -- "claude" | "openai" | "gemini"
    endpoint TEXT,  -- "summarize" | "keyword_extract"
    
    -- 【使用量】
    tokens_used INTEGER,
    response_time_ms INTEGER,
    
    -- 【ステータス】
    status TEXT,  -- "success" | "error" | "timeout"
    error_message TEXT,
    
    -- 【日時】
    executed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 【インデックス】
CREATE INDEX IF NOT EXISTS idx_api_usage_date ON api_usage(executed_at DESC);
CREATE INDEX IF NOT EXISTS idx_api_usage_name ON api_usage(api_name);
```

**用途**：
```python
# 月額 API コスト計算
SELECT 
    api_name,
    SUM(tokens_used) as total_tokens
FROM api_usage
WHERE executed_at > datetime('now', '-30 days')
GROUP BY api_name;
```

---

## 4️⃣ CSV エクスポートフォーマット

### 4.1 articles.csv

```csv
id,title,source_name,published_at,category,relevance_score,summary
abc123,OpenAI が GPT-5 を発表,TechCrunch,2026-01-29T08:00:00,AI,92,OpenAI は次世代モデル GPT-5 を発表...
def456,トヨタ営業利益 28% 増,EDINET,2026-01-28T09:00:00,決算,85,トヨタ自動車の営業利益が過去最高を更新...
```

---

## 5️⃣ データベース初期化スクリプト

```python
# src/storage/database.py

import sqlite3

class DatabaseManager:
    
    def __init__(self, db_path: str = 'articles_archive.db'):
        self.db_path = db_path
        self.conn = None
    
    def init_database(self):
        """データベース初期化"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                category TEXT,
                relevance_score INTEGER,
                published_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        print("✅ DB 初期化完了")
    
    def insert_articles(self, articles: list):
        """記事を挿入"""
        cursor = self.conn.cursor()
        for article in articles:
            cursor.execute('''
                INSERT OR REPLACE INTO articles 
                (id, title, category, relevance_score, published_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (article.id, article.title, article.category, 
                  article.relevance_score, article.published_at))
        self.conn.commit()
```

---

**DB 設計が完成です！** 🎉
