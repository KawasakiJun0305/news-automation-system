"""
HTML 生成モジュール（新聞風デザイン）

UniversalArticle のリストから、新聞風デザインの HTML を生成します。
"""

import os
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from jinja2 import Template

from src.models import UniversalArticle


class HTMLGenerator:
    """
    新聞風デザインの HTML を生成するクラス
    """

    def __init__(self, output_dir: str = "output"):
        """
        HTMLGenerator を初期化

        パラメータ:
            output_dir (str): 出力ディレクトリのパス
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        articles: List[UniversalArticle],
        title: str = "AI News Daily",
        filename: Optional[str] = None
    ) -> str:
        """
        記事リストから HTML を生成

        パラメータ:
            articles (List[UniversalArticle]): 記事のリスト
            title (str): ページタイトル
            filename (Optional[str]): 出力ファイル名（指定しない場合は日時から自動生成）

        戻り値:
            str: 生成された HTML ファイルのパス
        """

        if not articles:
            raise ValueError("記事リストが空です")

        # ファイル名を生成
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"news_{timestamp}.html"

        # 記事を日付でソート（新しい順）
        sorted_articles = sorted(
            articles,
            key=lambda x: x.published_at,
            reverse=True
        )

        # HTML を生成
        html_content = self._render_template(sorted_articles, title)

        # ファイルに保存
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"✅ HTML ファイルを生成しました: {output_path}")

        return str(output_path)

    def _render_template(self, articles: List[UniversalArticle], title: str) -> str:
        """
        Jinja2 テンプレートから HTML をレンダリング

        パラメータ:
            articles (List[UniversalArticle]): 記事のリスト
            title (str): ページタイトル

        戻り値:
            str: レンダリングされた HTML
        """

        template_str = self._get_template()
        template = Template(template_str)

        # 記事をトップニュースとその他に分割
        # トップニュースは最初の3件
        top_articles = articles[:3] if len(articles) >= 3 else articles
        other_articles = articles[3:] if len(articles) > 3 else []

        # 現在の日時
        now = datetime.now()

        # テンプレートに渡すデータ
        context = {
            'title': title,
            'date': now.strftime('%Y年%m月%d日'),
            'time': now.strftime('%H:%M'),
            'top_articles': top_articles,
            'other_articles': other_articles,
            'total_count': len(articles)
        }

        return template.render(**context)

    def _get_template(self) -> str:
        """
        HTML テンプレート文字列を取得

        戻り値:
            str: HTML テンプレート
        """

        return '''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&display=swap" rel="stylesheet">
    <style>
        /* リセット & ベーススタイル */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Georgia', 'Times New Roman', serif;
            background-color: #f5f5f0;
            color: #222;
            line-height: 1.6;
        }

        /* ヘッダー（新聞のマストヘッド） */
        header {
            background-color: #fff;
            border-bottom: 3px solid #000;
            padding: 20px 0;
            margin-bottom: 10px;
        }

        .masthead {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            text-align: center;
        }

        .masthead h1 {
            font-family: 'Playfair Display', 'Georgia', 'Times New Roman', serif;
            font-size: 3.5rem;
            font-weight: 900;
            letter-spacing: 3px;
            margin-bottom: 10px;
            text-transform: uppercase;
        }

        .masthead .date-info {
            font-size: 0.9rem;
            color: #666;
            border-top: 1px solid #ddd;
            border-bottom: 1px solid #ddd;
            padding: 5px 0;
            margin-top: 10px;
        }

        /* メインコンテンツ */
        main {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        /* トップニュースセクション */
        .top-news {
            background-color: #fff;
            padding: 30px;
            margin-bottom: 30px;
            border: 1px solid #ddd;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .top-news h2 {
            font-size: 1.2rem;
            border-bottom: 2px solid #000;
            padding-bottom: 5px;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* 記事カード（トップニュース） */
        .article-card {
            margin-bottom: 30px;
            padding-bottom: 30px;
            border-bottom: 1px solid #ddd;
        }

        .article-card:last-child {
            border-bottom: none;
        }

        .article-card h3 {
            font-size: 1.8rem;
            margin-bottom: 10px;
            line-height: 1.3;
        }

        .article-card h3 a {
            color: #000;
            text-decoration: none;
            transition: color 0.3s;
        }

        .article-card h3 a:hover {
            color: #0066cc;
        }

        .article-meta {
            font-size: 0.85rem;
            color: #666;
            margin-bottom: 15px;
            font-style: italic;
        }

        .article-meta span {
            margin-right: 15px;
        }

        .article-summary {
            font-size: 1rem;
            line-height: 1.7;
            margin-bottom: 10px;
        }

        .article-description {
            font-size: 0.95rem;
            color: #555;
            line-height: 1.6;
            margin-bottom: 10px;
        }

        .read-more {
            display: inline-block;
            margin-top: 10px;
            color: #0066cc;
            text-decoration: none;
            font-weight: bold;
            font-size: 0.9rem;
        }

        .read-more:hover {
            text-decoration: underline;
        }

        /* その他のニュースセクション */
        .other-news {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .news-item {
            background-color: #fff;
            padding: 20px;
            border: 1px solid #ddd;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .news-item h3 {
            font-size: 1.3rem;
            margin-bottom: 10px;
            line-height: 1.3;
        }

        .news-item h3 a {
            color: #000;
            text-decoration: none;
        }

        .news-item h3 a:hover {
            color: #0066cc;
        }

        .news-item .article-meta {
            margin-bottom: 10px;
        }

        .news-item .article-summary {
            font-size: 0.95rem;
        }

        .news-item .article-description {
            font-size: 0.9rem;
        }

        /* フッター */
        footer {
            background-color: #222;
            color: #fff;
            text-align: center;
            padding: 20px;
            margin-top: 50px;
        }

        footer p {
            font-size: 0.9rem;
        }

        /* レスポンシブデザイン */
        @media (max-width: 768px) {
            .masthead h1 {
                font-size: 2.5rem;
            }

            .article-card h3 {
                font-size: 1.5rem;
            }

            .other-news {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <!-- ヘッダー -->
    <header>
        <div class="masthead">
            <h1>{{ title }}</h1>
            <div class="date-info">
                {{ date }} ({{ time }}) | 総記事数: {{ total_count }}
            </div>
        </div>
    </header>

    <!-- メインコンテンツ -->
    <main>
        {% if top_articles %}
        <!-- トップニュース -->
        <section class="top-news">
            <h2>トップニュース</h2>
            {% for article in top_articles %}
            <article class="article-card">
                <h3><a href="{{ article.source_url }}" target="_blank">{{ article.title }}</a></h3>
                <div class="article-meta">
                    <span>📰 {{ article.source_name }}</span>
                    <span>📅 {{ article.published_at.strftime('%Y-%m-%d %H:%M') }}</span>
                    <span>🌐 {{ article.language.upper() }}</span>
                </div>
                {% if article.summary %}
                <p class="article-summary"><strong>要約:</strong> {{ article.summary }}</p>
                {% endif %}
                {% if article.description %}
                <p class="article-description">{{ article.description }}</p>
                {% endif %}
                <a href="{{ article.source_url }}" target="_blank" class="read-more">記事を読む →</a>
            </article>
            {% endfor %}
        </section>
        {% endif %}

        {% if other_articles %}
        <!-- その他のニュース -->
        <section class="other-news">
            {% for article in other_articles %}
            <article class="news-item">
                <h3><a href="{{ article.source_url }}" target="_blank">{{ article.title }}</a></h3>
                <div class="article-meta">
                    <span>📰 {{ article.source_name }}</span>
                    <span>📅 {{ article.published_at.strftime('%Y-%m-%d %H:%M') }}</span>
                </div>
                {% if article.summary %}
                <p class="article-summary"><strong>要約:</strong> {{ article.summary }}</p>
                {% endif %}
                {% if article.description %}
                <p class="article-description">{{ article.description[:150] }}{% if article.description|length > 150 %}...{% endif %}</p>
                {% endif %}
                <a href="{{ article.source_url }}" target="_blank" class="read-more">記事を読む →</a>
            </article>
            {% endfor %}
        </section>
        {% endif %}
    </main>

    <!-- フッター -->
    <footer>
        <p>&copy; {{ date }} AI News Daily | Powered by NewsAPI & Claude</p>
    </footer>
</body>
</html>'''

    def open_in_browser(self, html_path: str):
        """
        生成された HTML をブラウザで開く

        パラメータ:
            html_path (str): HTML ファイルのパス
        """

        # 絶対パスに変換
        abs_path = Path(html_path).absolute()

        # ファイルが存在するか確認
        if not abs_path.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {abs_path}")

        # ブラウザで開く
        file_url = f"file:///{abs_path}"
        print(f"🌐 ブラウザで開いています: {file_url}")

        webbrowser.open(file_url)

    def generate_and_preview(
        self,
        articles: List[UniversalArticle],
        title: str = "AI News Daily",
        filename: Optional[str] = None
    ) -> str:
        """
        HTML を生成してブラウザでプレビュー

        パラメータ:
            articles (List[UniversalArticle]): 記事のリスト
            title (str): ページタイトル
            filename (Optional[str]): 出力ファイル名

        戻り値:
            str: 生成された HTML ファイルのパス
        """

        # HTML を生成
        html_path = self.generate(articles, title=title, filename=filename)

        # ブラウザで開く
        self.open_in_browser(html_path)

        return html_path
