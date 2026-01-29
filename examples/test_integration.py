"""
NewsAPI + Claude の統合テスト

実際のニュース記事を NewsAPI から取得し、Claude で要約を生成します。

実行方法:
    python examples/test_integration.py
"""

import sys
import os
from pathlib import Path

# Windows環境でUTF-8を使用するための設定
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# プロジェクトのルートディレクトリを sys.path に追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.data_sources.newsapi_source import NewsAPISource
from src.llm.claude_client import ClaudeClient


def main():
    """メイン処理"""

    # .env ファイルから環境変数を読み込む
    load_dotenv()

    print("=" * 70)
    print("NewsAPI + Claude 統合テスト")
    print("=" * 70)
    print()

    try:
        # 1. NewsAPISource を初期化
        print("【ステップ 1】NewsAPI からニュース記事を取得")
        print("-" * 70)
        news_source = NewsAPISource()
        print("✅ NewsAPISource を初期化しました")
        print()

        # 2. ニュース記事を取得（英語）
        keyword = "Artificial Intelligence"
        print(f"🔍 キーワード: '{keyword}' で記事を検索中...")
        articles = news_source.fetch_articles(keyword, language="en", page_size=3)

        if not articles:
            print("❌ 記事が取得できませんでした")
            return

        print(f"✅ {len(articles)} 件の記事を取得しました")
        print()

        # 取得した記事を表示
        print("【取得した記事一覧】")
        print("-" * 70)
        for i, article in enumerate(articles, 1):
            print(f"\n記事 {i}:")
            print(f"  タイトル: {article.get('title', 'N/A')}")
            print(f"  ソース: {article.get('source', {}).get('name', 'N/A')}")
            print(f"  公開日: {article.get('publishedAt', 'N/A')}")
            print(f"  説明: {article.get('description', 'N/A')[:100]}...")

        print()
        print("=" * 70)
        print()

        # 3. ClaudeClient を初期化
        print("【ステップ 2】Claude で記事を要約")
        print("-" * 70)
        claude_client = ClaudeClient()
        print(f"✅ ClaudeClient を初期化しました（モデル: {claude_client.model}）")
        print()

        # 4. 記事を要約
        summarized_articles = claude_client.summarize_multiple(
            articles,
            max_tokens=200,
            language="en"
        )

        # 5. 結果を表示
        print()
        print("=" * 70)
        print("【要約結果】")
        print("=" * 70)

        for i, article in enumerate(summarized_articles, 1):
            print(f"\n記事 {i}:")
            print(f"  タイトル: {article.get('title', 'N/A')}")
            print(f"  ソース: {article.get('source', {}).get('name', 'N/A')}")
            print(f"  URL: {article.get('url', 'N/A')}")
            print()
            print(f"  【元の説明】")
            print(f"  {article.get('description', 'N/A')}")
            print()
            print(f"  【Claude による要約】")
            print(f"  {article.get('summary', 'N/A')}")
            print()
            print("-" * 70)

        print()
        print("=" * 70)
        print()
        print("✅ 統合テストが正常に完了しました！")
        print()
        print("📊 結果:")
        print(f"  - 取得した記事数: {len(articles)} 件")
        print(f"  - 要約生成成功: {sum(1 for a in summarized_articles if a.get('summary'))} 件")
        print()

        # 6. 日本語の記事でもテスト
        print("=" * 70)
        print("【ボーナステスト】日本語記事の取得と要約")
        print("-" * 70)

        keyword_ja = "Python"
        print(f"🔍 キーワード: '{keyword_ja}' で日本語記事を検索中...")
        articles_ja = news_source.fetch_articles(keyword_ja, language="ja", page_size=2)

        if articles_ja:
            print(f"✅ {len(articles_ja)} 件の日本語記事を取得しました")
            print()

            summarized_ja = claude_client.summarize_multiple(
                articles_ja,
                max_tokens=200,
                language="ja"
            )

            print("【日本語記事の要約結果】")
            print("-" * 70)

            for i, article in enumerate(summarized_ja, 1):
                print(f"\n記事 {i}:")
                print(f"  タイトル: {article.get('title', 'N/A')}")
                print(f"  要約: {article.get('summary', 'N/A')}")
                print()
        else:
            print("⚠️ 日本語記事が取得できませんでした（無料プランの制限の可能性）")

        print()
        print("=" * 70)
        print("✅ 全ての統合テストが完了しました！")

    except ValueError as e:
        print(f"❌ エラー: {e}")
        print()
        print("💡 ヒント:")
        print("  .env ファイルに NEWSAPI_KEY と CLAUDE_API_KEY が設定されているか確認してください。")
        sys.exit(1)

    except Exception as e:
        print(f"❌ 予期しないエラーが発生しました: {e}")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
