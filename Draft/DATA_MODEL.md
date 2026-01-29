# Data Model - データモデル設計書

## 📚 概要

複数のニュースソース（NewsAPI, RSS, EDINET, arXiv など）から取得したデータを、
**統一スキーマに正規化** することで、以降の処理（フィルタリング、スコアリング等）
を統一的に実装できるようにします。

---

## 🎯 統一スキーマ：UniversalArticle クラス

すべてのニュースソースを、この統一フォーマットに変換します。

```python
# src/models.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
import uuid

@dataclass
class UniversalArticle:
    """
    全ニュースソースの統一スキーマ
    
    どのソース（NewsAPI, RSS, EDINET など）から取得した記事でも、
    このクラスに統一して扱う。
    
    【使用例】
    article = UniversalArticle(
        id="uuid-xxx",
        title="OpenAI が GPT-5 を発表",
        source_url="https://example.com",
        ...
    )
    """
    
    # =====================================
    # 【コア情報】全ソースで必須
    # =====================================
    id: str                           # 一意識別子（UUID）
    title: str                        # 記事タイトル
    source_url: str                   # 元記事へのリンク
    source_name: str                  # ソース名（"NewsAPI", "日経新聞" など）
    published_at: datetime            # 記事の公開日時
    fetched_at: datetime              # システムが記事を取得した日時
    
    # =====================================
    # 【分類情報】カテゴリ・ソースタイプ
    # =====================================
    source_type: str                  # ソースの種類
                                      # "newsapi" | "rss" | "edinet" | "arxiv"
    category: str                     # カテゴリ（後で自動判定）
                                      # "AI" | "決算" | "科学" | "モノづくり" | "ボードゲーム"
    
    # =====================================
    # 【処理後の情報】オプション（None 可）
    # =====================================
    summary: Optional[str] = None     # 要約（Claude 生成）
    keywords: Optional[List[str]] = None  # キーワード（自動抽出）
    relevance_score: Optional[int] = None # 関連度スコア（0-100）
    credibility_score: Optional[int] = None # ソース信頼度（0-100）
    
    # =====================================
    # 【メタデータ】元のデータ保持用
    # =====================================
    original_data: dict = None        # 元のソースからのデータ（参照用）
                                      # なぜ？各ソース固有の情報が必要な時があるため
    
    # =====================================
    # 【ソース固有情報】オプション
    # =====================================
    authors: Optional[List[str]] = None     # 著者（論文の場合など）
    language: str = "ja"                    # 言語（デフォルト：日本語）
    region: str = "JP"                      # 地域（デフォルト：日本）
    
    # =====================================
    # 【その他フラグ】
    # =====================================
    is_cached: bool = False           # キャッシュから取得したか？
    is_duplicate: bool = False        # 重複検出済みか？
    
    def __post_init__(self):
        """
        データ検証処理
        
        データが正しい形式か確認。
        例えば、relevance_score は 0-100 の範囲か？など
        """
        if self.relevance_score is not None:
            assert 0 <= self.relevance_score <= 100, \
                "relevance_score は 0-100 の範囲で指定してください"
        
        if self.credibility_score is not None:
            assert 0 <= self.credibility_score <= 100, \
                "credibility_score は 0-100 の範囲で指定してください"
```

---

## 🔄 各ソースの正規化方法

### **1. NewsAPI → UniversalArticle**

**NewsAPI の応答例：**
```json
{
  "source": {
    "id": "techcrunch",
    "name": "TechCrunch"
  },
  "author": "Sarah Chen",
  "title": "OpenAI Releases GPT-5 Preview",
  "description": "OpenAI announced GPT-5...",
  "url": "https://techcrunch.com/...",
  "urlToImage": "https://...",
  "publishedAt": "2026-01-29T08:00:00Z",
  "content": "OpenAI announced..."
}
```

**変換コード：**
```python
# src/data_sources/newsapi_source.py

from src.models import UniversalArticle
from datetime import datetime
import uuid

class NewsAPISource:
    
    @staticmethod
    def normalize(newsapi_article: dict) -> UniversalArticle:
        """
        NewsAPI の記事フォーマットを UniversalArticle に変換
        
        パラメータ：
            newsapi_article (dict): NewsAPI から返されたニュース記事
        
        戻り値：
            UniversalArticle: 統一フォーマットに変換された記事
        """
        
        # ソース名を取得（辞書のキー名が "source" で、その中に "name" がある）
        source_name = newsapi_article.get('source', {}).get('name', 'Unknown')
        
        # 公開日を datetime に変換
        published_at_str = newsapi_article.get('publishedAt', '')
        published_at = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
        
        # 一意 ID を生成（タイトル + ソース名のハッシュ）
        article_id = str(uuid.uuid5(
            uuid.NAMESPACE_DNS,
            f"{newsapi_article['title']}-{source_name}"
        ))
        
        # UniversalArticle に変換
        return UniversalArticle(
            id=article_id,
            title=newsapi_article.get('title', ''),
            source_url=newsapi_article.get('url', ''),
            source_name=source_name,
            published_at=published_at,
            fetched_at=datetime.now(timezone.utc),
            source_type='newsapi',
            category='unknown',  # 後で自動判定
            original_data=newsapi_article  # 元データは保持しておく
        )
```

---

### **2. RSS フィード → UniversalArticle**

**RSS エントリの例：**
```xml
<item>
  <title>日経新聞：トヨタの営業利益が過去最高</title>
  <link>https://nikkei.com/article/...</link>
  <pubDate>Wed, 29 Jan 2026 12:00:00 +0900</pubDate>
  <description>トヨタ自動車が...</description>
</item>
```

**変換コード：**
```python
# src/data_sources/rss_source.py

import feedparser
from email.utils import parsedate_to_datetime
import uuid

class RSSSource:
    
    @staticmethod
    def normalize(rss_entry: dict, source_name: str) -> UniversalArticle:
        """
        RSS フィードのエントリを UniversalArticle に変換
        
        パラメータ：
            rss_entry (dict): feedparser が解析した RSS エントリ
            source_name (str): RSS ソースの名前（"日経新聞" など）
        
        戻り値：
            UniversalArticle: 統一フォーマット
        """
        
        # 公開日を datetime に変換
        # RSS では "published_parsed" が struct_time なので datetime に変換
        published_at = datetime(*rss_entry['published_parsed'][:6])
        
        # 一意 ID を生成
        article_id = str(uuid.uuid5(
            uuid.NAMESPACE_DNS,
            f"{rss_entry['title']}-{source_name}"
        ))
        
        return UniversalArticle(
            id=article_id,
            title=rss_entry.get('title', ''),
            source_url=rss_entry.get('link', ''),
            source_name=source_name,
            published_at=published_at,
            fetched_at=datetime.now(timezone.utc),
            source_type='rss',
            category='unknown',
            original_data=rss_entry
        )
```

---

### **3. EDINET（日本企業決算）→ UniversalArticle**

**EDINET 開示情報の例：**
```json
{
  "document_id": "S100ABC123",
  "document_name": "トヨタ自動車株式会社 2025年度第3四半期決算説明会資料",
  "submitter_name": "トヨタ自動車",
  "submission_date": "2026-01-28",
  "document_url": "https://edinet-api.fsa.go.jp/doc/S100ABC123",
  "xbrl_url": "https://edinet-api.fsa.go.jp/xbrl/S100ABC123"
}
```

**変換コード：**
```python
# src/data_sources/edinet_source.py

import uuid

class EDINETSource:
    
    @staticmethod
    def normalize(filing_data: dict) -> UniversalArticle:
        """
        EDINET 開示情報を UniversalArticle に変換
        
        パラメータ：
            filing_data (dict): EDINET API から返された開示情報
        
        戻り値：
            UniversalArticle: 統一フォーマット
        """
        
        # 提出日を datetime に変換
        submission_date_str = filing_data.get('submission_date', '')
        published_at = datetime.strptime(submission_date_str, '%Y-%m-%d')
        
        # 一意 ID を生成
        article_id = filing_data.get('document_id', str(uuid.uuid4()))
        
        return UniversalArticle(
            id=article_id,
            title=filing_data.get('document_name', ''),
            source_url=filing_data.get('document_url', ''),
            source_name=filing_data.get('submitter_name', ''),
            published_at=published_at,
            fetched_at=datetime.now(timezone.utc),
            source_type='edinet',
            category='決算',  # EDINET は必ず決算関連
            original_data=filing_data
        )
```

---

### **4. arXiv（学術論文）→ UniversalArticle**

**arXiv API の応答例：**
```json
{
  "id": "2401.12345",
  "title": "A Novel Approach to Quantum Computing",
  "authors": ["Alice Smith", "Bob Johnson"],
  "summary": "We propose a new method for...",
  "published": "2026-01-29T10:00:00Z",
  "arxiv_url": "https://arxiv.org/abs/2401.12345"
}
```

**変換コード：**
```python
# src/data_sources/arxiv_source.py

import uuid

class ArxivSource:
    
    @staticmethod
    def normalize(paper: dict) -> UniversalArticle:
        """
        arXiv 論文情報を UniversalArticle に変換
        
        パラメータ：
            paper (dict): arXiv API から返された論文情報
        
        戻り値：
            UniversalArticle: 統一フォーマット
        """
        
        # 公開日を datetime に変換
        published_at = datetime.fromisoformat(
            paper.get('published', '').replace('Z', '+00:00')
        )
        
        # 著者リストを取得
        authors = paper.get('authors', [])
        
        return UniversalArticle(
            id=paper.get('id', str(uuid.uuid4())),
            title=paper.get('title', ''),
            source_url=paper.get('arxiv_url', ''),
            source_name='arXiv',
            published_at=published_at,
            fetched_at=datetime.now(timezone.utc),
            source_type='arxiv',
            category='科学',  # arXiv は必ず科学関連
            authors=authors,
            original_data=paper
        )
```

---

## 🔗 正規化の流れ（全体）

```python
# src/normalizer.py

from src.data_sources.newsapi_source import NewsAPISource
from src.data_sources.rss_source import RSSSource
from src.data_sources.edinet_source import EDINETSource
from src.data_sources.arxiv_source import ArxivSource

class DataNormalizer:
    """
    複数のソースから取得したデータを、
    UniversalArticle に統一する処理
    """
    
    @staticmethod
    def normalize_articles(raw_articles_by_source: dict) -> List[UniversalArticle]:
        """
        複数ソースの記事をまとめて正規化
        
        パラメータ：
            raw_articles_by_source (dict): {
                'newsapi': [記事, 記事, ...],
                'rss': [記事, 記事, ...],
                'edinet': [記事, 記事, ...]
            }
        
        戻り値：
            List[UniversalArticle]: 統一フォーマットの記事リスト
        """
        normalized = []
        
        # NewsAPI 記事を正規化
        for article in raw_articles_by_source.get('newsapi', []):
            normalized.append(NewsAPISource.normalize(article))
        
        # RSS 記事を正規化
        for source_name, entries in raw_articles_by_source.get('rss', {}).items():
            for entry in entries:
                normalized.append(RSSSource.normalize(entry, source_name))
        
        # EDINET 記事を正規化
        for filing in raw_articles_by_source.get('edinet', []):
            normalized.append(EDINETSource.normalize(filing))
        
        # arXiv 論文を正規化
        for paper in raw_articles_by_source.get('arxiv', []):
            normalized.append(ArxivSource.normalize(paper))
        
        return normalized
```

---

## 💾 データベース設計

### **テーブル定義（SQLite 例）**

```sql
-- articles_history テーブル
-- 毎日のニュース記事を蓄積するテーブル

CREATE TABLE articles_history (
    -- 基本情報
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    source_url TEXT,
    source_name TEXT,
    source_type TEXT,
    
    -- 日時情報
    published_at DATETIME,
    fetched_at DATETIME,
    
    -- 分類
    category TEXT,
    
    -- スコア
    relevance_score INTEGER,
    credibility_score INTEGER,
    
    -- 処理済み情報
    summary TEXT,
    keywords TEXT,  -- JSON 形式で保存：["AI", "企業"]
    
    -- メタデータ
    authors TEXT,   -- JSON 形式
    original_data TEXT,  -- JSON 形式（元データ）
    
    -- フラグ
    is_cached BOOLEAN DEFAULT 0,
    is_duplicate BOOLEAN DEFAULT 0,
    
    -- レコード管理
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- インデックス（検索を高速化）
CREATE INDEX idx_category ON articles_history(category);
CREATE INDEX idx_published_at ON articles_history(published_at);
CREATE INDEX idx_source_type ON articles_history(source_type);
```

### **CSV ファイル形式**

```csv
id,title,source_name,published_at,fetched_at,category,relevance_score,summary,keywords
abc123,OpenAI が GPT-5 を発表,TechCrunch,2026-01-29T08:00:00,2026-01-29T06:15:00,AI,92,OpenAI は次世代モデル GPT-5 を発表しました。精度が 35% 向上しています。,"[""AI"",""OpenAI"",""言語モデル""]"
def456,トヨタ営業利益 28% 増,EDINET,2026-01-28T09:00:00,2026-01-29T06:15:00,決算,85,トヨタ自動車の営業利益が過去最高を更新しました。EV 事業が好調です。,"[""決算"",""トヨタ"",""自動車""]"
```

---

## 🔍 データ整合性チェック

```python
# src/models.py

class UniversalArticle:
    
    def validate(self) -> bool:
        """
        記事データが正しいか検証
        
        戻り値：
            bool: データが有効なら True、無効なら False
        """
        
        # 必須フィールドチェック
        if not self.id or not self.title or not self.source_url:
            return False
        
        # スコア範囲チェック
        if self.relevance_score is not None:
            if not (0 <= self.relevance_score <= 100):
                return False
        
        # 日付の妥当性チェック
        if self.published_at > datetime.now():
            # 未来の日付は不正
            return False
        
        if self.fetched_at < self.published_at:
            # 取得日時 < 公開日時 は不正
            return False
        
        return True
```

---

## 📊 スキーマ関係図

```
【入力】複数のソース
  ├─ NewsAPI（REST API）
  ├─ RSS フィード（XML）
  ├─ EDINET API（JSON）
  └─ arXiv API（XML）

          ↓
          
【正規化】各ソース別の変換処理
  ├─ NewsAPISource.normalize()
  ├─ RSSSource.normalize()
  ├─ EDINETSource.normalize()
  └─ ArxivSource.normalize()

          ↓
          
【統一】UniversalArticle
  └─ id, title, source_url, ...
  
          ↓
          
【以降の処理】統一的に扱える
  ├─ フィルタリング
  ├─ スコアリング
  ├─ 要約生成
  ├─ キーワード抽出
  └─ ...すべて同じロジック
  
          ↓
          
【出力】複数形式
  ├─ HTML
  ├─ Markdown
  ├─ Notion
  └─ Note
```

---

## 🎯 実装上の注意点

### **1. 日時の扱い**
```python
# ❌ 間違い（タイムゾーン情報がない）
published_at = datetime.fromisoformat("2026-01-29T08:00:00")

# ✅ 正しい（UTC を指定）
from datetime import timezone
published_at = datetime.fromisoformat("2026-01-29T08:00:00Z".replace('Z', '+00:00'))
published_at = published_at.astimezone(timezone.utc)
```

### **2. ID の生成**
```python
# ❌ 間違い（毎回異なる ID になってしまう）
id = str(uuid.uuid4())

# ✅ 正しい（同じ記事なら同じ ID になる）
id = str(uuid.uuid5(
    uuid.NAMESPACE_DNS,
    f"{title}-{source_name}"
))
```

### **3. JSON フィールド**
```python
# keywords や authors は JSON で保存
import json

# 保存時：
keywords_json = json.dumps(["AI", "企業"])  # ["AI", "企業"] → '"[""AI"", ""企業""]'

# 読み込み時：
keywords = json.loads(keywords_json)  # ["AI", "企業"]
```

---

## ✨ 完成時の状態

```python
# このようにすべてのソースを統一的に扱える

articles = fetch_from_multiple_sources()  # 複数ソース取得
normalized = normalize_articles(articles)  # 正規化

# 以下は同じ処理で OK
for article in normalized:
    score = calculate_score(article)      # スコア計算
    summary = generate_summary(article)   # 要約生成
    keywords = extract_keywords(article)  # キーワード抽出
```

---

**次は IMPLEMENTATION_PLAN.md を読んでください！**
