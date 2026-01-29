"""
NewsAPI からニュース記事を取得するモジュール
"""

import requests
import os
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Optional

from src.models import UniversalArticle


class NewsAPISource:
    """
    NewsAPI からニュース記事を取得するクラス
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        NewsAPISource を初期化

        パラメータ:
            api_key (Optional[str]): NewsAPI キー。指定しない場合は環境変数から取得
        """
        self.api_key = api_key or os.getenv('NEWSAPI_KEY')
        if not self.api_key:
            raise ValueError("NEWSAPI_KEY が設定されていません。.env ファイルを確認してください。")

        self.base_url = 'https://newsapi.org/v2/everything'

    def fetch_articles(
        self,
        keyword: str,
        language: str = 'ja',
        page_size: int = 20,
        sort_by: str = 'publishedAt'
    ) -> List[Dict]:
        """
        キーワードでニュース記事を検索

        パラメータ:
            keyword (str): 検索キーワード（例: "AI", "Python"）
            language (str): 言語コード（デフォルト: 'ja' - 日本語）
            page_size (int): 取得する記事数（デフォルト: 20、最大: 100）
            sort_by (str): ソート順（'publishedAt', 'relevancy', 'popularity'）

        戻り値:
            List[Dict]: 記事のリスト。各記事は辞書形式。

        例外:
            requests.exceptions.RequestException: API リクエストに失敗した場合
        """

        # パラメータ検証
        if not keyword or not keyword.strip():
            raise ValueError("keyword は空にできません")

        if page_size < 1 or page_size > 100:
            raise ValueError("page_size は 1〜100 の範囲で指定してください")

        # API リクエストパラメータ
        params = {
            'q': keyword,
            'language': language,
            'pageSize': page_size,
            'sortBy': sort_by,
            'apiKey': self.api_key
        }

        try:
            print(f"📡 NewsAPI にリクエスト中: キーワード='{keyword}', 言語={language}")

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()  # HTTP エラーがあれば例外を発生

            data = response.json()

            # API のステータスを確認
            if data.get('status') != 'ok':
                error_message = data.get('message', '不明なエラー')
                raise Exception(f"NewsAPI エラー: {error_message}")

            articles = data.get('articles', [])
            total_results = data.get('totalResults', 0)

            print(f"✅ {keyword}: {len(articles)} 件取得（全 {total_results} 件中）")

            return articles

        except requests.exceptions.Timeout:
            print(f"❌ タイムアウト: NewsAPI への接続がタイムアウトしました")
            raise

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else 'unknown'
            print(f"❌ HTTP エラー ({status_code}): {e}")
            raise

        except requests.exceptions.RequestException as e:
            print(f"❌ リクエストエラー: {e}")
            raise

    def fetch_top_headlines(
        self,
        country: str = 'jp',
        category: Optional[str] = None,
        page_size: int = 20
    ) -> List[Dict]:
        """
        トップヘッドラインを取得（国別）

        パラメータ:
            country (str): 国コード（デフォルト: 'jp' - 日本）
            category (Optional[str]): カテゴリ（'business', 'technology', 'science' など）
            page_size (int): 取得する記事数（デフォルト: 20）

        戻り値:
            List[Dict]: 記事のリスト
        """

        url = 'https://newsapi.org/v2/top-headlines'

        params = {
            'country': country,
            'pageSize': page_size,
            'apiKey': self.api_key
        }

        if category:
            params['category'] = category

        try:
            print(f"📡 トップヘッドライン取得中: 国={country}")

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('status') != 'ok':
                error_message = data.get('message', '不明なエラー')
                raise Exception(f"NewsAPI エラー: {error_message}")

            articles = data.get('articles', [])

            print(f"✅ トップヘッドライン: {len(articles)} 件取得")

            return articles

        except requests.exceptions.RequestException as e:
            print(f"❌ エラーが発生しました: {e}")
            raise

    @staticmethod
    def normalize(newsapi_article: Dict) -> UniversalArticle:
        """
        NewsAPI の記事フォーマットを UniversalArticle に変換

        パラメータ:
            newsapi_article (dict): NewsAPI から返されたニュース記事

        戻り値:
            UniversalArticle: 統一フォーマットに変換された記事

        例:
            raw_article = {
                'source': {'name': 'TechCrunch'},
                'title': 'OpenAI releases GPT-5',
                'url': 'https://...',
                'publishedAt': '2026-01-29T08:00:00Z',
                'description': '...',
                'content': '...'
            }
            article = NewsAPISource.normalize(raw_article)
        """

        # ソース名を取得
        source_name = newsapi_article.get('source', {}).get('name', 'Unknown')

        # タイトルを取得
        title = newsapi_article.get('title', 'Untitled')

        # 公開日を datetime に変換
        published_at_str = newsapi_article.get('publishedAt', '')
        try:
            if published_at_str:
                # ISO 8601 形式の文字列を datetime に変換
                # 'Z' を '+00:00' に置き換えて UTC として扱う
                published_at = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
            else:
                # 公開日がない場合は現在時刻を使用
                published_at = datetime.now(timezone.utc)
        except (ValueError, TypeError):
            # パースに失敗した場合も現在時刻を使用
            published_at = datetime.now(timezone.utc)

        # 取得時刻（UTC）
        fetched_at = datetime.now(timezone.utc)

        # 一意 ID を生成（タイトル + ソース名のハッシュ）
        # 同じ記事なら同じIDになるようにする
        article_id = str(uuid.uuid5(
            uuid.NAMESPACE_DNS,
            f"{title}-{source_name}"
        ))

        # 言語を判定（簡易的）
        description = newsapi_article.get('description', '')
        content = newsapi_article.get('content', '')
        combined_text = f"{title} {description}"

        # 日本語文字が含まれているかチェック
        has_japanese = any('\u3000' <= c <= '\u9fff' or '\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff'
                          for c in combined_text)
        language = 'ja' if has_japanese else 'en'

        # UniversalArticle に変換
        return UniversalArticle(
            id=article_id,
            title=title,
            source_url=newsapi_article.get('url', ''),
            source_name=source_name,
            published_at=published_at,
            fetched_at=fetched_at,
            source_type='newsapi',
            category='unknown',  # 後でカテゴリ判定機能を追加
            description=description,
            content=content,
            image_url=newsapi_article.get('urlToImage'),
            language=language,
            original_data=newsapi_article  # 元データは保持しておく
        )

    @classmethod
    def fetch_and_normalize(
        cls,
        keyword: str,
        language: str = 'ja',
        page_size: int = 20,
        api_key: Optional[str] = None
    ) -> List[UniversalArticle]:
        """
        NewsAPI から記事を取得し、UniversalArticle に変換する便利メソッド

        パラメータ:
            keyword (str): 検索キーワード
            language (str): 言語コード
            page_size (int): 取得する記事数
            api_key (Optional[str]): API キー

        戻り値:
            List[UniversalArticle]: 正規化された記事のリスト
        """
        source = cls(api_key=api_key)
        raw_articles = source.fetch_articles(keyword, language=language, page_size=page_size)

        # 各記事を UniversalArticle に変換
        normalized_articles = [cls.normalize(article) for article in raw_articles]

        return normalized_articles
