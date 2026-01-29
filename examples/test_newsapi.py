"""
NewsAPISource の動作確認スクリプト

このスクリプトは、実際の NewsAPI から記事を取得して表示します。
実行前に .env ファイルに NEWSAPI_KEY を設定してください。

実行方法:
    python examples/test_newsapi.py
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


def main():
    """メイン処理"""

    # .env ファイルから環境変数を読み込む
    load_dotenv()

    print("=" * 60)
    print("NewsAPI 動作確認スクリプト")
    print("=" * 60)
    print()

    try:
        # NewsAPISource を初期化
        source = NewsAPISource()
        print(f"✅ NewsAPISource を初期化しました")
        print()

        # テスト 1: キーワード検索（日本語）
        print("【テスト 1】キーワード検索: 'AI'")
        print("-" * 60)
        articles_ai = source.fetch_articles("AI", language="ja", page_size=5)

        print(f"\n取得した記事数: {len(articles_ai)} 件\n")

        for i, article in enumerate(articles_ai, 1):
            print(f"記事 {i}:")
            print(f"  タイトル: {article.get('title', 'N/A')}")
            print(f"  ソース: {article.get('source', {}).get('name', 'N/A')}")
            print(f"  公開日時: {article.get('publishedAt', 'N/A')}")
            print(f"  URL: {article.get('url', 'N/A')}")
            print()

        print("=" * 60)
        print()

        # テスト 2: キーワード検索（英語）
        print("【テスト 2】キーワード検索: 'Python' (英語)")
        print("-" * 60)
        articles_python = source.fetch_articles("Python", language="en", page_size=3)

        print(f"\n取得した記事数: {len(articles_python)} 件\n")

        for i, article in enumerate(articles_python, 1):
            print(f"記事 {i}:")
            print(f"  タイトル: {article.get('title', 'N/A')}")
            print(f"  ソース: {article.get('source', {}).get('name', 'N/A')}")
            print(f"  説明: {article.get('description', 'N/A')[:100]}...")
            print()

        print("=" * 60)
        print()

        # テスト 3: トップヘッドライン（日本）
        print("【テスト 3】トップヘッドライン（日本）")
        print("-" * 60)
        headlines = source.fetch_top_headlines(country="jp", page_size=5)

        print(f"\n取得した記事数: {len(headlines)} 件\n")

        for i, article in enumerate(headlines, 1):
            print(f"記事 {i}:")
            print(f"  タイトル: {article.get('title', 'N/A')}")
            print(f"  ソース: {article.get('source', {}).get('name', 'N/A')}")
            print()

        print("=" * 60)
        print()
        print("✅ 全てのテストが正常に完了しました！")

    except ValueError as e:
        print(f"❌ エラー: {e}")
        print()
        print("💡 ヒント:")
        print("  .env ファイルに NEWSAPI_KEY が設定されているか確認してください。")
        print("  例: NEWSAPI_KEY=your_api_key_here")
        sys.exit(1)

    except Exception as e:
        print(f"❌ 予期しないエラーが発生しました: {e}")
        print()
        print("💡 ヒント:")
        print("  - インターネット接続を確認してください")
        print("  - API キーが有効か確認してください")
        print("  - NewsAPI の利用制限に達していないか確認してください")
        sys.exit(1)


if __name__ == "__main__":
    main()
