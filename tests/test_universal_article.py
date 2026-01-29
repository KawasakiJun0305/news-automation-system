"""
UniversalArticle のユニットテスト
"""

import pytest
from datetime import datetime, timezone
from src.models import UniversalArticle


class TestUniversalArticle:
    """UniversalArticle クラスのテストスイート"""

    def test_create_valid_article(self):
        """有効な記事データでインスタンスを作成できるか"""
        article = UniversalArticle(
            id="test-id-123",
            title="Test Article",
            source_url="https://example.com/article",
            source_name="Test Source",
            published_at=datetime(2026, 1, 29, 10, 0, 0, tzinfo=timezone.utc),
            fetched_at=datetime(2026, 1, 29, 12, 0, 0, tzinfo=timezone.utc),
            source_type="newsapi",
            category="AI"
        )

        assert article.id == "test-id-123"
        assert article.title == "Test Article"
        assert article.source_name == "Test Source"
        assert article.category == "AI"

    def test_required_fields_validation(self):
        """必須フィールドが空の場合にエラーが発生するか"""
        with pytest.raises(ValueError, match="id は必須です"):
            UniversalArticle(
                id="",
                title="Test",
                source_url="https://example.com",
                source_name="Test",
                published_at=datetime.now(timezone.utc),
                fetched_at=datetime.now(timezone.utc),
                source_type="newsapi"
            )

        with pytest.raises(ValueError, match="title は必須です"):
            UniversalArticle(
                id="test-id",
                title="",
                source_url="https://example.com",
                source_name="Test",
                published_at=datetime.now(timezone.utc),
                fetched_at=datetime.now(timezone.utc),
                source_type="newsapi"
            )

        with pytest.raises(ValueError, match="source_url は必須です"):
            UniversalArticle(
                id="test-id",
                title="Test",
                source_url="",
                source_name="Test",
                published_at=datetime.now(timezone.utc),
                fetched_at=datetime.now(timezone.utc),
                source_type="newsapi"
            )

    def test_relevance_score_validation(self):
        """relevance_score が範囲外の場合にエラーが発生するか"""
        with pytest.raises(ValueError, match="relevance_score は 0-100 の範囲で指定してください"):
            UniversalArticle(
                id="test-id",
                title="Test",
                source_url="https://example.com",
                source_name="Test",
                published_at=datetime.now(timezone.utc),
                fetched_at=datetime.now(timezone.utc),
                source_type="newsapi",
                relevance_score=101
            )

        with pytest.raises(ValueError, match="relevance_score は 0-100 の範囲で指定してください"):
            UniversalArticle(
                id="test-id",
                title="Test",
                source_url="https://example.com",
                source_name="Test",
                published_at=datetime.now(timezone.utc),
                fetched_at=datetime.now(timezone.utc),
                source_type="newsapi",
                relevance_score=-1
            )

    def test_credibility_score_validation(self):
        """credibility_score が範囲外の場合にエラーが発生するか"""
        with pytest.raises(ValueError, match="credibility_score は 0-100 の範囲で指定してください"):
            UniversalArticle(
                id="test-id",
                title="Test",
                source_url="https://example.com",
                source_name="Test",
                published_at=datetime.now(timezone.utc),
                fetched_at=datetime.now(timezone.utc),
                source_type="newsapi",
                credibility_score=150
            )

    def test_validate_method(self):
        """validate メソッドが正しく動作するか"""
        # 有効な記事
        valid_article = UniversalArticle(
            id="test-id",
            title="Test Article",
            source_url="https://example.com",
            source_name="Test",
            published_at=datetime(2026, 1, 28, 10, 0, 0, tzinfo=timezone.utc),
            fetched_at=datetime(2026, 1, 29, 10, 0, 0, tzinfo=timezone.utc),
            source_type="newsapi"
        )
        assert valid_article.validate() is True

        # スコアが範囲内
        valid_article_with_scores = UniversalArticle(
            id="test-id",
            title="Test Article",
            source_url="https://example.com",
            source_name="Test",
            published_at=datetime.now(timezone.utc),
            fetched_at=datetime.now(timezone.utc),
            source_type="newsapi",
            relevance_score=50,
            credibility_score=80
        )
        assert valid_article_with_scores.validate() is True

    def test_to_dict(self):
        """to_dict メソッドが正しく辞書に変換できるか"""
        article = UniversalArticle(
            id="test-id",
            title="Test Article",
            source_url="https://example.com",
            source_name="Test Source",
            published_at=datetime(2026, 1, 29, 10, 0, 0, tzinfo=timezone.utc),
            fetched_at=datetime(2026, 1, 29, 12, 0, 0, tzinfo=timezone.utc),
            source_type="newsapi",
            category="AI",
            summary="Test summary",
            keywords=["AI", "test"],
            relevance_score=75
        )

        data = article.to_dict()

        assert data['id'] == "test-id"
        assert data['title'] == "Test Article"
        assert data['category'] == "AI"
        assert data['summary'] == "Test summary"
        assert data['keywords'] == ["AI", "test"]
        assert data['relevance_score'] == 75
        assert isinstance(data['published_at'], str)
        assert isinstance(data['fetched_at'], str)

    def test_from_dict(self):
        """from_dict メソッドが正しくインスタンスを生成できるか"""
        data = {
            'id': 'test-id',
            'title': 'Test Article',
            'source_url': 'https://example.com',
            'source_name': 'Test Source',
            'published_at': '2026-01-29T10:00:00+00:00',
            'fetched_at': '2026-01-29T12:00:00+00:00',
            'source_type': 'newsapi',
            'category': 'AI',
            'summary': 'Test summary',
            'keywords': ['AI', 'test'],
            'relevance_score': 75,
            'credibility_score': 85,
            'language': 'ja',
            'region': 'JP',
            'is_cached': False,
            'is_duplicate': False
        }

        article = UniversalArticle.from_dict(data)

        assert article.id == 'test-id'
        assert article.title == 'Test Article'
        assert article.category == 'AI'
        assert article.summary == 'Test summary'
        assert article.keywords == ['AI', 'test']
        assert article.relevance_score == 75
        assert isinstance(article.published_at, datetime)
        assert isinstance(article.fetched_at, datetime)

    def test_repr(self):
        """__repr__ メソッドが適切な文字列表現を返すか"""
        article = UniversalArticle(
            id="test-id-123456789",
            title="This is a very long test article title that should be truncated",
            source_url="https://example.com",
            source_name="Test Source",
            published_at=datetime.now(timezone.utc),
            fetched_at=datetime.now(timezone.utc),
            source_type="newsapi",
            category="AI"
        )

        repr_str = repr(article)

        assert "UniversalArticle" in repr_str
        assert "test-id-" in repr_str  # ID の最初の部分
        assert "source=Test Source" in repr_str
        assert "category=AI" in repr_str

    def test_optional_fields(self):
        """オプショナルフィールドが None でも問題ないか"""
        article = UniversalArticle(
            id="test-id",
            title="Test Article",
            source_url="https://example.com",
            source_name="Test",
            published_at=datetime.now(timezone.utc),
            fetched_at=datetime.now(timezone.utc),
            source_type="newsapi"
        )

        assert article.summary is None
        assert article.keywords is None
        assert article.relevance_score is None
        assert article.credibility_score is None
        assert article.authors is None
        assert article.original_data is None

    def test_default_values(self):
        """デフォルト値が正しく設定されるか"""
        article = UniversalArticle(
            id="test-id",
            title="Test Article",
            source_url="https://example.com",
            source_name="Test",
            published_at=datetime.now(timezone.utc),
            fetched_at=datetime.now(timezone.utc),
            source_type="newsapi"
        )

        assert article.category == "unknown"
        assert article.language == "ja"
        assert article.region == "JP"
        assert article.is_cached is False
        assert article.is_duplicate is False


class TestUniversalArticleIntegration:
    """UniversalArticle の統合テスト"""

    def test_newsapi_normalization_workflow(self):
        """NewsAPI からの記事正規化ワークフローのテスト"""
        from src.data_sources.newsapi_source import NewsAPISource

        # NewsAPI の応答をシミュレート
        newsapi_article = {
            'source': {'name': 'TechCrunch'},
            'title': 'OpenAI Releases GPT-5',
            'url': 'https://techcrunch.com/article',
            'publishedAt': '2026-01-29T08:00:00Z',
            'description': 'OpenAI has announced the release of GPT-5.',
            'content': 'Full article content here...',
            'urlToImage': 'https://example.com/image.jpg'
        }

        # 正規化
        article = NewsAPISource.normalize(newsapi_article)

        # 検証
        assert isinstance(article, UniversalArticle)
        assert article.title == 'OpenAI Releases GPT-5'
        assert article.source_name == 'TechCrunch'
        assert article.source_type == 'newsapi'
        assert article.description == 'OpenAI has announced the release of GPT-5.'
        assert article.image_url == 'https://example.com/image.jpg'
        assert article.language == 'en'  # 英語記事として判定される
        assert article.original_data == newsapi_article
