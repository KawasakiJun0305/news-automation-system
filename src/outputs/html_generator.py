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

    def __init__(self, output_dir: str = "output", template_style: str = "newspaper"):
        """
        HTMLGenerator を初期化

        パラメータ:
            output_dir (str): 出力ディレクトリのパス
            template_style (str): テンプレートスタイル ('newspaper', 'magazine', 'card')
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.template_style = template_style

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

        template_str = self._get_template(self.template_style)
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

    def _get_template(self, style: str = "newspaper") -> str:
        """
        HTML テンプレート文字列を取得

        パラメータ:
            style (str): テンプレートスタイル ('newspaper', 'magazine', 'card', 'hybrid')

        戻り値:
            str: HTML テンプレート
        """
        if style == "magazine":
            return self._get_magazine_template()
        elif style == "card":
            return self._get_card_template()
        elif style == "hybrid":
            return self._get_hybrid_template()
        else:
            return self._get_newspaper_template()

    def _get_newspaper_template(self) -> str:
        """
        新聞風テンプレート（既存のデザイン）

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

    def _get_magazine_template(self) -> str:
        """
        マガジン風テンプレート（モダン、画像強調、非対称レイアウト）

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
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Noto Sans JP', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.7;
        }

        /* ヘッダー */
        header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 30px 0;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 1000;
        }

        .masthead {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .masthead h1 {
            font-size: 2.5rem;
            font-weight: 900;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .masthead .date-info {
            font-size: 0.9rem;
            color: #666;
            text-align: right;
        }

        /* メインコンテンツ */
        main {
            max-width: 1400px;
            margin: 40px auto;
            padding: 0 30px;
        }

        /* ヒーロー記事 */
        .hero-article {
            background: white;
            border-radius: 20px;
            overflow: hidden;
            margin-bottom: 40px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }

        .hero-article:hover {
            transform: translateY(-5px);
        }

        .hero-image {
            width: 100%;
            height: 500px;
            object-fit: cover;
            display: block;
        }

        .hero-content {
            padding: 40px;
        }

        .hero-content h2 {
            font-size: 2.5rem;
            margin-bottom: 20px;
            line-height: 1.3;
        }

        .hero-content h2 a {
            color: #333;
            text-decoration: none;
            transition: color 0.3s;
        }

        .hero-content h2 a:hover {
            color: #667eea;
        }

        .article-meta {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            font-size: 0.9rem;
            color: #666;
        }

        .article-summary {
            font-size: 1.1rem;
            margin-bottom: 15px;
            line-height: 1.8;
        }

        .article-description {
            font-size: 1rem;
            color: #555;
            margin-bottom: 20px;
        }

        .read-more {
            display: inline-block;
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-weight: 700;
            transition: transform 0.3s, box-shadow 0.3s;
        }

        .read-more:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }

        /* グリッドレイアウト */
        .articles-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }

        .article-card {
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .article-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }

        .article-image {
            width: 100%;
            height: 250px;
            object-fit: cover;
            display: block;
        }

        .article-card-content {
            padding: 25px;
        }

        .article-card h3 {
            font-size: 1.4rem;
            margin-bottom: 15px;
            line-height: 1.4;
        }

        .article-card h3 a {
            color: #333;
            text-decoration: none;
            transition: color 0.3s;
        }

        .article-card h3 a:hover {
            color: #667eea;
        }

        .article-card .article-summary {
            font-size: 0.95rem;
        }

        /* プレースホルダー画像 */
        .placeholder-image {
            width: 100%;
            height: 250px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 3rem;
        }

        .hero-placeholder {
            height: 500px;
            font-size: 5rem;
        }

        /* フッター */
        footer {
            background: rgba(0, 0, 0, 0.9);
            color: white;
            text-align: center;
            padding: 30px;
            margin-top: 60px;
        }

        /* レスポンシブ */
        @media (max-width: 768px) {
            .masthead {
                flex-direction: column;
                text-align: center;
            }

            .masthead h1 {
                font-size: 2rem;
                margin-bottom: 10px;
            }

            .hero-image, .hero-placeholder {
                height: 300px;
            }

            .hero-content h2 {
                font-size: 1.8rem;
            }

            .articles-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="masthead">
            <h1>{{ title }}</h1>
            <div class="date-info">
                <div>{{ date }} {{ time }}</div>
                <div>総記事数: {{ total_count }}</div>
            </div>
        </div>
    </header>

    <main>
        {% if top_articles %}
        <!-- ヒーロー記事 -->
        <article class="hero-article">
            {% if top_articles[0].image_url %}
            <img src="{{ top_articles[0].image_url }}" alt="{{ top_articles[0].title }}" class="hero-image">
            {% else %}
            <div class="placeholder-image hero-placeholder">📰</div>
            {% endif %}
            <div class="hero-content">
                <h2><a href="{{ top_articles[0].source_url }}" target="_blank">{{ top_articles[0].title }}</a></h2>
                <div class="article-meta">
                    <span>📰 {{ top_articles[0].source_name }}</span>
                    <span>📅 {{ top_articles[0].published_at.strftime('%Y-%m-%d %H:%M') }}</span>
                    <span>🌐 {{ top_articles[0].language.upper() }}</span>
                </div>
                {% if top_articles[0].summary %}
                <p class="article-summary"><strong>要約:</strong> {{ top_articles[0].summary }}</p>
                {% endif %}
                {% if top_articles[0].description %}
                <p class="article-description">{{ top_articles[0].description }}</p>
                {% endif %}
                <a href="{{ top_articles[0].source_url }}" target="_blank" class="read-more">続きを読む →</a>
            </div>
        </article>
        {% endif %}

        <!-- その他の記事グリッド -->
        <div class="articles-grid">
            {% for article in top_articles[1:] + other_articles %}
            <article class="article-card">
                {% if article.image_url %}
                <img src="{{ article.image_url }}" alt="{{ article.title }}" class="article-image">
                {% else %}
                <div class="placeholder-image">📰</div>
                {% endif %}
                <div class="article-card-content">
                    <h3><a href="{{ article.source_url }}" target="_blank">{{ article.title }}</a></h3>
                    <div class="article-meta">
                        <span>📰 {{ article.source_name }}</span>
                        <span>📅 {{ article.published_at.strftime('%Y-%m-%d') }}</span>
                    </div>
                    {% if article.summary %}
                    <p class="article-summary"><strong>要約:</strong> {{ article.summary[:150] }}{% if article.summary|length > 150 %}...{% endif %}</p>
                    {% endif %}
                    <a href="{{ article.source_url }}" target="_blank" class="read-more">続きを読む →</a>
                </div>
            </article>
            {% endfor %}
        </div>
    </main>

    <footer>
        <p>&copy; {{ date }} {{ title }} | Powered by NewsAPI & Claude</p>
    </footer>
</body>
</html>'''

    def _get_card_template(self) -> str:
        """
        カード型テンプレート（モダン、均等グリッド、クリーン）

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
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Noto Sans JP', sans-serif;
            background: #f8f9fa;
            color: #333;
            line-height: 1.7;
        }

        /* ヘッダー */
        header {
            background: white;
            padding: 40px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin-bottom: 40px;
        }

        .masthead {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 30px;
            text-align: center;
        }

        .masthead h1 {
            font-size: 3rem;
            font-weight: 900;
            color: #2c3e50;
            margin-bottom: 15px;
        }

        .masthead .date-info {
            font-size: 1rem;
            color: #7f8c8d;
        }

        /* メインコンテンツ */
        main {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 30px;
        }

        /* カードグリッド */
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 30px;
            margin-bottom: 60px;
        }

        .card {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            display: flex;
            flex-direction: column;
        }

        .card:hover {
            transform: translateY(-8px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }

        .card-image-container {
            position: relative;
            width: 100%;
            height: 220px;
            overflow: hidden;
        }

        .card-image {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
        }

        .card:hover .card-image {
            transform: scale(1.05);
        }

        .card-placeholder {
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #3498db, #8e44ad);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 3rem;
        }

        .card-content {
            padding: 25px;
            flex: 1;
            display: flex;
            flex-direction: column;
        }

        .card h2 {
            font-size: 1.3rem;
            margin-bottom: 12px;
            line-height: 1.4;
            flex-grow: 0;
        }

        .card h2 a {
            color: #2c3e50;
            text-decoration: none;
            transition: color 0.3s;
        }

        .card h2 a:hover {
            color: #3498db;
        }

        .card-meta {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            font-size: 0.85rem;
            color: #95a5a6;
        }

        .card-summary {
            font-size: 0.95rem;
            color: #555;
            margin-bottom: 15px;
            line-height: 1.6;
            flex-grow: 1;
        }

        .card-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: auto;
        }

        .tag {
            display: inline-block;
            padding: 5px 12px;
            background: #ecf0f1;
            color: #7f8c8d;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 700;
        }

        .card-link {
            color: #3498db;
            text-decoration: none;
            font-weight: 700;
            transition: color 0.3s;
        }

        .card-link:hover {
            color: #2980b9;
        }

        /* フッター */
        footer {
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 40px;
            margin-top: 80px;
        }

        footer p {
            font-size: 1rem;
        }

        /* レスポンシブ */
        @media (max-width: 768px) {
            .masthead h1 {
                font-size: 2rem;
            }

            .cards-grid {
                grid-template-columns: 1fr;
            }

            .card-image-container {
                height: 200px;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="masthead">
            <h1>{{ title }}</h1>
            <div class="date-info">
                {{ date }} {{ time }} | 総記事数: {{ total_count }}
            </div>
        </div>
    </header>

    <main>
        <div class="cards-grid">
            {% for article in top_articles + other_articles %}
            <article class="card">
                <div class="card-image-container">
                    {% if article.image_url %}
                    <img src="{{ article.image_url }}" alt="{{ article.title }}" class="card-image">
                    {% else %}
                    <div class="card-placeholder">📰</div>
                    {% endif %}
                </div>
                <div class="card-content">
                    <h2><a href="{{ article.source_url }}" target="_blank">{{ article.title }}</a></h2>
                    <div class="card-meta">
                        <span>📰 {{ article.source_name }}</span>
                        <span>📅 {{ article.published_at.strftime('%Y-%m-%d') }}</span>
                    </div>
                    {% if article.summary %}
                    <p class="card-summary"><strong>要約:</strong> {{ article.summary[:120] }}{% if article.summary|length > 120 %}...{% endif %}</p>
                    {% elif article.description %}
                    <p class="card-summary">{{ article.description[:120] }}{% if article.description|length > 120 %}...{% endif %}</p>
                    {% endif %}
                    <div class="card-footer">
                        <span class="tag">{{ article.language.upper() }}</span>
                        <a href="{{ article.source_url }}" target="_blank" class="card-link">続きを読む →</a>
                    </div>
                </div>
            </article>
            {% endfor %}
        </div>
    </main>

    <footer>
        <p>&copy; {{ date }} {{ title }} | Powered by NewsAPI & Claude</p>
    </footer>
</body>
</html>'''

    def _get_hybrid_template(self) -> str:
        """
        ハイブリッドテンプレート（カード型 + マガジン風ヒーロー記事）

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
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Noto Sans JP', sans-serif;
            background: #f8f9fa;
            color: #333;
            line-height: 1.7;
        }

        /* ヘッダー */
        header {
            background: white;
            padding: 40px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin-bottom: 40px;
        }

        .masthead {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 30px;
            text-align: center;
        }

        .masthead h1 {
            font-size: 3rem;
            font-weight: 900;
            color: #2c3e50;
            margin-bottom: 15px;
        }

        .masthead .date-info {
            font-size: 1rem;
            color: #7f8c8d;
        }

        /* メインコンテンツ */
        main {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 30px;
        }

        /* ヒーロー記事 */
        .hero-article {
            background: white;
            border-radius: 15px;
            overflow: hidden;
            margin-bottom: 50px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
        }

        .hero-article:hover {
            box-shadow: 0 8px 30px rgba(0,0,0,0.12);
            transform: translateY(-3px);
        }

        .hero-image-container {
            width: 100%;
            height: 450px;
            overflow: hidden;
        }

        .hero-image {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
        }

        .hero-article:hover .hero-image {
            transform: scale(1.03);
        }

        .hero-placeholder {
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #3498db, #8e44ad);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 5rem;
        }

        .hero-content {
            padding: 40px;
        }

        .hero-content h2 {
            font-size: 2.2rem;
            margin-bottom: 20px;
            line-height: 1.4;
            color: #2c3e50;
        }

        .hero-content h2 a {
            color: #2c3e50;
            text-decoration: none;
            transition: color 0.3s;
        }

        .hero-content h2 a:hover {
            color: #3498db;
        }

        .hero-meta {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            font-size: 0.95rem;
            color: #7f8c8d;
        }

        .hero-summary {
            font-size: 1.1rem;
            margin-bottom: 15px;
            line-height: 1.8;
            color: #555;
        }

        .hero-description {
            font-size: 1rem;
            color: #666;
            margin-bottom: 25px;
            line-height: 1.7;
        }

        .hero-read-more {
            display: inline-block;
            padding: 14px 35px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 700;
            transition: all 0.3s;
        }

        .hero-read-more:hover {
            background: #2980b9;
            transform: translateX(5px);
        }

        /* カードグリッド */
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 30px;
            margin-bottom: 60px;
        }

        .card {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            display: flex;
            flex-direction: column;
        }

        .card:hover {
            transform: translateY(-8px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }

        .card-image-container {
            position: relative;
            width: 100%;
            height: 220px;
            overflow: hidden;
        }

        .card-image {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
        }

        .card:hover .card-image {
            transform: scale(1.05);
        }

        .card-placeholder {
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #3498db, #8e44ad);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 3rem;
        }

        .card-content {
            padding: 25px;
            flex: 1;
            display: flex;
            flex-direction: column;
        }

        .card h3 {
            font-size: 1.3rem;
            margin-bottom: 12px;
            line-height: 1.4;
            flex-grow: 0;
        }

        .card h3 a {
            color: #2c3e50;
            text-decoration: none;
            transition: color 0.3s;
        }

        .card h3 a:hover {
            color: #3498db;
        }

        .card-meta {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            font-size: 0.85rem;
            color: #95a5a6;
        }

        .card-summary {
            font-size: 0.95rem;
            color: #555;
            margin-bottom: 15px;
            line-height: 1.6;
            flex-grow: 1;
        }

        .card-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: auto;
        }

        .tag {
            display: inline-block;
            padding: 5px 12px;
            background: #ecf0f1;
            color: #7f8c8d;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 700;
        }

        .card-link {
            color: #3498db;
            text-decoration: none;
            font-weight: 700;
            transition: color 0.3s;
        }

        .card-link:hover {
            color: #2980b9;
        }

        /* フッター */
        footer {
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 40px;
            margin-top: 80px;
        }

        footer p {
            font-size: 1rem;
        }

        /* レスポンシブ */
        @media (max-width: 768px) {
            .masthead h1 {
                font-size: 2rem;
            }

            .hero-image-container {
                height: 300px;
            }

            .hero-content {
                padding: 25px;
            }

            .hero-content h2 {
                font-size: 1.6rem;
            }

            .cards-grid {
                grid-template-columns: 1fr;
            }

            .card-image-container {
                height: 200px;
            }
        }
    </style>
</head>
<body>
    <header>
        <div class="masthead">
            <h1>{{ title }}</h1>
            <div class="date-info">
                {{ date }} {{ time }} | 総記事数: {{ total_count }}
            </div>
        </div>
    </header>

    <main>
        {% if top_articles %}
        <!-- ヒーロー記事（1件目のみ） -->
        <article class="hero-article">
            <div class="hero-image-container">
                {% if top_articles[0].image_url %}
                <img src="{{ top_articles[0].image_url }}" alt="{{ top_articles[0].title }}" class="hero-image">
                {% else %}
                <div class="hero-placeholder">📰</div>
                {% endif %}
            </div>
            <div class="hero-content">
                <h2><a href="{{ top_articles[0].source_url }}" target="_blank">{{ top_articles[0].title }}</a></h2>
                <div class="hero-meta">
                    <span>📰 {{ top_articles[0].source_name }}</span>
                    <span>📅 {{ top_articles[0].published_at.strftime('%Y-%m-%d %H:%M') }}</span>
                    <span>🌐 {{ top_articles[0].language.upper() }}</span>
                </div>
                {% if top_articles[0].summary %}
                <p class="hero-summary"><strong>要約:</strong> {{ top_articles[0].summary }}</p>
                {% endif %}
                {% if top_articles[0].description %}
                <p class="hero-description">{{ top_articles[0].description }}</p>
                {% endif %}
                <a href="{{ top_articles[0].source_url }}" target="_blank" class="hero-read-more">続きを読む →</a>
            </div>
        </article>
        {% endif %}

        <!-- その他の記事（カードグリッド） -->
        <div class="cards-grid">
            {% for article in top_articles[1:] + other_articles %}
            <article class="card">
                <div class="card-image-container">
                    {% if article.image_url %}
                    <img src="{{ article.image_url }}" alt="{{ article.title }}" class="card-image">
                    {% else %}
                    <div class="card-placeholder">📰</div>
                    {% endif %}
                </div>
                <div class="card-content">
                    <h3><a href="{{ article.source_url }}" target="_blank">{{ article.title }}</a></h3>
                    <div class="card-meta">
                        <span>📰 {{ article.source_name }}</span>
                        <span>📅 {{ article.published_at.strftime('%Y-%m-%d') }}</span>
                    </div>
                    {% if article.summary %}
                    <p class="card-summary"><strong>要約:</strong> {{ article.summary[:120] }}{% if article.summary|length > 120 %}...{% endif %}</p>
                    {% elif article.description %}
                    <p class="card-summary">{{ article.description[:120] }}{% if article.description|length > 120 %}...{% endif %}</p>
                    {% endif %}
                    <div class="card-footer">
                        <span class="tag">{{ article.language.upper() }}</span>
                        <a href="{{ article.source_url }}" target="_blank" class="card-link">続きを読む →</a>
                    </div>
                </div>
            </article>
            {% endfor %}
        </div>
    </main>

    <footer>
        <p>&copy; {{ date }} {{ title }} | Powered by NewsAPI & Claude</p>
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
