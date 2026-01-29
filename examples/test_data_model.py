"""
UniversalArticle データモデルの動作確認スクリプト

実際の NewsAPI から記事を取得し、UniversalArticle に変換します。

実行方法:
    python examples/test_data_model.py
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
from src.models import UniversalArticle
import json


def main():
    """メイン処理"""

    # .env ファイルから環境変数を読み込む
    load_dotenv()

    print("=" * 70)
    print("UniversalArticle データモデル 動作確認")
    print("=" * 70)
    print()

    try:
        # 1. NewsAPI から記事を取得
        print("【ステップ 1】NewsAPI から記事を取得")
        print("-" * 70)

        articles = NewsAPISource.fetch_and_normalize(
            keyword="Python",
            language="en",
            page_size=3
        )

        print(f"✅ {len(articles)} 件の記事を UniversalArticle に変換しました")
        print()

        # 2. 各記事の詳細を表示
        print("=" * 70)
        print("【ステップ 2】UniversalArticle の詳細表示")
        print("=" * 70)

        for i, article in enumerate(articles, 1):
            print(f"\n記事 {i}:")
            print(f"  ID: {article.id}")
            print(f"  タイトル: {article.title}")
            print(f"  ソース: {article.source_name}")
            print(f"  ソースタイプ: {article.source_type}")
            print(f"  カテゴリ: {article.category}")
            print(f"  URL: {article.source_url}")
            print(f"  公開日: {article.published_at}")
            print(f"  取得日: {article.fetched_at}")
            print(f"  言語: {article.language}")
            print(f"  地域: {article.region}")

            if article.description:
                print(f"  説明: {article.description[:100]}...")

            if article.image_url:
                print(f"  画像URL: {article.image_url}")

            # バリデーション
            is_valid = article.validate()
            print(f"  データ検証: {'✅ 有効' if is_valid else '❌ 無効'}")
            print()
            print("-" * 70)

        # 3. UniversalArticle の機能テスト
        print()
        print("=" * 70)
        print("【ステップ 3】UniversalArticle の機能テスト")
        print("=" * 70)

        if articles:
            test_article = articles[0]

            # to_dict テスト
            print("\n1. to_dict() メソッドのテスト")
            print("-" * 70)
            article_dict = test_article.to_dict()
            print(f"✅ 辞書形式に変換成功")
            print(f"  キー数: {len(article_dict)}")
            print(f"  主要キー: {list(article_dict.keys())[:8]}")
            print()

            # from_dict テスト
            print("2. from_dict() メソッドのテスト")
            print("-" * 70)
            recreated_article = UniversalArticle.from_dict(article_dict)
            print(f"✅ 辞書から UniversalArticle を再構築成功")
            print(f"  再構築されたタイトル: {recreated_article.title}")
            print(f"  元のタイトルと一致: {'✅' if recreated_article.title == test_article.title else '❌'}")
            print()

            # __repr__ テスト
            print("3. __repr__() メソッドのテスト")
            print("-" * 70)
            repr_str = repr(test_article)
            print(f"✅ 文字列表現: {repr_str}")
            print()

            # JSON シリアライズテスト
            print("4. JSON シリアライズ・デシリアライズテスト")
            print("-" * 70)

            # 日付を ISO 形式の文字列に変換してから JSON にシリアライズ
            json_data = json.dumps(article_dict, indent=2, ensure_ascii=False, default=str)
            print(f"✅ JSON 形式にシリアライズ成功")
            print(f"  JSON データサイズ: {len(json_data)} バイト")
            print(f"  JSON プレビュー（最初の200文字）:")
            print(f"  {json_data[:200]}...")
            print()

        # 4. 統計情報
        print("=" * 70)
        print("【ステップ 4】統計情報")
        print("=" * 70)
        print()

        print(f"総記事数: {len(articles)}")

        # 言語別集計
        languages = {}
        for article in articles:
            languages[article.language] = languages.get(article.language, 0) + 1

        print("\n言語別集計:")
        for lang, count in languages.items():
            print(f"  {lang}: {count} 件")

        # ソース別集計
        sources = {}
        for article in articles:
            sources[article.source_name] = sources.get(article.source_name, 0) + 1

        print("\nソース別集計:")
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            print(f"  {source}: {count} 件")

        # バリデーション結果
        valid_count = sum(1 for article in articles if article.validate())
        print(f"\nデータ検証:")
        print(f"  有効な記事: {valid_count}/{len(articles)} 件")

        print()
        print("=" * 70)
        print("✅ 全てのテストが正常に完了しました！")

    except ValueError as e:
        print(f"❌ エラー: {e}")
        print()
        print("💡 ヒント:")
        print("  .env ファイルに NEWSAPI_KEY が設定されているか確認してください。")
        sys.exit(1)

    except Exception as e:
        print(f"❌ 予期しないエラーが発生しました: {e}")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
