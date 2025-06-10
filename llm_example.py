#!/usr/bin/env python3
"""
LLM策略示例 - 展示如何讓LLM控制遊戲
"""

import json
import random
from typing import List, Dict, Any
from main import LLMX4Game


class SimpleLLMStrategy:
    """簡單的LLM策略示例"""
    
    def __init__(self):
        self.strategy_name = "簡單擴張策略"
    
    def decide_actions(self, observation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """根據觀察決定行動"""
        actions = []
        ap_remaining = observation["game_info"]["action_points_remaining"]
        
        # 優先級策略
        # 1. 如果有可探索的位置，先探索
        explorable = observation["map_overview"].get("explorable_positions", [])
        if explorable and ap_remaining >= 1:
            target = random.choice(explorable)
            actions.append({
                "action_type": "explore",
                "target_x": target[0],
                "target_y": target[1]
            })
            ap_remaining -= 1
        
        # 2. 如果糧食不足，優先建造農場
        net_food = observation["resources"]["net_food_change"]
        if net_food < 10 and ap_remaining >= 2:
            controlled = observation["controlled_territories"]
            for territory in controlled:
                if territory["terrain"] == "plains" and "farm" not in territory["buildings"]:
                    actions.append({
                        "action_type": "build",
                        "target_x": territory["position"]["x"],
                        "target_y": territory["position"]["y"],
                        "building_type": "farm"
                    })
                    ap_remaining -= 2
                    break
        
        # 3. 如果有可擴張的位置且資源足夠，進行擴張
        expandable = observation["map_overview"].get("expandable_positions", [])
        current_resources = observation["resources"]["current_resources"]
        if (expandable and ap_remaining >= 2 and 
            current_resources["food"] >= 20 and current_resources["wood"] >= 10):
            target = random.choice(expandable)
            actions.append({
                "action_type": "expand",
                "target_x": target[0],
                "target_y": target[1]
            })
            ap_remaining -= 2
        
        # 4. 建造提升生產的建築
        if ap_remaining >= 2:
            controlled = observation["controlled_territories"]
            for territory in controlled:
                terrain = territory["terrain"]
                buildings = territory["buildings"]
                
                if terrain == "mountain" and "mine" not in buildings:
                    if (current_resources["wood"] >= 20 and 
                        current_resources["metal"] >= 10):
                        actions.append({
                            "action_type": "build",
                            "target_x": territory["position"]["x"],
                            "target_y": territory["position"]["y"],
                            "building_type": "mine"
                        })
                        ap_remaining -= 2
                        break
                elif terrain == "forest" and "lumber_mill" not in buildings:
                    if (current_resources["wood"] >= 15 and 
                        current_resources["metal"] >= 5):
                        actions.append({
                            "action_type": "build",
                            "target_x": territory["position"]["x"],
                            "target_y": territory["position"]["y"],
                            "building_type": "lumber_mill"
                        })
                        ap_remaining -= 2
                        break
        
        # 5. 如果有多餘的行動點，進行開發
        if ap_remaining >= 1:
            controlled = observation["controlled_territories"]
            if controlled:
                territory = random.choice(controlled)
                actions.append({
                    "action_type": "exploit",
                    "target_x": territory["position"]["x"],
                    "target_y": territory["position"]["y"]
                })
                ap_remaining -= 1
        
        # 6. 如果還有行動點且資源充足，進行研究
        if (ap_remaining >= 3 and 
            current_resources["metal"] >= 15 and 
            current_resources["food"] >= 10):
            actions.append({
                "action_type": "research"
            })
        
        return actions


def run_llm_simulation(num_games: int = 3):
    """運行LLM模擬"""
    strategy = SimpleLLMStrategy()
    results = []
    
    for game_num in range(num_games):
        print(f"\n=== 遊戲 {game_num + 1} ===")
        game = LLMX4Game()
        turn_count = 0
        
        while not game.game_state.game_over and turn_count < 100:
            # 獲取觀察
            observation_str = game.get_observation()
            observation = json.loads(observation_str)
            
            # LLM決定行動
            actions = strategy.decide_actions(observation)
            
            print(f"回合 {game.game_state.turn}: 計劃執行 {len(actions)} 個行動")
            
            # 執行行動
            if actions:
                action_results = game.execute_actions(actions)
                for i, result in enumerate(action_results):
                    if result["success"]:
                        print(f"  行動 {i+1}: ✓ {result['message']}")
                    else:
                        print(f"  行動 {i+1}: ✗ {result['message']}")
            
            # 進入下一回合
            turn_result = game.next_turn()
            turn_count += 1
            
            # 簡單狀態報告
            simple_obs = json.loads(game.get_simple_observation())
            print(f"  資源: 礦石{simple_obs['resources']['ore']}, 木材{simple_obs['resources']['wood']}, 金屬{simple_obs['resources']['metal']}, 糧食{simple_obs['resources']['food']}")
            print(f"  領土: {simple_obs['controlled_tiles']}, 人口: {simple_obs['population']}")
            
            if turn_result["game_over"]:
                print(f"遊戲結束！勝利: {turn_result['victory']}")
                break
        
        # 收集結果
        final_score = game.get_final_score()
        results.append({
            "game": game_num + 1,
            "turns": turn_count,
            "victory": game.game_state.victory,
            "final_score": final_score
        })
        
        print(f"最終得分: {final_score['final_score']['total_score']:.2f}")
    
    # 總結結果
    print("\n=== 模擬結果總結 ===")
    victories = sum(1 for r in results if r["victory"])
    avg_score = sum(r["final_score"]["final_score"]["total_score"] for r in results) / len(results)
    avg_turns = sum(r["turns"] for r in results) / len(results)
    
    print(f"總遊戲數: {num_games}")
    print(f"勝利次數: {victories}")
    print(f"勝利率: {victories/num_games:.1%}")
    print(f"平均得分: {avg_score:.2f}")
    print(f"平均回合數: {avg_turns:.1f}")
    
    return results


def test_single_game():
    """測試單個遊戲"""
    print("=== 單遊戲測試 ===")
    game = LLMX4Game()
    strategy = SimpleLLMStrategy()
    
    for turn in range(10):  # 只運行10回合作為演示
        print(f"\n--- 回合 {game.game_state.turn} ---")
        
        # 獲取觀察
        observation = json.loads(game.get_observation())
        print(f"當前資源: {observation['resources']['current_resources']}")
        print(f"行動點: {observation['game_info']['action_points_remaining']}")
        
        # 決定行動
        actions = strategy.decide_actions(observation)
        print(f"計劃行動: {len(actions)}")
        
        # 執行行動
        if actions:
            results = game.execute_actions(actions)
            for i, (action, result) in enumerate(zip(actions, results)):
                status = "✓" if result["success"] else "✗"
                print(f"  {status} {action['action_type']}: {result['message']}")
        
        # 下一回合
        game.next_turn()
        
        if game.game_state.game_over:
            print("遊戲結束！")
            break
    
    # 最終狀態
    print(f"\n最終狀態:")
    print(game.get_simple_observation())


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "simulate":
        num_games = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        run_llm_simulation(num_games)
    else:
        test_single_game()
