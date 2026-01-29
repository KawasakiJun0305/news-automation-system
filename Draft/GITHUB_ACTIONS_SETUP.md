# GitHub Actions Setup - GitHub Actions 設定ガイド

## 🎯 概要

GitHub Actions を使って **毎朝 6 時に自動実行** し、結果を GitHub Pages に配置。

---

## ✅ ステップ 1：GitHub にプッシュ

```bash
# Git 初期化
git init
git add .
git commit -m "Initial commit: News Automation System"

# GitHub リモート登録
git remote add origin https://github.com/YOUR_USERNAME/news-automation-system.git

# プッシュ
git push -u origin main
```

---

## ✅ ステップ 2：Secrets 登録（API キー）

GitHub 上で：
1. Settings → Secrets and variables → Actions
2. New repository secret

以下を登録：

```
NEWSAPI_KEY = your_newsapi_key
CLAUDE_API_KEY = sk-ant-your_key
NOTION_API_TOKEN = ntn_your_token
NOTION_DATABASE_ID = your_db_id
```

---

## ✅ ステップ 3：GitHub Actions YAML 作成

```yaml
# .github/workflows/daily-news.yml

name: Daily News Generation

on:
  schedule:
    # 毎日朝 9 時（JST）= UTC 00:00 に実行
    - cron: '0 0 * * *'
  
  # 手動実行も可能
  workflow_dispatch:

jobs:
  generate-news:
    runs-on: ubuntu-latest
    
    steps:
      # Step 1: リポジトリをチェックアウト
      - uses: actions/checkout@v3
      
      # Step 2: Python をセットアップ
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      # Step 3: 依存ライブラリをインストール
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      # Step 4: メイン処理を実行
      - name: Generate News
        env:
          NEWSAPI_KEY: ${{ secrets.NEWSAPI_KEY }}
          CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}
          NOTION_API_TOKEN: ${{ secrets.NOTION_API_TOKEN }}
          NOTION_DATABASE_ID: ${{ secrets.NOTION_DATABASE_ID }}
        run: python src/main.py
      
      # Step 5: HTML ファイルが生成されたか確認
      - name: Check generated files
        run: |
          if [ -f news/$(date +%Y-%m-%d).html ]; then
            echo "✅ HTML generated successfully"
          else
            echo "❌ HTML generation failed"
            exit 1
          fi
      
      # Step 6: 変更を Git にコミット
      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add news/
          git commit -m "Daily news update: $(date +%Y-%m-%d)" || echo "No changes"
          git push
      
      # Step 7: GitHub Pages にデプロイ
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./news
          cname: CNAME  # カスタムドメインを使う場合

  # 失敗時の通知（オプション）
  notify-failure:
    runs-on: ubuntu-latest
    needs: generate-news
    if: failure()
    
    steps:
      - name: Send Slack notification
        run: |
          # Slack への通知処理（オプション）
          echo "News generation failed"
```

---

## 📊 タイムゾーン設定

**重要**：GitHub Actions はデフォルト UTC

```yaml
# JST（日本時間）朝 6 時に実行したい場合

schedule:
  # UTC 21:00 = JST 06:00
  - cron: '0 21 * * *'
```

---

## 🔍 デバッグ

### Actions ログ確認

GitHub > Actions タブで実行ログを確認。

### 手動実行テスト

```yaml
workflow_dispatch:
```

の設定があれば、GitHub UI から手動実行可能。

---

## ✅ チェックリスト

- [ ] GitHub リポジトリが作成されている
- [ ] code push されている
- [ ] Secrets が全て登録されている
- [ ] `.github/workflows/daily-news.yml` が存在
- [ ] GitHub Pages が有効化されている（Settings → Pages）
- [ ] 初回実行が成功した

---

**次は最後の MONETIZATION_ROADMAP.md を読んでください！**
