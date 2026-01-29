"""
ClaudeClient の動作確認スクリプト

このスクリプトは、実際の Claude API で要約を生成して表示します。
実行前に .env ファイルに CLAUDE_API_KEY を設定してください。

実行方法:
    python examples/test_claude.py
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
from src.llm.claude_client import ClaudeClient


def main():
    """メイン処理"""

    # .env ファイルから環境変数を読み込む
    load_dotenv()

    print("=" * 60)
    print("Claude API 動作確認スクリプト")
    print("=" * 60)
    print()

    try:
        # ClaudeClient を初期化
        client = ClaudeClient()
        print(f"✅ ClaudeClient を初期化しました（モデル: {client.model}）")
        print()

        # テスト 1: 単一テキストの要約（日本語）
        print("【テスト 1】単一テキストの要約（日本語）")
        print("-" * 60)

        article_ja = """
        OpenAI は本日、次世代言語モデル「GPT-5」のプレビュー版を公開しました。
        GPT-5 は、従来の GPT-4 と比較して推論精度が 35% 向上し、
        複雑な数学問題やコード生成でも高い精度を実現しています。
        特に、多言語対応が強化され、100以上の言語で高品質な応答が可能になりました。
        正式リリースは3月を予定しており、API経由で利用可能になる予定です。
        """

        print("元テキスト:")
        print(article_ja.strip())
        print()

        summary_ja = client.summarize(article_ja, language="ja")

        print("要約:")
        print(summary_ja)
        print()
        print("=" * 60)
        print()

        # テスト 2: 単一テキストの要約（英語）
        print("【テスト 2】単一テキストの要約（英語）")
        print("-" * 60)

        article_en = """
        Tesla has announced a new breakthrough in battery technology that could
        revolutionize electric vehicles. The company's latest battery design
        promises a 50% increase in energy density while reducing costs by 30%.
        This advancement could extend the range of Tesla vehicles to over 600 miles
        on a single charge. The new batteries are expected to enter production
        in the second half of 2026.
        """

        print("Original text:")
        print(article_en.strip())
        print()

        summary_en = client.summarize(article_en, language="en")

        print("Summary:")
        print(summary_en)
        print()
        print("=" * 60)
        print()

        # テスト 3: 複数テキストの一括要約
        print("【テスト 3】複数テキストの一括要約")
        print("-" * 60)

        texts = [
            "Python 3.12 がリリースされました。処理速度が10%向上しています。",
            "AI技術の進展により、自動運転車の実用化が加速しています。",
            "量子コンピュータの研究が新たな段階に入りました。"
        ]

        print(f"{len(texts)} 件のテキストを要約します...")
        print()

        summaries = client.batch_summarize(texts, language="ja")

        for i, (text, summary) in enumerate(zip(texts, summaries), 1):
            print(f"テキスト {i}:")
            print(f"  元: {text}")
            print(f"  要約: {summary}")
            print()

        print("=" * 60)
        print()

        # テスト 4: 記事形式の複数要約
        print("【テスト 4】記事形式の複数要約")
        print("-" * 60)

        articles = [
            {
                "title": "新型iPhone発表",
                "description": "Appleは本日、新型iPhoneを発表しました。5Gに対応し、カメラ性能が大幅に向上しています。"
            },
            {
                "title": "気候変動サミット開催",
                "description": "国連の気候変動サミットが開催され、各国が2030年までの削減目標を発表しました。"
            }
        ]

        print(f"{len(articles)} 件の記事を要約します...")
        print()

        summarized_articles = client.summarize_multiple(articles, language="ja")

        for i, article in enumerate(summarized_articles, 1):
            print(f"記事 {i}:")
            print(f"  タイトル: {article['title']}")
            print(f"  元の説明: {article['description']}")
            print(f"  要約: {article['summary']}")
            print()

        print("=" * 60)
        print()
        print("✅ 全てのテストが正常に完了しました！")

    except ValueError as e:
        print(f"❌ エラー: {e}")
        print()
        print("💡 ヒント:")
        print("  .env ファイルに CLAUDE_API_KEY が設定されているか確認してください。")
        print("  例: CLAUDE_API_KEY=sk-ant-...")
        sys.exit(1)

    except Exception as e:
        print(f"❌ 予期しないエラーが発生しました: {e}")
        print()
        print("💡 ヒント:")
        print("  - インターネット接続を確認してください")
        print("  - API キーが有効か確認してください")
        print("  - Claude API の利用制限に達していないか確認してください")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
