# LLM-X4 遊戲使用指南

## 快速開始

### 1. 安裝和設置

```bash
# 使用提供的腳本安裝依賴
./run.sh install

# 或者手動安裝
pip install -r requirements.txt
```

### 2. 運行測試

```bash
# 運行完整測試套件
./run.sh test

# 或者直接運行
python test_game.py
```

### 3. 基礎使用

#### 互動模式
```bash
./run.sh interactive
# 或者
python main.py
```

#### LLM策略演示
```bash
./run.sh demo
# 或者
python llm_example.py
```

#### API服務器
```bash
./run.sh api
# 或者
python api_server.py
```

## 詳細使用說明

### 互動模式命令

在互動模式中，可以使用以下命令：

- `help` - 顯示幫助信息
- `status` - 顯示簡化的遊戲狀態
- `observation` - 顯示詳細的遊戲觀察
- `next` - 進入下一回合
- `action <JSON>` - 執行行動
- `quit` - 退出遊戲

#### 行動例子

```bash
# 探索
action {"action_type": "explore", "target_x": 5, "target_y": 5}

# 擴張
action {"action_type": "expand", "target_x": 6, "target_y": 5}

# 建造農場
action {"action_type": "build", "target_x": 5, "target_y": 5, "building_type": "farm"}

# 開發資源
action {"action_type": "exploit", "target_x": 5, "target_y": 5}

# 研究
action {"action_type": "research"}

# 遷移人口
action {"action_type": "migrate"}
```

### API使用

#### 創建新遊戲

```bash
curl -X POST http://localhost:5000/game/new \
  -H "Content-Type: application/json" \
  -d '{"width": 10, "height": 10}'
```

響應：
```json
{
  "success": true,
  "game_id": "game_1234567890_5678",
  "message": "新遊戲已創建，地圖大小: 10x10"
}
```

#### 獲取遊戲狀態

```bash
# 簡化狀態
curl http://localhost:5000/game/{game_id}/observation?simple=true

# 完整狀態
curl http://localhost:5000/game/{game_id}/observation
```

#### 執行行動

```bash
curl -X POST http://localhost:5000/game/{game_id}/action \
  -H "Content-Type: application/json" \
  -d '{"action_type": "explore", "target_x": 5, "target_y": 5}'
```

#### 進入下一回合

```bash
curl -X POST http://localhost:5000/game/{game_id}/next_turn
```

### 程式化使用

```python
from main import LLMX4Game
import json

# 創建遊戲
game = LLMX4Game(width=10, height=10)

# 獲取觀察
observation = json.loads(game.get_observation())
print(f"當前回合: {observation['game_info']['current_turn']}")

# 執行行動
actions = [
    {"action_type": "explore", "target_x": 5, "target_y": 5},
    {"action_type": "build", "target_x": 5, "target_y": 5, "building_type": "farm"}
]
results = game.execute_actions(actions)

# 進入下一回合
turn_result = game.next_turn()

# 檢查遊戲狀態
if game.game_state.game_over:
    final_score = game.get_final_score()
    print(f"遊戲結束，最終得分: {final_score}")
```

## LLM整合

### 基礎提示詞模板

```
你是一個4X策略遊戲AI，目標是在100回合內累積1000金屬獲勝。

當前狀態：
{observation}

請以JSON格式返回行動列表：
[
  {"action_type": "explore", "target_x": 5, "target_y": 5},
  {"action_type": "build", "target_x": 4, "target_y": 4, "building_type": "farm"}
]

策略要點：
1. 優先確保糧食供應
2. 平衡探索和建設
3. 重視金屬生產
4. 合理分配行動點
```

### Python LLM整合示例

```python
import openai
from main import LLMX4Game

def llm_play_game(api_key, model="gpt-4"):
    client = openai.OpenAI(api_key=api_key)
    game = LLMX4Game()
    
    while not game.game_state.game_over:
        # 獲取觀察
        observation = game.get_observation()
        
        # 構建提示詞
        prompt = f"""
        你是4X策略遊戲AI，目標是累積1000金屬獲勝。
        
        當前狀態：
        {observation}
        
        請以JSON格式返回行動列表。
        """
        
        # 調用LLM
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # 解析行動
        try:
            actions = json.loads(response.choices[0].message.content)
            results = game.execute_actions(actions)
            print(f"回合 {game.game_state.turn}: 執行了 {len(results)} 個行動")
        except:
            print("LLM回應解析失敗")
        
        # 下一回合
        game.next_turn()
    
    return game.get_final_score()
```

## 分析和評估

### 批量測試

```python
from llm_example import SimpleLLMStrategy, run_llm_simulation

# 運行多個遊戲測試
results = run_llm_simulation(num_games=10)

# 分析結果
victories = sum(1 for r in results if r["victory"])
avg_score = sum(r["final_score"]["final_score"]["total_score"] for r in results) / len(results)

print(f"勝利率: {victories/len(results):.1%}")
print(f"平均得分: {avg_score:.2f}")
```

### 性能分析

```python
from analyzer import GameAnalyzer

# 創建分析器
analyzer = GameAnalyzer()

# 添加遊戲記錄
for result in results:
    analyzer.add_game_record(result)

# 生成報告
report = analyzer.generate_report("analysis_report.md")
print(report)
```

## 配置和自定義

### 遊戲參數調整

在 `config.py` 中可以調整：

```python
GAME_CONFIG = {
    "default_map_width": 10,      # 地圖寬度
    "default_map_height": 10,     # 地圖高度
    "max_turns": 100,             # 最大回合數
    "action_points_per_turn": 5,  # 每回合行動點
    "victory_metal_target": 1000  # 勝利目標金屬數
}
```

### 自定義策略

繼承 `SimpleLLMStrategy` 類實現自定義策略：

```python
class MyStrategy(SimpleLLMStrategy):
    def decide_actions(self, observation):
        # 實現你的策略邏輯
        actions = []
        # ... 策略代碼 ...
        return actions
```

## 故障排除

### 常見問題

1. **模組導入錯誤**
   ```bash
   # 確保在正確目錄運行
   cd /path/to/X4_sim
   python main.py
   ```

2. **依賴缺失**
   ```bash
   # 重新安裝依賴
   pip install -r requirements.txt
   ```

3. **API連接問題**
   ```bash
   # 檢查服務器是否啟動
   curl http://localhost:5000/health
   ```

### 調試模式

啟用詳細日誌：

```python
from utils import GameLogger

logger = GameLogger("game.log")
logger.info("遊戲開始")
```

### 性能優化

對於大規模測試：

```python
# 使用簡化觀察減少數據傳輸
simple_obs = game.get_simple_observation()

# 批量執行行動
actions = [action1, action2, action3]
results = game.execute_actions(actions)
```

## 更多資源

- 查看 `llm_prompts.md` 獲取更多提示詞示例
- 運行 `python demo.py` 查看完整功能演示
- 查看 `test_game.py` 了解測試用例
- 訪問 `/api/help` 端點獲取API文檔
