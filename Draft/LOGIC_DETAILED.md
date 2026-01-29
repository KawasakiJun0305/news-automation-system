# Logic Detailed - ロジック詳細説明

## 📊 全体フロー

```
取得した記事
    ↓
【1. フィルタリング】低品質・スパム除外
    ↓
【2. 正規化】複数ソースの形式を統一
    ↓
【3. スコアリング】重要度を数値化（0-100）
    ↓
【4. 要約生成】Claude で日本語要約
    ↓
【5. キーワード抽出】重要単語を自動抽出
    ↓
【6. 重複排除】同じニュースを統一
    ↓
【7. ランキング】スコア順に整列
    ↓
最終的なニュースレポート
```

---

## 1️⃣ フィルタリング（低品質記事除外）

### 目的
スパム、削除済み記事、短すぎる記事など、品質の低い記事を除外。

```python
# src/core/filter.py

class ArticleFilter:
    """
    記事の品質をチェックするクラス
    """
    
    FILTER_RULES = {
        'min_title_length': 10,        # タイトル最小 10 文字
        'min_content_length': 50,      # 本文最小 50 文字
        'max_article_age_hours': 72,   # 72 時間以上古い記事は除外
        'blacklist_titles': ['[Removed]', '[Deleted]'],  # 削除済みマーク
    }
    
    @staticmethod
    def filter_articles(articles: list) -> list:
        """
        記事をフィルタリング
        
        戻り値：
            list: フィルタを通過した記事
        """
        filtered = []
        
        for article in articles:
            # ❌ タイトルがない OR 短すぎる
            if not article.title or \
               len(article.title) < ArticleFilter.FILTER_RULES['min_title_length']:
                continue
            
            # ❌ 削除済みマーク
            if any(mark in article.title for mark in ArticleFilter.FILTER_RULES['blacklist_titles']):
                continue
            
            # ❌ 本文がない OR 短すぎる
            if article.summary is None or \
               len(article.summary) < ArticleFilter.FILTER_RULES['min_content_length']:
                continue
            
            # ❌ 古すぎる（72 時間以上前）
            from datetime import datetime, timedelta, timezone
            age_hours = (datetime.now(timezone.utc) - article.published_at).total_seconds() / 3600
            if age_hours > ArticleFilter.FILTER_RULES['max_article_age_hours']:
                continue
            
            # ✅ すべてのチェックを通過
            filtered.append(article)
        
        return filtered
```

---

## 2️⃣ スコアリング（重要度計算）

### 計算式

```
スコア = 
  キーワードマッチ度 × 40% +
  記事の鮮度 × 20% +
  ソース信頼度 × 20% +
  コンテンツ質 × 20%
```

### 詳細実装

```python
# src/core/scorer.py

from datetime import datetime, timezone

class ArticleScorer:
    """
    記事をスコアリングするクラス
    """
    
    KEYWORD_WEIGHT = 0.40
    RECENCY_WEIGHT = 0.20
    CREDIBILITY_WEIGHT = 0.20
    QUALITY_WEIGHT = 0.20
    
    CREDIBILITY_MAP = {
        'Nature': 20,
        'arXiv': 18,
        '日経新聞': 18,
        'TechCrunch': 16,
        'Reuters': 17,
        # ... その他のソース
    }
    
    @staticmethod
    def calculate_score(article, keywords_matched: list) -> int:
        """
        記事のスコア（0-100）を計算
        """
        score = 0
        
        # ===== 1. キーワードマッチ度（40%）=====
        # マッチしたキーワード数が多いほど高スコア
        keyword_matches = len([
            kw for kw in keywords_matched
            if kw.lower() in article.title.lower() or \
               kw.lower() in (article.summary or '').lower()
        ])
        keyword_score = min(keyword_matches * 20, 40)  # 最大 40
        score += keyword_score
        
        # ===== 2. 記事の鮮度（20%）=====
        # 最近のニュースほど高スコア
        hours_old = (datetime.now(timezone.utc) - article.published_at).total_seconds() / 3600
        
        if hours_old < 1:
            recency_score = 20  # 1 時間以内
        elif hours_old < 6:
            recency_score = 15  # 6 時間以内
        elif hours_old < 24:
            recency_score = 10  # 24 時間以内
        else:
            recency_score = 5
        
        score += recency_score
        
        # ===== 3. ソース信頼度（20%）=====
        source_credibility = ArticleScorer.CREDIBILITY_MAP.get(
            article.source_name, 10  # デフォルト 10
        )
        score += source_credibility
        
        # ===== 4. コンテンツ質（20%）=====
        # タイトル長、本文長で判定
        title_length_score = min(len(article.title) // 10, 10)
        summary_length = len(article.summary or '') if article.summary else 0
        summary_length_score = min(summary_length // 50, 10)
        quality_score = (title_length_score + summary_length_score) / 2
        
        score += quality_score
        
        return int(min(score, 100))  # 最大 100
```

---

## 3️⃣ 要約生成

### 手順

```python
# src/llm/claude_client.py

class ClaudeClient:
    
    async def summarize(self, article) -> str:
        """
        記事を要約生成
        """
        prompt = f"""
次のニュース記事を、簡潔な日本語で2-3文の要約にしてください。
正確性を重視し、主観的な評価は入れないでください。

【タイトル】
{article.title}

【本文】
{article.original_data.get('content', '')[:500]}

【要約】
"""
        
        message = self.client.messages.create(
            model="claude-opus-4-5-20251101",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text.strip()
```

---

## 4️⃣ キーワード抽出

```python
# src/core/keyword_extractor.py

class KeywordExtractor:
    
    @staticmethod
    def extract(article) -> list:
        """
        記事から重要キーワードを自動抽出
        """
        text = f"{article.title} {article.summary or ''}"
        
        # 設定済みキーワードをチェック
        matched = []
        for keyword in KEYWORD_MAPPING.keys():
            if keyword.lower() in text.lower():
                matched.append(keyword)
        
        return list(set(matched))  # 重複排除
```

---

## 5️⃣ 重複排除

```python
# src/core/deduplicator.py

class Deduplicator:
    
    @staticmethod
    def deduplicate(articles: list) -> list:
        """
        同じニュースの複数報道を統合
        """
        seen = {}
        deduplicated = []
        
        for article in articles:
            # タイトルの正規化（数字を統一）
            import re
            normalized = re.sub(r'\d+', '0', article.title.lower())
            
            if normalized in seen:
                # 既に見た似た記事
                existing = seen[normalized]
                # スコアが高い方を保持
                if article.relevance_score > existing.relevance_score:
                    deduplicated.remove(existing)
                    deduplicated.append(article)
            else:
                seen[normalized] = article
                deduplicated.append(article)
        
        return deduplicated
```

---

## 6️⃣ ランキング

```python
# src/core/ranker.py

class Ranker:
    
    @staticmethod
    def rank_by_category(articles: list) -> dict:
        """
        カテゴリごとに記事をランク付け
        """
        by_category = {}
        
        for article in articles:
            if article.category not in by_category:
                by_category[article.category] = []
            by_category[article.category].append(article)
        
        # 各カテゴリをスコア順にソート
        for category in by_category:
            by_category[category] = sorted(
                by_category[category],
                key=lambda x: (x.relevance_score, x.published_at),
                reverse=True
            )
        
        return by_category
```

---

## 📈 スコアリング例

```
【例 1】
タイトル："OpenAI が GPT-5 を発表"
ソース："TechCrunch"
公開 ：2 時間前
マッチキーワード："AI"

計算：
- キーワード（40%）：1 個マッチ × 20 = 20
- 鮮度（20%）：2 時間前 = 15
- 信頼度（20%）：TechCrunch = 16
- コンテンツ質（20%）：タイトル長・本文長 = 15

合計スコア：20 + 15 + 16 + 15 = 66


【例 2】
タイトル ："トヨタの営業利益 28% 増"
ソース："EDINET（日本企業決算）"
公開：1 日前
マッチキーワード："決算"

計算：
- キーワード（40%）：1 個マッチ × 20 = 20
- 鮮度（20%）：24 時間前 = 10
- 信頼度（20%）：金融情報源 = 18
- コンテンツ質（20%）：タイトル長・本文長 = 17

合計スコア：20 + 10 + 18 + 17 = 65
```

---

## 🧪 テスト例

```python
# tests/test_scorer.py

def test_scoring():
    """
    スコアリングが正しく計算されるか
    """
    article = UniversalArticle(
        id="test1",
        title="AI の新展開",
        source_name="TechCrunch",
        published_at=datetime.now() - timedelta(hours=2),
        fetched_at=datetime.now(),
        summary="AI が発表されました"
    )
    
    score = ArticleScorer.calculate_score(article, ['AI'])
    
    # スコアが 0-100 の範囲
    assert 0 <= score <= 100
    
    # "AI" キーワードマッチで高スコア
    assert score > 50
```

---

**次は MULTI_API_ROUTING.md を読んでください！**
