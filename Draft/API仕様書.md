# API 仕様書 - API Specification

## 📋 ドキュメント情報

```
プロジェクト名：Digest Daily
バージョン：1.0
作成日：2026-01-29
対象：内部 API（クラス/関数インターフェース）
```

---

## 1️⃣ API 概要

このドキュメントは、**内部 API**（Python クラス・関数）の仕様を定義します。

REST API ではなく、Python モジュール間のインターフェースです。

---

## 2️⃣ Data Fetcher API

### 2.1 DataFetcher クラス

```python
class DataFetcher:
    """
    複数のニュースソースからデータを取得するクラス
    """
```

#### メソッド：fetch_all()

```python
async def fetch_all() -> List[UniversalArticle]:
    """
    全登録ソースからニュース記事を非同期取得
    
    戻り値：
        List[UniversalArticle]：取得した記事リスト
    
    例外：
        Exception：全ソースが失敗した場合
    
    使用例：
        fetcher = DataFetcher()
        articles = await fetcher.fetch_all()
        print(f"{len(articles)} 件取得")
    """
```

#### メソッド：fetch_by_source()

```python
async def fetch_by_source(source_name: str) -> List[UniversalArticle]:
    """
    特定ソースからのみ記事を取得
    
    パラメータ：
        source_name (str)：ソース名（"newsapi", "rss", など）
    
    戻り値：
        List[UniversalArticle]：取得した記事リスト
    
    例外：
        ValueError：未知のソース名
        Exception：ソース取得失敗
    
    使用例：
        articles = await fetcher.fetch_by_source('newsapi')
    """
```

---

## 3️⃣ Article Processor API

### 3.1 DataNormalizer クラス

```python
class DataNormalizer:
    """
    複数ソースのデータを UniversalArticle に統一
    """

    @staticmethod
    def normalize_articles(raw_articles: dict) -> List[UniversalArticle]:
        """
        複数ソースの記事をまとめて正規化
        
        パラメータ：
            raw_articles (dict)：{
                'newsapi': [記事, 記事, ...],
                'rss': {
                    'nikkei': [エントリ, ...],
                    'nhk': [エントリ, ...]
                }
            }
        
        戻り値：
            List[UniversalArticle]：正規化済み記事リスト
        
        使用例：
            articles = DataNormalizer.normalize_articles(raw_data)
        """
```

---

### 3.2 ArticleFilter クラス

```python
class ArticleFilter:
    """
    記事の品質をチェック・フィルタリング
    """

    @staticmethod
    def filter_articles(articles: List[UniversalArticle]) -> List[UniversalArticle]:
        """
        低品質・スパム記事を除外
        
        チェック項目：
        - タイトル長 >= 10 文字
        - 削除済みマークなし
        - 公開日が 72 時間以内
        - 本文が存在
        
        パラメータ：
            articles：検査対象の記事リスト
        
        戻り値：
            List[UniversalArticle]：フィルター通過した記事
        
        使用例：
            filtered = ArticleFilter.filter_articles(articles)
            print(f"{len(articles)} → {len(filtered)} 件")
        """
```

---

### 3.3 ArticleScorer クラス

```python
class ArticleScorer:
    """
    記事の重要度をスコアリング（0-100）
    """

    @staticmethod
    def calculate_score(
        article: UniversalArticle,
        keywords_matched: List[str]
    ) -> int:
        """
        記事のスコア（重要度）を計算
        
        スコア計算式：
            スコア = 
              キーワードマッチ度 × 40% +
              記事の鮮度 × 20% +
              ソース信頼度 × 20% +
              コンテンツ質 × 20%
        
        パラメータ：
            article (UniversalArticle)：採点対象の記事
            keywords_matched (List[str])：マッチしたキーワードリスト
                例：["AI", "企業"]
        
        戻り値：
            int：スコア（0-100）
        
        使用例：
            score = ArticleScorer.calculate_score(article, ["AI"])
            print(f"スコア：{score}")
        """
```

---

### 3.4 KeywordExtractor クラス

```python
class KeywordExtractor:
    """
    記事から重要キーワードを自動抽出
    """

    @staticmethod
    def extract(article: UniversalArticle) -> List[str]:
        """
        記事から重要キーワードを抽出
        
        抽出方法：
        - 設定済みキーワードマッピングから検索
        - タイトル・本文内の出現をチェック
        
        パラメータ：
            article (UniversalArticle)：キーワード抽出対象
        
        戻り値：
            List[str]：抽出されたキーワードリスト
                例：["AI", "OpenAI", "言語モデル"]
        
        使用例：
            keywords = KeywordExtractor.extract(article)
        """
```

---

### 3.5 Deduplicator クラス

```python
class Deduplicator:
    """
    同じニュースの複数報道を統合
    """

    @staticmethod
    def deduplicate(articles: List[UniversalArticle]) -> List[UniversalArticle]:
        """
        重複記事を検出・除外
        
        判定方法：
        - タイトルの正規化を比較
        - 数字を統一
        - 類似度判定
        
        パラメータ：
            articles：重複チェック対象
        
        戻り値：
            List[UniversalArticle]：重複排除済み記事
        
        使用例：
            dedup = Deduplicator.deduplicate(articles)
            print(f"重複：{len(articles) - len(dedup)} 件")
        """
```

---

### 3.6 Ranker クラス

```python
class Ranker:
    """
    記事をカテゴリ別にランキング
    """

    @staticmethod
    def rank_by_category(articles: List[UniversalArticle]) -> Dict[str, List[UniversalArticle]]:
        """
        カテゴリ別に記事をランク付け
        
        ランキング基準：
        1. relevance_score（降順）
        2. published_at（新しい順）
        
        パラメータ：
            articles：ランク対象の記事
        
        戻り値：
            Dict[str, List]：{
                "AI": [1位, 2位, ...],
                "決算": [1位, 2位, ...],
                ...
            }
        
        使用例：
            ranking = Ranker.rank_by_category(articles)
            for category, items in ranking.items():
                print(f"{category}: {len(items)} 件")
        """
```

---

## 4️⃣ LLM API

### 4.1 AdaptiveLLMRouter クラス

```python
class AdaptiveLLMRouter:
    """
    カテゴリ・難易度に応じて最適な LLM を自動選択
    """

    async def summarize(
        self,
        article: UniversalArticle,
        category: str
    ) -> Tuple[str, str]:
        """
        記事を要約（最適な API で自動実行）
        
        API 選択ロジック：
        - "AI" → Claude（高精度）
        - "決算" → ChatGPT（数値分析得意）
        - "科学" → Claude（論文対応）
        - その他 → Gemini（低コスト）
        
        パラメータ：
            article (UniversalArticle)：要約対象
            category (str)：記事カテゴリ
        
        戻り値：
            Tuple[str, str]：(要約テキスト, 使用した API名)
                例：("OpenAI は GPT-5 を発表...", "claude")
        
        例外：
            Exception：全 API が失敗
        
        使用例：
            summary, api_name = await router.summarize(article, "AI")
            print(f"使用 API：{api_name}")
        """

    async def summarize_with_fallback(
        self,
        article: UniversalArticle,
        category: str
    ) -> Tuple[str, str]:
        """
        フェイルオーバー対応の要約生成
        
        動作：
        1. メイン API で試行
        2. 失敗したら次の API で試行
        3. 全て失敗したらキャッシュから返す
        
        パラメータ：
            article (UniversalArticle)
            category (str)
        
        戻り値：
            Tuple[str, str]：(要約, API名)
        
        使用例：
            summary, api = await router.summarize_with_fallback(article, "AI")
        """
```

### 4.2 ClaudeClient クラス

```python
class ClaudeClient:
    """
    Claude API ラッパー
    """

    async def summarize(
        self,
        text: str,
        max_tokens: int = 200
    ) -> str:
        """
        テキストを要約
        
        パラメータ：
            text (str)：要約対象テキスト
            max_tokens (int)：最大トークン数
        
        戻り値：
            str：生成された要約
        
        使用例：
            summary = await claude.summarize(article_text)
        """
```

---

## 5️⃣ Output API

### 5.1 HTMLGenerator クラス

```python
class HTMLGenerator:
    """
    UniversalArticle を HTML に変換
    """

    @staticmethod
    def generate(
        articles: List[UniversalArticle],
        date: str
    ) -> str:
        """
        記事リストを新聞風 HTML に変換
        
        HTML 特性：
        - レスポンシブデザイン（iPad 対応）
        - 日本語フォント対応
        - ダークモード対応（将来）
        
        パラメータ：
            articles (List[UniversalArticle])：変換対象記事
            date (str)：日付（"2026-01-29"）
        
        戻り値：
            str：完成した HTML
        
        使用例：
            html = HTMLGenerator.generate(articles, "2026-01-29")
            with open("news.html", "w") as f:
                f.write(html)
        """
```

### 5.2 MarkdownGenerator クラス

```python
class MarkdownGenerator:
    """
    UniversalArticle を Markdown に変換
    """

    @staticmethod
    def generate(
        articles: List[UniversalArticle],
        date: str
    ) -> str:
        """
        記事リストを Markdown に変換
        
        パラメータ：
            articles (List[UniversalArticle])
            date (str)：日付
        
        戻り値：
            str：Markdown テキスト
        
        使用例：
            md = MarkdownGenerator.generate(articles, date)
        """
```

### 5.3 NotionUploader クラス

```python
class NotionUploader:
    """
    Notion データベースへの投稿
    """

    async def upload_articles(
        self,
        articles: List[UniversalArticle]
    ) -> bool:
        """
        記事リストを Notion に投稿
        
        パラメータ：
            articles (List[UniversalArticle])
        
        戻り値：
            bool：成功なら True
        
        例外：
            Exception：投稿失敗
        
        使用例：
            success = await uploader.upload_articles(articles)
        """
```

---

## 6️⃣ メイン処理 API

### 6.1 main() 関数

```python
async def main():
    """
    Digest Daily のメイン処理
    
    フロー：
    1. データ取得
    2. 正規化・フィルタリング
    3. スコアリング・要約生成
    4. HTML/Markdown/Notion に出力
    
    使用例：
        asyncio.run(main())
    """
```

---

## 7️⃣ エラーコード定義

```python
【カスタム例外】

class NewsSourceError(Exception):
    """ニュースソース取得エラー"""

class NormalizationError(Exception):
    """データ正規化エラー"""

class LLMError(Exception):
    """LLM 処理エラー"""

class OutputError(Exception):
    """出力処理エラー"""

【エラーハンドリング例】

try:
    articles = await fetcher.fetch_all()
except NewsSourceError as e:
    logger.error(f"データ取得失敗：{e}")
    # 他のソースは継続
except Exception as e:
    logger.error(f"予期しないエラー：{e}")
```

---

## 8️⃣ データモデル（再掲）

```python
@dataclass
class UniversalArticle:
    # 【必須】
    id: str                          # 記事一意 ID
    title: str                       # タイトル
    source_url: str                  # 元記事 URL
    source_name: str                 # ソース名
    published_at: datetime           # 公開日時
    fetched_at: datetime             # 取得日時
    source_type: str                 # ソース種別
    category: str                    # カテゴリ
    
    # 【処理後】
    summary: Optional[str] = None    # 要約
    keywords: Optional[List[str]] = None  # キーワード
    relevance_score: Optional[int] = None  # 0-100 スコア
```

---

## 9️⃣ 利用例：フル パイプライン

```python
# src/main.py の使用例

import asyncio
from src.data_sources.newsapi_source import NewsAPISource
from src.llm.router import AdaptiveLLMRouter
from src.outputs.html_generator import HTMLGenerator

async def main():
    # 1. データ取得
    fetcher = DataFetcher()
    articles = await fetcher.fetch_all()
    print(f"✅ {len(articles)} 件取得")
    
    # 2. フィルタリング
    filtered = ArticleFilter.filter_articles(articles)
    print(f"✅ {len(filtered)} 件フィルター通過")
    
    # 3. スコアリング
    for article in filtered:
        score = ArticleScorer.calculate_score(article, article.category)
        article.relevance_score = score
    
    # 4. 要約生成
    router = AdaptiveLLMRouter()
    for article in filtered:
        summary, api = await router.summarize(article, article.category)
        article.summary = summary
        print(f"✅ {api} で要約生成")
    
    # 5. HTML 出力
    html = HTMLGenerator.generate(filtered, "2026-01-29")
    with open("news/2026-01-29.html", "w") as f:
        f.write(html)
    
    print("✅ 完成！")

if __name__ == '__main__':
    asyncio.run(main())
```

---

**これがシステム内部の API 仕様です！**
