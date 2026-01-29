"""
ClaudeClient のユニットテスト
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from src.llm.claude_client import ClaudeClient


class TestClaudeClient:
    """ClaudeClient クラスのテストスイート"""

    @patch('anthropic.Anthropic')
    def test_init_with_api_key(self, mock_anthropic):
        """API キーを指定して初期化できるか"""
        api_key = "test_api_key_12345"
        client = ClaudeClient(api_key=api_key)

        assert client.api_key == api_key
        assert client.model == "claude-sonnet-4-5-20250929"

    @patch('anthropic.Anthropic')
    def test_init_with_custom_model(self, mock_anthropic):
        """カスタムモデルを指定して初期化できるか"""
        api_key = "test_api_key"
        model = "claude-opus-4-5-20251101"
        client = ClaudeClient(api_key=api_key, model=model)

        assert client.model == model

    @patch('anthropic.Anthropic')
    def test_init_with_env_variable(self, mock_anthropic):
        """環境変数から API キーを読み込めるか"""
        with patch.dict(os.environ, {'CLAUDE_API_KEY': 'env_api_key'}):
            client = ClaudeClient()
            assert client.api_key == 'env_api_key'

    def test_init_without_api_key_raises_error(self):
        """API キーが設定されていない場合にエラーが発生するか"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="CLAUDE_API_KEY が設定されていません"):
                ClaudeClient()

    @patch('anthropic.Anthropic')
    def test_summarize_validates_text(self, mock_anthropic):
        """空のテキストでエラーが発生するか"""
        client = ClaudeClient(api_key="test_key")

        with pytest.raises(ValueError, match="text は空にできません"):
            client.summarize("")

        with pytest.raises(ValueError, match="text は空にできません"):
            client.summarize("   ")

    @patch('anthropic.Anthropic')
    def test_summarize_success_japanese(self, mock_anthropic):
        """日本語の要約が成功するか"""
        # モックレスポンスを設定
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="これはテストの要約です。")]
        mock_client.messages.create.return_value = mock_message

        # テスト実行
        client = ClaudeClient(api_key="test_key")
        summary = client.summarize("これはテスト記事です。", language="ja")

        # 検証
        assert summary == "これはテストの要約です。"
        mock_client.messages.create.assert_called_once()

        # プロンプトに日本語の指示が含まれているか確認
        call_args = mock_client.messages.create.call_args
        messages = call_args[1]['messages']
        assert "日本語" in messages[0]['content']

    @patch('anthropic.Anthropic')
    def test_summarize_success_english(self, mock_anthropic):
        """英語の要約が成功するか"""
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="This is a test summary.")]
        mock_client.messages.create.return_value = mock_message

        client = ClaudeClient(api_key="test_key")
        summary = client.summarize("This is a test article.", language="en")

        assert summary == "This is a test summary."

        # プロンプトに英語の指示が含まれているか確認
        call_args = mock_client.messages.create.call_args
        messages = call_args[1]['messages']
        assert "Please summarize" in messages[0]['content']

    @patch('anthropic.Anthropic')
    def test_summarize_with_custom_max_tokens(self, mock_anthropic):
        """max_tokens を指定できるか"""
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="要約")]
        mock_client.messages.create.return_value = mock_message

        client = ClaudeClient(api_key="test_key")
        client.summarize("テスト", max_tokens=500)

        # max_tokens が正しく渡されているか確認
        call_args = mock_client.messages.create.call_args
        assert call_args[1]['max_tokens'] == 500

    @patch('anthropic.Anthropic')
    def test_summarize_api_error(self, mock_anthropic):
        """API エラーが発生した場合の処理"""
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API Error")

        client = ClaudeClient(api_key="test_key")

        with pytest.raises(Exception, match="API Error"):
            client.summarize("テスト記事")

    @patch('anthropic.Anthropic')
    def test_batch_summarize_success(self, mock_anthropic):
        """複数テキストの一括要約が成功するか"""
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        # 各呼び出しで異なる要約を返すようにモックを設定
        mock_message1 = MagicMock()
        mock_message1.content = [MagicMock(text="要約1")]

        mock_message2 = MagicMock()
        mock_message2.content = [MagicMock(text="要約2")]

        mock_client.messages.create.side_effect = [mock_message1, mock_message2]

        client = ClaudeClient(api_key="test_key")
        summaries = client.batch_summarize(["テキスト1", "テキスト2"])

        assert len(summaries) == 2
        assert summaries[0] == "要約1"
        assert summaries[1] == "要約2"
        assert mock_client.messages.create.call_count == 2

    @patch('anthropic.Anthropic')
    def test_batch_summarize_empty_list(self, mock_anthropic):
        """空のリストを渡した場合"""
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        client = ClaudeClient(api_key="test_key")
        summaries = client.batch_summarize([])

        assert summaries == []
        mock_client.messages.create.assert_not_called()

    @patch('anthropic.Anthropic')
    def test_summarize_multiple_articles_success(self, mock_anthropic):
        """複数記事の要約が成功するか"""
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        mock_message1 = MagicMock()
        mock_message1.content = [MagicMock(text="記事1の要約")]

        mock_message2 = MagicMock()
        mock_message2.content = [MagicMock(text="記事2の要約")]

        mock_client.messages.create.side_effect = [mock_message1, mock_message2]

        client = ClaudeClient(api_key="test_key")

        articles = [
            {"title": "タイトル1", "description": "内容1"},
            {"title": "タイトル2", "content": "内容2"}
        ]

        summarized = client.summarize_multiple(articles)

        assert len(summarized) == 2
        assert summarized[0]['summary'] == "記事1の要約"
        assert summarized[1]['summary'] == "記事2の要約"

    @patch('anthropic.Anthropic')
    def test_summarize_multiple_articles_with_missing_content(self, mock_anthropic):
        """コンテンツがない記事をスキップするか"""
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="要約")]
        mock_client.messages.create.return_value = mock_message

        client = ClaudeClient(api_key="test_key")

        articles = [
            {"title": "タイトル1", "description": "内容1"},
            {"title": "タイトル2"},  # コンテンツなし
            {"title": "タイトル3", "description": "内容3"}
        ]

        summarized = client.summarize_multiple(articles)

        assert len(summarized) == 3
        assert summarized[0]['summary'] == "要約"
        assert summarized[1]['summary'] == ""  # スキップされた記事
        assert summarized[2]['summary'] == "要約"

        # コンテンツがある記事のみAPI呼び出しが行われる
        assert mock_client.messages.create.call_count == 2


class TestClaudeClientIntegration:
    """
    統合テスト（実際の API を呼び出す）

    注意: これらのテストは実際の API キーが必要です
    CI/CD では @pytest.mark.skip でスキップすることを推奨
    """

    @pytest.mark.skip(reason="実際の API を使用するため、手動実行時のみ有効化")
    def test_real_api_summarize(self):
        """実際の Claude API で要約を生成（手動テスト用）"""
        api_key = os.getenv('CLAUDE_API_KEY')
        if not api_key:
            pytest.skip("CLAUDE_API_KEY が設定されていません")

        client = ClaudeClient(api_key=api_key)

        text = """
        OpenAI は本日、次世代言語モデル「GPT-5」をプレビュー公開しました。
        従来の GPT-4 比で推論精度が 35% 向上し、複雑な数学問題やコード生成でも高い精度を実現しています。
        3 月の正式リリースが予定されています。
        """

        summary = client.summarize(text, language="ja")

        # 基本的な検証
        assert len(summary) > 0
        assert isinstance(summary, str)

    @pytest.mark.skip(reason="実際の API を使用するため、手動実行時のみ有効化")
    def test_real_api_batch_summarize(self):
        """実際の Claude API で複数要約を生成（手動テスト用）"""
        api_key = os.getenv('CLAUDE_API_KEY')
        if not api_key:
            pytest.skip("CLAUDE_API_KEY が設定されていません")

        client = ClaudeClient(api_key=api_key)

        texts = [
            "Python は、汎用プログラミング言語です。",
            "AI 技術が急速に発展しています。"
        ]

        summaries = client.batch_summarize(texts, language="ja")

        assert len(summaries) == 2
        assert all(len(s) > 0 for s in summaries)
