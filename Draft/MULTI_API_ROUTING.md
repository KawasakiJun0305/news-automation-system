# Multi API Routing - マルチ API ルーティング設計

## 🎯 概要

**カテゴリやタスク別に、最適な LLM を自動選択** し、コスト削減と品質向上を実現。

---

## 🔄 ルーティング戦略

```
【入力】ニュース記事 + カテゴリ
  ↓
【判定】この記事はどの API で処理すべき？
  ↓
【ルーティング】
  ├─ AI カテゴリ＆複雑 → Claude（高精度）
  ├─ 決算＆数値分析 → ChatGPT（得意）
  ├─ 科学論文 → Gemini（安い）
  └─ その他 → Gemini（最安）
  ↓
【実行】選択された API で処理
  ↓
【結果】品質を保ちながらコスト削減
```

---

## 💾 ルーティング設定

```python
# config.py

API_ROUTING = {
    "AI": {
        "summarize": "claude",        # 高精度が必要
        "keyword_extract": "gemini",  # シンプル → 安い
        "priority": ["claude", "openai", "gemini"]
    },
    
    "決算": {
        "summarize": "openai",        # ChatGPT は数値分析得意
        "keyword_extract": "gemini",
        "priority": ["openai", "claude", "gemini"]
    },
    
    "科学": {
        "summarize": "claude",        # 論文は複雑
        "keyword_extract": "gemini",
        "priority": ["claude", "openai"]
    },
    
    "モノづくり": {
        "summarize": "gemini",        # 比較的シンプル
        "keyword_extract": "gemini",
        "priority": ["gemini", "openai"]
    },
    
    "ボードゲーム": {
        "summarize": "gemini",
        "keyword_extract": "gemini",
        "priority": ["gemini", "openai"]
    }
}

DIFFICULTY_BASED = {
    "low": "gemini",      # 簡単 → 最安
    "medium": "openai",   # 中程度
    "high": "claude"      # 難しい → 高精度
}
```

---

## 🤖 ルーター実装

```python
# src/llm/router.py

class AdaptiveLLMRouter:
    """
    カテゴリと難易度から最適な API を自動選択
    """
    
    def __init__(self):
        self.routing_config = API_ROUTING
    
    async def summarize(self, article, category):
        """
        記事を要約（最適な API で自動実行）
        """
        # 最適な API を選択
        provider = self._select_provider(category, task="summarize")
        
        # 選択された API で処理
        if provider == "claude":
            from src.llm.claude_client import ClaudeClient
            client = ClaudeClient()
        elif provider == "openai":
            from src.llm.openai_client import OpenAIClient
            client = OpenAIClient()
        else:  # gemini
            from src.llm.gemini_client import GeminiClient
            client = GeminiClient()
        
        summary = await client.summarize(article.summary or article.title)
        
        return summary, provider
    
    def _select_provider(self, category: str, task: str) -> str:
        """
        ルーティングロジック
        """
        if category in self.routing_config:
            if task in self.routing_config[category]:
                return self.routing_config[category][task]
        
        # デフォルト：最安の API
        return "gemini"
    
    def _assess_difficulty(self, text: str) -> str:
        """
        テキストの複雑度を判定
        """
        # 学術用語が多い → 難しい
        academic_terms = ['研究', '論文', '実験', 'arXiv']
        complexity = sum(1 for term in academic_terms if term in text)
        
        if complexity > 3:
            return "high"
        elif complexity > 1:
            return "medium"
        else:
            return "low"
```

---

## 💰 コスト最適化

### API 価格比較

```
Claude:   $3 / 1M tokens
ChatGPT:  $0.5 / 1M tokens  
Gemini:   $0.075 / 1M tokens  ← 最安
```

### 月額試算（記事 20 件/日）

```
Claude のみ使用：
  記事数：600 件/月
  トークン：約 330,000
  コスト：約 ¥1,000

Gemini を優先（高コスト削減）：
  Gemini 80%：260,000 tokens × $0.075 = $19.5
  Claude 20%：70,000 tokens × $3 = $210
  合計：約 ¥230/月  ← 78% 削減
```

---

## 🔄 フェイルオーバー機構

API が落ちても大丈夫：

```python
async def summarize_with_fallback(self, article, category):
    """
    メイン API が失敗したら次の API に切り替え
    """
    providers = self.routing_config[category]["priority"]
    
    for provider in providers:
        try:
            summary = await self._summarize_with_provider(provider, article)
            return summary, provider
        
        except Exception as e:
            logging.warning(f"{provider} failed: {e}")
            continue
    
    # 全て失敗したらキャッシュから返す
    return get_from_cache(article.id)
```

---

## 📊 使用統計

```python
# 実行ログを見て、どの API がどれだけ使われたか確認

stats = {
    "claude": 120,    # 20%
    "openai": 240,    # 40%
    "gemini": 240     # 40%
}

# コスト計算：
# claude: 120 × 3 / 1M = $0.36
# openai: 240 × 0.5 / 1M = $0.12
# gemini: 240 × 0.075 / 1M = $0.018
# 合計：約 $0.50/月 ← 超安い
```

---

**次は MULTI_SOURCE_EXPANSION.md を読んでください！**
