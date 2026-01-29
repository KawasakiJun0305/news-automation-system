"""
NewsAPISource のユニットテスト
"""

import pytest
import os
from unittest.mock import Mock, patch
from src.data_sources.newsapi_source import NewsAPISource


class TestNewsAPISource:
    """NewsAPISource クラスのテストスイート"""

    def test_init_with_api_key(self):
        """API キーを指定して初期化できるか"""
        api_key = "test_api_key_12345"
        source = NewsAPISource(api_key=api_key)

        assert source.api_key == api_key
        assert source.base_url == 'https://newsapi.org/v2/everything'

    def test_init_with_env_variable(self):
        """環境変数から API キーを読み込めるか"""
        with patch.dict(os.environ, {'NEWSAPI_KEY': 'env_api_key'}):
            source = NewsAPISource()
            assert source.api_key == 'env_api_key'

    def test_init_without_api_key_raises_error(self):
        """API キーが設定されていない場合にエラーが発生するか"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="NEWSAPI_KEY が設定されていません"):
                NewsAPISource()

    def test_fetch_articles_validates_keyword(self):
        """空のキーワードでエラーが発生するか"""
        source = NewsAPISource(api_key="test_key")

        with pytest.raises(ValueError, match="keyword は空にできません"):
            source.fetch_articles("")

    def test_fetch_articles_validates_page_size(self):
        """無効な page_size でエラーが発生するか"""
        source = NewsAPISource(api_key="test_key")

        with pytest.raises(ValueError, match="page_size は 1〜100 の範囲で指定してください"):
            source.fetch_articles("AI", page_size=0)

        with pytest.raises(ValueError, match="page_size は 1〜100 の範囲で指定してください"):
            source.fetch_articles("AI", page_size=101)

    @patch('requests.get')
    def test_fetch_articles_success(self, mock_get):
        """記事の取得が成功するか"""
        # モックレスポンスを設定
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'ok',
            'totalResults': 2,
            'articles': [
                {
                    'title': 'Test Article 1',
                    'description': 'Description 1',
                    'url': 'https://example.com/1',
                    'publishedAt': '2026-01-29T10:00:00Z',
                    'source': {'name': 'Test Source'}
                },
                {
                    'title': 'Test Article 2',
                    'description': 'Description 2',
                    'url': 'https://example.com/2',
                    'publishedAt': '2026-01-29T11:00:00Z',
                    'source': {'name': 'Test Source'}
                }
            ]
        }
        mock_get.return_value = mock_response

        # テスト実行
        source = NewsAPISource(api_key="test_key")
        articles = source.fetch_articles("AI")

        # 検証
        assert len(articles) == 2
        assert articles[0]['title'] == 'Test Article 1'
        assert articles[1]['title'] == 'Test Article 2'

        # API が正しく呼ばれたか確認
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]['params']['q'] == 'AI'
        assert call_args[1]['params']['language'] == 'ja'

    @patch('requests.get')
    def test_fetch_articles_api_error(self, mock_get):
        """API がエラーを返した場合の処理"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'error',
            'message': 'API key is invalid'
        }
        mock_get.return_value = mock_response

        source = NewsAPISource(api_key="invalid_key")

        with pytest.raises(Exception, match="NewsAPI エラー: API key is invalid"):
            source.fetch_articles("AI")

    @patch('requests.get')
    def test_fetch_articles_http_error(self, mock_get):
        """HTTP エラーが発生した場合の処理"""
        import requests

        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_get.return_value = mock_response

        source = NewsAPISource(api_key="test_key")

        with pytest.raises(requests.exceptions.HTTPError):
            source.fetch_articles("AI")

    @patch('requests.get')
    def test_fetch_articles_timeout(self, mock_get):
        """タイムアウトが発生した場合の処理"""
        import requests

        mock_get.side_effect = requests.exceptions.Timeout()

        source = NewsAPISource(api_key="test_key")

        with pytest.raises(requests.exceptions.Timeout):
            source.fetch_articles("AI")

    @patch('requests.get')
    def test_fetch_top_headlines_success(self, mock_get):
        """トップヘッドラインの取得が成功するか"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'ok',
            'totalResults': 1,
            'articles': [
                {
                    'title': 'Top News',
                    'description': 'Breaking news',
                    'url': 'https://example.com/top',
                    'publishedAt': '2026-01-29T12:00:00Z',
                    'source': {'name': 'News Source'}
                }
            ]
        }
        mock_get.return_value = mock_response

        source = NewsAPISource(api_key="test_key")
        articles = source.fetch_top_headlines(country='jp')

        assert len(articles) == 1
        assert articles[0]['title'] == 'Top News'

        # API が正しく呼ばれたか確認
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]['params']['country'] == 'jp'


class TestNewsAPISourceIntegration:
    """
    統合テスト（実際の API を呼び出す）

    注意: これらのテストは実際の API キーが必要です
    CI/CD では @pytest.mark.skip でスキップすることを推奨
    """

    @pytest.mark.skip(reason="実際の API を使用するため、手動実行時のみ有効化")
    def test_real_api_fetch_articles(self):
        """実際の NewsAPI から記事を取得（手動テスト用）"""
        # 環境変数から API キーを取得
        api_key = os.getenv('NEWSAPI_KEY')
        if not api_key:
            pytest.skip("NEWSAPI_KEY が設定されていません")

        source = NewsAPISource(api_key=api_key)
        articles = source.fetch_articles("Python", page_size=5)

        # 基本的な検証
        assert len(articles) > 0
        assert 'title' in articles[0]
        assert 'url' in articles[0]
        assert 'publishedAt' in articles[0]

    @pytest.mark.skip(reason="実際の API を使用するため、手動実行時のみ有効化")
    def test_real_api_fetch_top_headlines(self):
        """実際の NewsAPI からトップヘッドラインを取得（手動テスト用）"""
        api_key = os.getenv('NEWSAPI_KEY')
        if not api_key:
            pytest.skip("NEWSAPI_KEY が設定されていません")

        source = NewsAPISource(api_key=api_key)
        articles = source.fetch_top_headlines(country='jp', page_size=5)

        assert len(articles) > 0
        assert 'title' in articles[0]
