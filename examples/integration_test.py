"""
NewsAPI + UniversalArticle + Claude の統合テスト

このスクリプトは以下の流れをテストします：
1. NewsAPIから記事を取得
2. UniversalArticleに変換
3. Claudeで要約を生成
4. 要約をUniversalArticleに追加
5. 結果を表示
"""

import os
import sys
from pathlib import Path
from typing import List

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
from src.models import UniversalArticle

# .env ファイルを読み込む
from dotenv import load_dotenv
load_dotenv()


def summarize_articles(articles: List[UniversalArticle], claude_client: ClaudeClient) -> List[UniversalArticle]:
    """
    UniversalArticle のリストに対して要約を生成し、summary フィールドに追加

    パラメータ:
        articles (List[UniversalArticle]): 記事のリスト
        claude_client (ClaudeClient): Claude API クライアント

    戻り値:
        List[UniversalArticle]: 要約が追加された記事のリスト
    """

    print(f"\n{'='*60}")
    print(f"📝 Claude による要約生成を開始します")
    print(f"{'='*60}\n")

    summarized_articles = []

    for i, article in enumerate(articles, 1):
        print(f"\n進捗: {i}/{len(articles)}")
        print(f"記事: {article.title[:50]}...")

        # 記事の内容を結合
        # タイトル + description + content を使用
        content_parts = [f"タイトル: {article.title}"]

        if article.description:
            content_parts.append(f"\n概要: {article.description}")

        if article.content:
            content_parts.append(f"\n本文: {article.content}")

        full_text = "\n".join(content_parts)

        # 内容が空の場合はスキップ
        if len(full_text.strip()) < 50:
            print(f"⚠️ 記事 {i} の内容が不足しています。スキップします。")
            article.summary = ""
            summarized_articles.append(article)
            continue

        try:
            # Claude で要約を生成
            summary = claude_client.summarize(
                text=full_text,
                max_tokens=300,
                language=article.language
            )

            # UniversalArticle の summary フィールドに追加
            article.summary = summary
            summarized_articles.append(article)

            print(f"✅ 要約完了: {summary[:80]}...")

        except Exception as e:
            print(f"❌ 記事 {i} の要約に失敗: {e}")
            article.summary = ""
            summarized_articles.append(article)

    print(f"\n{'='*60}")
    print(f"✅ {len(summarized_articles)} 件の要約が完了しました")
    print(f"{'='*60}\n")

    return summarized_articles


def display_results(articles: List[UniversalArticle]):
    """
    結果を見やすく表示

    パラメータ:
        articles (List[UniversalArticle]): 表示する記事のリスト
    """

    print(f"\n{'='*60}")
    print(f"📰 統合テスト結果")
    print(f"{'='*60}\n")

    for i, article in enumerate(articles, 1):
        print(f"\n【記事 {i}】")
        print(f"ID: {article.id}")
        print(f"タイトル: {article.title}")
        print(f"ソース: {article.source_name}")
        print(f"公開日: {article.published_at.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"言語: {article.language}")
        print(f"URL: {article.source_url}")

        if article.description:
            print(f"\n📄 元の概要:")
            print(f"  {article.description[:200]}...")

        if article.summary:
            print(f"\n✨ Claude 要約:")
            print(f"  {article.summary}")
        else:
            print(f"\n⚠️ 要約なし")

        print(f"\n{'-'*60}")

    # 統計情報
    print(f"\n{'='*60}")
    print(f"📊 統計情報")
    print(f"{'='*60}")
    print(f"総記事数: {len(articles)}")
    print(f"要約済み: {sum(1 for a in articles if a.summary)}")
    print(f"要約失敗: {sum(1 for a in articles if not a.summary)}")
    print(f"日本語記事: {sum(1 for a in articles if a.language == 'ja')}")
    print(f"英語記事: {sum(1 for a in articles if a.language == 'en')}")


def main():
    """
    統合テストのメイン処理
    """

    print(f"\n{'='*60}")
    print(f"🚀 NewsAPI + UniversalArticle + Claude 統合テスト")
    print(f"{'='*60}\n")

    try:
        # 1. NewsAPI から記事を取得 & UniversalArticle に変換
        print("📡 ステップ 1: NewsAPI から記事を取得中...")

        keyword = "AI"  # テスト用のキーワード
        articles = NewsAPISource.fetch_and_normalize(
            keyword=keyword,
            language='en',  # 英語記事で試す
            page_size=5  # テストなので少なめに
        )

        print(f"✅ {len(articles)} 件の記事を UniversalArticle に変換しました\n")

        # 2. Claude クライアントを初期化
        print("🤖 ステップ 2: Claude クライアントを初期化中...")
        claude_client = ClaudeClient()
        print("✅ Claude クライアント初期化完了\n")

        # 3. 要約を生成
        print("📝 ステップ 3: 要約を生成中...")
        summarized_articles = summarize_articles(articles, claude_client)

        # 4. 結果を表示
        display_results(summarized_articles)

        print(f"\n{'='*60}")
        print(f"🎉 統合テスト完了！")
        print(f"{'='*60}\n")

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
