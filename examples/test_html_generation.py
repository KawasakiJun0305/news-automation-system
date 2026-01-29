"""
HTML 生成機能のテスト

NewsAPI + Claude + HTML生成の完全な流れをテストし、
ブラウザでプレビューします。
"""

import os
import sys
from pathlib import Path

# Windows環境でのUTF-8出力を有効化
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# プロジェクトのルートディレクトリをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data_sources.newsapi_source import NewsAPISource
from src.llm.claude_client import ClaudeClient
from src.outputs.html_generator import HTMLGenerator
from src.models import UniversalArticle

# .env ファイルを読み込む
from dotenv import load_dotenv
load_dotenv()


def main():
    """
    HTML生成のテスト
    """

    print(f"\n{'='*60}")
    print(f"🚀 HTML生成機能のテスト")
    print(f"{'='*60}\n")

    try:
        # 1. NewsAPI から記事を取得 & UniversalArticle に変換
        print("📡 ステップ 1: 英語記事を取得中（日本語で要約予定）...")

        # 英語記事を取得（日本語で要約する）
        keyword = "AI"
        articles = NewsAPISource.fetch_and_normalize(
            keyword=keyword,
            language='en',
            page_size=10
        )

        print(f"✅ {len(articles)} 件の記事を取得しました\n")

        # 2. Claude で要約を生成
        print("🤖 ステップ 2: Claude で要約を生成中...")
        claude_client = ClaudeClient()

        for i, article in enumerate(articles, 1):
            print(f"\n進捗: {i}/{len(articles)} - {article.title[:50]}...")

            # 記事の内容を結合
            content_parts = [f"タイトル: {article.title}"]

            if article.description:
                content_parts.append(f"\n概要: {article.description}")

            if article.content:
                content_parts.append(f"\n本文: {article.content}")

            full_text = "\n".join(content_parts)

            # 内容が不足している場合はスキップ
            if len(full_text.strip()) < 50:
                print(f"⚠️ 内容が不足しています。スキップします。")
                article.summary = ""
                continue

            try:
                # Claude で要約を生成（日本語で）
                summary = claude_client.summarize(
                    text=full_text,
                    max_tokens=300,
                    language='ja'  # 日本語で要約
                )

                # UniversalArticle に要約を追加
                article.summary = summary
                print(f"✅ 要約完了")

            except Exception as e:
                print(f"❌ 要約失敗: {e}")
                article.summary = ""

        print(f"\n✅ 要約生成が完了しました\n")

        # 3. HTML を生成
        print("📄 ステップ 3: HTML を生成中...")

        html_generator = HTMLGenerator(output_dir="output")

        html_path = html_generator.generate_and_preview(
            articles=articles,
            title="AI News Daily",
            filename="ai_news_latest.html"
        )

        print(f"✅ HTML ファイルを生成しました: {html_path}")

        print(f"\n{'='*60}")
        print(f"🎉 テスト完了！")
        print(f"{'='*60}\n")

        print(f"📝 生成された HTML ファイル:")
        print(f"  {html_path}")
        print(f"\n💡 ブラウザでプレビューが表示されます")

    except KeyboardInterrupt:
        print("\n\n⚠️ ユーザーによって中断されました")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
