# Multi Source Expansion - マルチソース拡張ガイド

## 🎯 目的

新しいニュースソース（RSS、EDINET、arXiv など）を追加する方法を説明。

---

## 📝 新しいソース追加の 5 ステップ

### Step 1: ソース用クラスを継承

```python
# src/data_sources/new_source.py

from src.data_sources.base_source import BaseSource
from src.models import UniversalArticle

class NewSource(BaseSource):
    """
    新しいニュースソース
    """
    
    def __init__(self):
        self.source_type = "new_source"
        self.source_name = "New Source Name"
    
    async def fetch(self) -> list:
        """
        データを取得する（実装必須）
        """
        # API 呼び出し、スクレイピング等
        pass
    
    def normalize(self, raw_data: dict) -> UniversalArticle:
        """
        取得したデータを UniversalArticle に正規化
        """
        return UniversalArticle(
            id=raw_data.get('id'),
            title=raw_data.get('title'),
            source_url=raw_data.get('url'),
            source_name=self.source_name,
            published_at=parse_date(raw_data.get('published')),
            fetched_at=datetime.now(),
            source_type=self.source_type,
            original_data=raw_data
        )
```

### Step 2: メイン処理に登録

```python
# src/main.py

async def main():
    from src.data_sources.newsapi_source import NewsAPISource
    from src.data_sources.new_source import NewSource
    
    fetchers = [
        NewsAPISource(),
        NewSource(),  # ← 新しいソースを追加
    ]
    
    all_articles = []
    for fetcher in fetchers:
        articles = await fetcher.fetch()
        all_articles.extend(articles)
```

### Step 3: 設定に追加

```python
# config.py

DATA_SOURCES = {
    "newsapi": {
        "enabled": True,
        "categories": ["AI", "決算", "科学"],
        "weight": 1.0
    },
    "new_source": {
        "enabled": True,
        "categories": ["科学"],  # このソースはどのカテゴリ対象か
        "weight": 1.0,
        "rate_limit": {"calls": 100, "window": 3600}
    }
}
```

### Step 4: テスト実装

```python
# tests/test_new_source.py

@pytest.mark.asyncio
async def test_new_source_fetch():
    source = NewSource()
    articles = await source.fetch()
    
    assert len(articles) > 0
    assert all(hasattr(a, 'title') for a in articles)
```

### Step 5: ドキュメント更新

README.md に追加：
```
### サポートされているソース
- NewsAPI
- New Source（説明）
```

---

## 💡 実装例 1：RSS フィード追加

```python
# src/data_sources/rss_source.py

import feedparser

class RSSSource(BaseSource):
    
    def __init__(self, url: str, source_name: str):
        self.url = url
        self.source_name = source_name
        self.source_type = "rss"
    
    async def fetch(self) -> list:
        """
        RSS フィードを取得
        """
        feed = feedparser.parse(self.url)
        articles = []
        
        for entry in feed.entries[:10]:  # 最新 10 件
            article = self.normalize(entry)
            articles.append(article)
        
        return articles
```

---

## 💡 実装例 2：EDINET（決算情報）追加

```python
# src/data_sources/edinet_source.py

import requests

class EDINETSource(BaseSource):
    
    def __init__(self):
        self.api_url = "https://api.edinet-fsa.go.jp"
        self.source_type = "edinet"
    
    async def fetch(self) -> list:
        """
        EDINET から企業決算情報を取得
        """
        params = {
            'date': '2026-01-29',  # 本日の決算発表
            'type': 120  # 有価証券報告書
        }
        
        response = requests.get(f"{self.api_url}/documents", params=params)
        data = response.json()
        
        articles = [
            self.normalize(filing)
            for filing in data['results']
        ]
        
        return articles
```

---

## 🔗 data_fetcher で複数ソース統合

```python
# src/data_fetcher.py

class DataFetcher:
    """
    複数ソースをまとめて取得
    """
    
    def __init__(self):
        # ソースを登録
        self.sources = {
            'newsapi': NewsAPISource(),
            'rss_nikkei': RSSSource(
                'https://www.nikkei.com/rss/',
                'Nikkei'
            ),
            'rss_nhk': RSSSource(
                'https://www.nhk.or.jp/rss/',
                'NHK'
            ),
            'edinet': EDINETSource(),
            'arxiv': ArxivSource()
        }
    
    async def fetch_all(self) -> list:
        """
        全ソースから非同期で取得
        """
        tasks = [
            self._fetch_with_rate_limit(name, source)
            for name, source in self.sources.items()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_articles = []
        for result in results:
            if isinstance(result, Exception):
                logging.error(f"Fetch error: {result}")
            else:
                all_articles.extend(result)
        
        return all_articles
```

---

## 📊 ソース管理

```python
# ソースごとの信頼度・優先度設定

SOURCE_CONFIG = {
    "newsapi": {
        "credibility": 12,
        "priority": "high",
        "cost": "free"
    },
    "rss_nikkei": {
        "credibility": 18,
        "priority": "high",
        "cost": "free"
    },
    "edinet": {
        "credibility": 20,
        "priority": "critical",
        "cost": "free"
    },
    "arxiv": {
        "credibility": 18,
        "priority": "medium",
        "cost": "free"
    }
}
```

---

## ✅ 新ソース追加チェックリスト

- [ ] ソースクラス実装（BaseSource 継承）
- [ ] fetch() メソッド実装
- [ ] normalize() メソッド実装
- [ ] config.py に登録
- [ ] テスト実装
- [ ] data_fetcher に登録
- [ ] ドキュメント更新
- [ ] pytest でテスト成功

---

**次は GITHUB_ACTIONS_SETUP.md を読んでください！**
