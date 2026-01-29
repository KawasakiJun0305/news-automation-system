"""
UniversalArticle - 統一記事データモデル

全ニュースソースを統一フォーマットに変換するためのデータクラス
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
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
        source_name="TechCrunch",
        published_at=datetime.now(timezone.utc),
        fetched_at=datetime.now(timezone.utc),
        source_type="newsapi",
        category="AI"
    )
    """

    # =====================================
    # 【コア情報】全ソースで必須
    # =====================================
    id: str                           # 一意識別子（UUID）
    title: str                        # 記事タイトル
    source_url: str                   # 元記事へのリンク
    source_name: str                  # ソース名（"NewsAPI", "日経新聞" など）
    published_at: datetime            # 記事の公開日時（UTC）
    fetched_at: datetime              # システムが記事を取得した日時（UTC）

    # =====================================
    # 【分類情報】カテゴリ・ソースタイプ
    # =====================================
    source_type: str                  # ソースの種類
                                      # "newsapi" | "rss" | "edinet" | "arxiv"
    category: str = "unknown"         # カテゴリ（後で自動判定）
                                      # "AI" | "決算" | "科学" | "モノづくり" | "ボードゲーム" | "unknown"

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
    original_data: Optional[Dict[str, Any]] = None  # 元のソースからのデータ（参照用）

    # =====================================
    # 【ソース固有情報】オプション
    # =====================================
    authors: Optional[List[str]] = None     # 著者（論文の場合など）
    language: str = "ja"                    # 言語（デフォルト：日本語）
    region: str = "JP"                      # 地域（デフォルト：日本）
    description: Optional[str] = None       # 記事の説明文
    content: Optional[str] = None           # 記事本文（取得できる場合）
    image_url: Optional[str] = None         # 画像URL（サムネイル等）

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
        # スコア範囲のバリデーション
        if self.relevance_score is not None:
            if not (0 <= self.relevance_score <= 100):
                raise ValueError(
                    f"relevance_score は 0-100 の範囲で指定してください（現在値: {self.relevance_score}）"
                )

        if self.credibility_score is not None:
            if not (0 <= self.credibility_score <= 100):
                raise ValueError(
                    f"credibility_score は 0-100 の範囲で指定してください（現在値: {self.credibility_score}）"
                )

        # 必須フィールドのバリデーション
        if not self.id:
            raise ValueError("id は必須です")

        if not self.title:
            raise ValueError("title は必須です")

        if not self.source_url:
            raise ValueError("source_url は必須です")

        # 日時のタイムゾーン確認（警告のみ）
        if self.published_at.tzinfo is None:
            import warnings
            warnings.warn(
                f"published_at にタイムゾーン情報がありません: {self.published_at}",
                UserWarning
            )

        if self.fetched_at.tzinfo is None:
            import warnings
            warnings.warn(
                f"fetched_at にタイムゾーン情報がありません: {self.fetched_at}",
                UserWarning
            )

    def validate(self) -> bool:
        """
        記事データが正しいか検証

        戻り値:
            bool: データが有効なら True、無効なら False
        """
        try:
            # 必須フィールドチェック
            if not self.id or not self.title or not self.source_url:
                return False

            # スコア範囲チェック
            if self.relevance_score is not None:
                if not (0 <= self.relevance_score <= 100):
                    return False

            if self.credibility_score is not None:
                if not (0 <= self.credibility_score <= 100):
                    return False

            # 日付の妥当性チェック
            now = datetime.now(timezone.utc)

            # 未来の日付は不正（ただし、多少の時差を許容: 1時間）
            if self.published_at > now + timedelta(hours=1):
                return False

            # 取得日時 < 公開日時 は不正
            if self.fetched_at < self.published_at:
                return False

            return True

        except Exception:
            return False

    def to_dict(self) -> Dict[str, Any]:
        """
        辞書形式に変換

        戻り値:
            Dict[str, Any]: 辞書形式のデータ
        """
        return {
            'id': self.id,
            'title': self.title,
            'source_url': self.source_url,
            'source_name': self.source_name,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'fetched_at': self.fetched_at.isoformat() if self.fetched_at else None,
            'source_type': self.source_type,
            'category': self.category,
            'summary': self.summary,
            'keywords': self.keywords,
            'relevance_score': self.relevance_score,
            'credibility_score': self.credibility_score,
            'original_data': self.original_data,
            'authors': self.authors,
            'language': self.language,
            'region': self.region,
            'description': self.description,
            'content': self.content,
            'image_url': self.image_url,
            'is_cached': self.is_cached,
            'is_duplicate': self.is_duplicate
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UniversalArticle':
        """
        辞書形式から UniversalArticle を生成

        パラメータ:
            data (Dict[str, Any]): 辞書形式のデータ

        戻り値:
            UniversalArticle: インスタンス
        """
        # 日時文字列を datetime に変換
        if isinstance(data.get('published_at'), str):
            data['published_at'] = datetime.fromisoformat(data['published_at'])

        if isinstance(data.get('fetched_at'), str):
            data['fetched_at'] = datetime.fromisoformat(data['fetched_at'])

        return cls(**data)

    def __repr__(self) -> str:
        """文字列表現"""
        return (
            f"UniversalArticle(id={self.id[:8]}..., "
            f"title='{self.title[:30]}...', "
            f"source={self.source_name}, "
            f"category={self.category})"
        )
