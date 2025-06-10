# LLM-X4 模擬遊戲

這是一個專為大型語言模型（LLM）設計的4X策略遊戲模擬器，旨在評估LLM在多步決策、資源分配與長期規劃方面的推理能力。

## 專案概述

LLM-X4 是基於經典的4X遊戲機制（eXplore、eXpand、eXploit、eXterminate）構建的純文字策略遊戲，提供結構化的JSON/YAML介面供LLM進行遊戲控制。

### 核心特色

- **純文字介面**：所有遊戲狀態都以JSON/YAML格式呈現，便於LLM理解和處理
- **回合制系統**：每回合限制5個行動點，迫使LLM進行策略優先排序
- **可量化評估**：提供多維度評分系統，包含資源效率、人口健康、目標達成度等指標
- **多種遊戲模式**：支援互動模式、API模式、和批量模擬測試

## 快速開始

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 運行互動模式

```bash
python main.py
```

### 運行API服務器

```bash
pip install flask
python api_server.py --host 0.0.0.0 --port 5000
```

### 運行測試

```bash
python test_game.py
```

### LLM策略示例

```bash
# 單遊戲測試
python llm_example.py

# 批量模擬
python llm_example.py simulate 5
```

## 遊戲機制

### 基本設定

- **地圖**：10x10方格陣列，包含平原、森林、山脈、湖泊四種地形
- **資源**：礦石、木材、金屬、糧食四種資源類型
- **人口**：每個地塊有人口基數和增長率，人口影響生產效率並消耗糧食
- **行動點**：每回合5點行動點，不同行動消耗不同點數

### 行動類型

| 行動 | 成本 | 說明 |
|------|------|------|
| explore | 1 AP | 探索相鄰未知地塊 |
| expand | 2 AP | 擴張到已探索地塊（需消耗資源） |
| exploit | 1 AP | 額外開發地塊資源 |
| build | 2 AP | 建造建築物（需消耗資源） |
| research | 3 AP | 進行技術研究（需消耗資源） |
| migrate | 1 AP | 在地塊間遷移人口 |

### 建築類型

- **礦場**：提升山脈地塊的礦石產出
- **伐木場**：提升森林地塊的木材產出  
- **農場**：增加糧食產出
- **冶煉廠**：將礦石轉換為金屬
- **房屋**：增加人口容量和增長率

### 勝利條件

- **主要目標**：累積1000金屬
- **時間限制**：100回合內達成目標
- **失敗條件**：所有人口死亡

## API使用

### 創建新遊戲

```bash
curl -X POST http://localhost:5000/game/new \
  -H "Content-Type: application/json" \
  -d '{"width": 10, "height": 10}'
```

### 獲取遊戲觀察

```bash
curl http://localhost:5000/game/{game_id}/observation
```

### 執行行動

```bash
curl -X POST http://localhost:5000/game/{game_id}/action \
  -H "Content-Type: application/json" \
  -d '{"action_type": "explore", "target_x": 5, "target_y": 5}'
```

### 進入下一回合

```bash
curl -X POST http://localhost:5000/game/{game_id}/next_turn
```

## 行動範例

### 探索

```json
{
  "action_type": "explore",
  "target_x": 5,
  "target_y": 5
}
```

### 擴張

```json
{
  "action_type": "expand", 
  "target_x": 6,
  "target_y": 5
}
```

### 建造

```json
{
  "action_type": "build",
  "target_x": 5,
  "target_y": 5,
  "building_type": "farm"
}
```

### 開發資源

```json
{
  "action_type": "exploit",
  "target_x": 5,
  "target_y": 5
}
```

### 研究

```json
{
  "action_type": "research"
}
```

### 遷移人口

```json
{
  "action_type": "migrate"
}
```

## 評分系統

遊戲提供多維度評分指標：

- **資源效率**：總資源產出 ÷ 總行動點消耗
- **人口健康**：當前人口 ÷ 最大可能人口
- **目標達成度**：當前金屬 ÷ 1000（勝利目標）
- **策略多樣性**：基於行動類型的Shannon熵值

最終得分 = 資源效率×0.3 + 人口健康×0.2 + 目標達成×0.4 + 策略多樣性×0.1

## 專案結構

```
X4_sim/
├── core/                   # 核心遊戲邏輯
│   ├── models.py          # 基礎數據模型
│   ├── map.py             # 地圖管理
│   ├── game_state.py      # 遊戲狀態管理
│   ├── action_engine.py   # 行動執行引擎
│   └── observation_builder.py # 觀察構建器
├── main.py                # 主程序（互動模式）
├── api_server.py          # HTTP API服務器
├── llm_example.py         # LLM策略示例
├── test_game.py           # 測試套件
├── requirements.txt       # Python依賴
└── README.md             # 說明文檔
```

## 開發說明

### 擴展建築類型

在 `core/models.py` 中的 `BuildingType` 枚舉添加新建築，然後在相關的產出計算函數中實現效果。

### 添加新行動

1. 在 `ActionType` 枚舉中添加新行動類型
2. 在 `ActionEngine` 中實現執行邏輯
3. 在 `ObservationBuilder` 中添加行動說明

### 添加新事件

在 `GameState` 的事件系統中添加新的 `EventType` 和對應的處理邏輯。

## 測試

執行完整測試套件：

```bash
python test_game.py
```

執行特定測試：

```bash
python -m unittest test_game.TestModels
```

## 許可證

MIT License - 詳見 LICENSE 文件

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 致謝

此專案靈感來源於經典4X策略遊戲和現代LLM推理能力評估需求。