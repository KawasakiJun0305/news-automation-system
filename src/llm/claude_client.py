"""
Claude API を使って要約生成するモジュール
"""

import os
from typing import Optional, List, Dict
import anthropic


class ClaudeClient:
    """
    Claude API を使って要約生成するクラス
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-5-20250929"):
        """
        ClaudeClient を初期化

        パラメータ:
            api_key (Optional[str]): Claude API キー。指定しない場合は環境変数から取得
            model (str): 使用する Claude モデル（デフォルト: claude-sonnet-4-5-20250929）
        """
        self.api_key = api_key or os.getenv('CLAUDE_API_KEY')
        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY が設定されていません。.env ファイルを確認してください。")

        self.model = model
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def summarize(
        self,
        text: str,
        max_tokens: int = 300,
        language: str = "ja"
    ) -> str:
        """
        テキストを要約する

        パラメータ:
            text (str): 要約する元テキスト
            max_tokens (int): 最大トークン数（デフォルト: 300）
            language (str): 要約言語（'ja': 日本語, 'en': 英語）

        戻り値:
            str: 生成された要約

        例外:
            ValueError: テキストが空の場合
            anthropic.APIError: API 呼び出しに失敗した場合
        """

        if not text or not text.strip():
            raise ValueError("text は空にできません")

        # 言語に応じたプロンプトを作成
        if language == "ja":
            prompt = f"""以下のニュース記事を、簡潔な日本語で2-3文の要約にしてください。
重要なポイントだけを抽出し、読者が記事の内容をすぐに理解できるようにしてください。

記事：
{text}

要約："""
        else:
            prompt = f"""Please summarize the following news article in 2-3 concise sentences.
Extract only the key points so readers can quickly understand the content.

Article:
{text}

Summary:"""

        try:
            print(f"🤖 Claude に要約をリクエスト中... (モデル: {self.model})")

            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # レスポンスからテキストを抽出
            summary = message.content[0].text

            print(f"✅ 要約生成完了（{len(summary)} 文字）")

            return summary.strip()

        except anthropic.APIError as e:
            print(f"❌ Claude API エラー: {e}")
            raise

        except Exception as e:
            print(f"❌ 予期しないエラー: {e}")
            raise

    def summarize_multiple(
        self,
        articles: List[Dict[str, str]],
        max_tokens: int = 300,
        language: str = "ja"
    ) -> List[Dict[str, str]]:
        """
        複数の記事を要約する

        パラメータ:
            articles (List[Dict]): 記事のリスト。各記事は {'title': ..., 'content': ...} の形式
            max_tokens (int): 各要約の最大トークン数
            language (str): 要約言語

        戻り値:
            List[Dict]: 要約が追加された記事のリスト。各記事に 'summary' フィールドが追加される
        """

        if not articles:
            return []

        print(f"📚 {len(articles)} 件の記事を要約中...")

        summarized_articles = []

        for i, article in enumerate(articles, 1):
            print(f"\n進捗: {i}/{len(articles)}")

            # 記事のタイトルと内容を結合
            title = article.get('title', '')
            content = article.get('description', '') or article.get('content', '')

            if not content:
                print(f"⚠️ 記事 {i} にコンテンツがありません。スキップします。")
                article['summary'] = ""
                summarized_articles.append(article)
                continue

            # タイトルと内容を結合してテキストを作成
            full_text = f"タイトル: {title}\n\n{content}"

            try:
                # 要約を生成
                summary = self.summarize(full_text, max_tokens=max_tokens, language=language)

                # 要約を記事に追加
                article['summary'] = summary
                summarized_articles.append(article)

            except Exception as e:
                print(f"❌ 記事 {i} の要約に失敗: {e}")
                article['summary'] = ""
                summarized_articles.append(article)

        print(f"\n✅ {len(summarized_articles)} 件の要約が完了しました")

        return summarized_articles

    def batch_summarize(
        self,
        texts: List[str],
        max_tokens: int = 300,
        language: str = "ja"
    ) -> List[str]:
        """
        複数のテキストを一括要約する（シンプル版）

        パラメータ:
            texts (List[str]): 要約するテキストのリスト
            max_tokens (int): 各要約の最大トークン数
            language (str): 要約言語

        戻り値:
            List[str]: 要約のリスト
        """

        if not texts:
            return []

        print(f"📚 {len(texts)} 件のテキストを要約中...")

        summaries = []

        for i, text in enumerate(texts, 1):
            print(f"進捗: {i}/{len(texts)}")

            try:
                summary = self.summarize(text, max_tokens=max_tokens, language=language)
                summaries.append(summary)

            except Exception as e:
                print(f"❌ テキスト {i} の要約に失敗: {e}")
                summaries.append("")

        return summaries
