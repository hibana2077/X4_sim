#!/usr/bin/env python3
"""
LLM-X4 模擬遊戲主程序
"""

import json
import sys
from typing import List, Dict, Any, Optional
from core.game_state import GameState
from core.action_engine import ActionEngine
from core.observation_builder import ObservationBuilder


class LLMX4Game:
    """LLM-X4 遊戲主類"""
    
    def __init__(self, map_width: int = 10, map_height: int = 10):
        self.game_state = GameState(map_width, map_height)
        self.action_engine = ActionEngine(self.game_state)
        self.observation_builder = ObservationBuilder(self.game_state)
        
    def get_observation(self, format_type: str = "json") -> str:
        """獲取當前遊戲狀態觀察"""
        return self.observation_builder.build_observation(format_type)
    
    def get_simple_observation(self) -> str:
        """獲取簡化的遊戲狀態觀察"""
        return self.observation_builder.build_simple_observation()
    
    def execute_actions(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """執行一系列行動"""
        return self.action_engine.execute_actions(actions)
    
    def next_turn(self) -> Dict[str, Any]:
        """進入下一回合"""
        self.game_state.next_turn()
        return {
            "turn": self.game_state.turn,
            "game_over": self.game_state.game_over,
            "victory": self.game_state.victory,
            "action_points": self.game_state.action_points
        }
    
    def get_final_score(self) -> Dict[str, Any]:
        """獲取最終得分"""
        if not self.game_state.game_over:
            return {"error": "遊戲尚未結束"}
        
        return {
            "final_score": self.game_state.get_score(),
            "victory": self.game_state.victory,
            "total_turns": self.game_state.turn,
            "final_resources": self.game_state.global_resources.to_dict(),
            "final_population": self.game_state.game_map.get_total_population()
        }
    
    def save_game(self, filename: str) -> bool:
        """保存遊戲狀態"""
        try:
            game_data = {
                "game_state": self.game_state.to_dict(),
                "version": "1.0"
            }
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(game_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存遊戲失敗: {e}")
            return False
    
    def load_game(self, filename: str) -> bool:
        """載入遊戲狀態"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                game_data = json.load(f)
            
            # 這裡需要實現狀態重建邏輯
            # 為了簡化，目前只支持新遊戲
            print("載入遊戲功能尚未完全實現")
            return False
        except Exception as e:
            print(f"載入遊戲失敗: {e}")
            return False


def interactive_mode():
    """互動模式 - 用於測試和演示"""
    print("=== LLM-X4 模擬遊戲 ===")
    print("輸入 'help' 查看可用命令")
    
    game = LLMX4Game()
    
    while not game.game_state.game_over:
        try:
            user_input = input(f"\n回合 {game.game_state.turn} (AP: {game.game_state.action_points})> ").strip()
            
            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'help':
                print_help()
            elif user_input.lower() == 'status':
                print("=== 遊戲狀態 ===")
                print(game.get_simple_observation())
            elif user_input.lower() == 'observation':
                print("=== 詳細觀察 ===")
                print(game.get_observation())
            elif user_input.lower() == 'next':
                result = game.next_turn()
                print(f"進入回合 {result['turn']}")
                if result['game_over']:
                    print("遊戲結束！")
                    if result['victory']:
                        print("恭喜獲勝！")
                    break
            elif user_input.startswith('action'):
                # 解析行動命令
                try:
                    action_str = user_input[6:].strip()
                    if action_str.startswith('{'):
                        # JSON格式行動
                        action_data = json.loads(action_str)
                        results = game.execute_actions([action_data])
                        for result in results:
                            print(f"行動結果: {result}")
                    else:
                        print("請使用JSON格式輸入行動，例如:")
                        print('action {"action_type": "explore", "target_x": 5, "target_y": 5}')
                except json.JSONDecodeError:
                    print("JSON格式錯誤")
                except Exception as e:
                    print(f"執行行動時發生錯誤: {e}")
            else:
                print("未知命令，輸入 'help' 查看可用命令")
                
        except KeyboardInterrupt:
            print("\n遊戲被中斷")
            break
        except Exception as e:
            print(f"發生錯誤: {e}")
    
    if game.game_state.game_over:
        print("\n=== 最終得分 ===")
        final_score = game.get_final_score()
        print(json.dumps(final_score, indent=2, ensure_ascii=False))


def print_help():
    """打印幫助信息"""
    help_text = """
可用命令:
- help: 顯示此幫助信息
- status: 顯示簡化的遊戲狀態
- observation: 顯示詳細的遊戲觀察
- next: 進入下一回合
- action <JSON>: 執行行動 (JSON格式)
- quit: 退出遊戲

行動示例:
- 探索: action {"action_type": "explore", "target_x": 5, "target_y": 5}
- 擴張: action {"action_type": "expand", "target_x": 5, "target_y": 5}
- 建造: action {"action_type": "build", "target_x": 5, "target_y": 5, "building_type": "farm"}
- 開發: action {"action_type": "exploit", "target_x": 5, "target_y": 5}
- 研究: action {"action_type": "research"}
- 遷移: action {"action_type": "migrate"}
"""
    print(help_text)


def api_mode():
    """API模式 - 用於與LLM集成"""
    print("LLM-X4 API模式啟動")
    print("請通過標準輸入發送JSON指令")
    
    game = LLMX4Game()
    
    try:
        while not game.game_state.game_over:
            line = sys.stdin.readline().strip()
            if not line:
                break
                
            try:
                command = json.loads(line)
                
                if command.get("type") == "get_observation":
                    response = {
                        "type": "observation",
                        "data": json.loads(game.get_observation())
                    }
                    print(json.dumps(response, ensure_ascii=False))
                    
                elif command.get("type") == "execute_actions":
                    actions = command.get("actions", [])
                    results = game.execute_actions(actions)
                    response = {
                        "type": "action_results",
                        "data": results
                    }
                    print(json.dumps(response, ensure_ascii=False))
                    
                elif command.get("type") == "next_turn":
                    result = game.next_turn()
                    response = {
                        "type": "turn_result",
                        "data": result
                    }
                    print(json.dumps(response, ensure_ascii=False))
                    
                elif command.get("type") == "get_score":
                    if game.game_state.game_over:
                        score = game.get_final_score()
                    else:
                        score = game.game_state.get_score()
                    response = {
                        "type": "score",
                        "data": score
                    }
                    print(json.dumps(response, ensure_ascii=False))
                    
                else:
                    response = {
                        "type": "error",
                        "message": f"未知指令類型: {command.get('type')}"
                    }
                    print(json.dumps(response, ensure_ascii=False))
                    
            except json.JSONDecodeError:
                response = {
                    "type": "error",
                    "message": "JSON格式錯誤"
                }
                print(json.dumps(response, ensure_ascii=False))
                
    except KeyboardInterrupt:
        print("\nAPI模式結束")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--api":
        api_mode()
    else:
        interactive_mode()
