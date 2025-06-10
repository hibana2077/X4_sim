#!/usr/bin/env python3
"""
完整演示腳本 - 展示LLM-X4遊戲的各種功能
"""

import json
import time
from main import LLMX4Game
from llm_example import SimpleLLMStrategy
from analyzer import GameAnalyzer


def demo_basic_game():
    """演示基礎遊戲功能"""
    print("=== 基礎遊戲演示 ===")
    
    game = LLMX4Game(width=8, height=8)
    
    # 顯示初始狀態
    print("\n初始遊戲狀態:")
    simple_obs = json.loads(game.get_simple_observation())
    print(f"回合: {simple_obs['turn']}")
    print(f"行動點: {simple_obs['ap']}")
    print(f"資源: {simple_obs['resources']}")
    print(f"控制地塊: {simple_obs['controlled_tiles']}")
    
    # 執行一些基本行動
    print("\n執行探索行動...")
    actions = [{"action_type": "explore", "target_x": 3, "target_y": 4}]
    results = game.execute_actions(actions)
    for result in results:
        print(f"結果: {result['message']}")
    
    print("\n執行建造行動...")
    actions = [{"action_type": "build", "target_x": 4, "target_y": 4, "building_type": "farm"}]
    results = game.execute_actions(actions)
    for result in results:
        print(f"結果: {result['message']}")
    
    # 進入下一回合
    print("\n進入下一回合...")
    turn_result = game.next_turn()
    print(f"新回合: {turn_result['turn']}")
    
    print("\n基礎演示完成!")
    return game


def demo_llm_strategy():
    """演示LLM策略"""
    print("\n=== LLM策略演示 ===")
    
    game = LLMX4Game(width=8, height=8)
    strategy = SimpleLLMStrategy()
    
    print(f"策略名稱: {strategy.strategy_name}")
    
    # 運行5回合
    for turn in range(5):
        print(f"\n--- 回合 {game.game_state.turn} ---")
        
        # 獲取觀察並制定策略
        observation = json.loads(game.get_observation())
        actions = strategy.decide_actions(observation)
        
        print(f"計劃執行 {len(actions)} 個行動")
        
        # 執行行動
        if actions:
            results = game.execute_actions(actions)
            for i, (action, result) in enumerate(zip(actions, results)):
                status = "✓" if result["success"] else "✗"
                print(f"  {status} {action['action_type']}: {result['message']}")
        
        # 顯示當前狀態
        simple_obs = json.loads(game.get_simple_observation())
        print(f"  資源: 礦石{simple_obs['resources']['ore']}, 木材{simple_obs['resources']['wood']}, 金屬{simple_obs['resources']['metal']}, 糧食{simple_obs['resources']['food']}")
        print(f"  領土: {simple_obs['controlled_tiles']}, 人口: {simple_obs['population']}")
        
        # 下一回合
        game.next_turn()
        
        if game.game_state.game_over:
            print("遊戲提前結束!")
            break
    
    print("\nLLM策略演示完成!")
    return game


def demo_api_format():
    """演示API格式"""
    print("\n=== API格式演示 ===")
    
    game = LLMX4Game()
    
    # 演示觀察格式
    print("\n1. 簡化觀察格式:")
    simple_obs = game.get_simple_observation()
    print(simple_obs)
    
    print("\n2. 完整觀察格式 (前200字符):")
    full_obs = game.get_observation()
    print(full_obs[:200] + "...")
    
    print("\n3. 行動執行格式:")
    action_example = {
        "action_type": "explore",
        "target_x": 5,
        "target_y": 5
    }
    print(f"輸入: {json.dumps(action_example, ensure_ascii=False)}")
    
    results = game.execute_actions([action_example])
    print(f"輸出: {json.dumps(results[0], ensure_ascii=False)}")
    
    print("\nAPI格式演示完成!")


def demo_analysis():
    """演示分析功能"""
    print("\n=== 遊戲分析演示 ===")
    
    analyzer = GameAnalyzer()
    
    # 模擬一些遊戲數據
    for i in range(3):
        print(f"\n生成模擬遊戲 {i+1}...")
        
        game = LLMX4Game(width=6, height=6)
        strategy = SimpleLLMStrategy()
        
        # 快速運行遊戲
        turn_count = 0
        while not game.game_state.game_over and turn_count < 20:
            observation = json.loads(game.get_observation())
            actions = strategy.decide_actions(observation)
            
            if actions:
                game.execute_actions(actions)
            
            game.next_turn()
            turn_count += 1
        
        # 收集遊戲數據
        game_data = {
            "total_turns": turn_count,
            "victory": game.game_state.victory,
            "final_score": game.game_state.get_score(),
            "final_resources": game.game_state.global_resources.to_dict(),
            "final_population": game.game_state.game_map.get_total_population(),
            "stats": game.game_state.stats
        }
        
        analyzer.add_game_record(game_data)
        print(f"遊戲 {i+1}: 回合{turn_count}, 得分{game_data['final_score']['total_score']:.2f}")
    
    # 生成分析報告
    print("\n=== 分析報告 ===")
    report = analyzer.generate_report()
    print(report[:500] + "..." if len(report) > 500 else report)
    
    print("\n分析演示完成!")


def demo_full_workflow():
    """演示完整工作流程"""
    print("\n=== 完整工作流程演示 ===")
    
    # 1. 創建遊戲
    print("1. 創建遊戲實例...")
    game = LLMX4Game()
    
    # 2. 獲取初始觀察
    print("2. 獲取初始觀察...")
    observation = json.loads(game.get_observation())
    print(f"   初始資源: {observation['resources']['current_resources']}")
    print(f"   控制地塊: {observation['map_overview']['controlled_tiles_count']}")
    
    # 3. LLM決策模擬
    print("3. LLM決策模擬...")
    strategy = SimpleLLMStrategy()
    actions = strategy.decide_actions(observation)
    print(f"   計劃行動: {len(actions)} 個")
    
    # 4. 執行行動
    print("4. 執行行動...")
    results = game.execute_actions(actions)
    success_count = sum(1 for r in results if r["success"])
    print(f"   成功執行: {success_count}/{len(results)} 個行動")
    
    # 5. 回合結算
    print("5. 回合結算...")
    turn_result = game.next_turn()
    print(f"   進入回合: {turn_result['turn']}")
    
    # 6. 狀態更新
    print("6. 檢查更新後狀態...")
    new_obs = json.loads(game.get_simple_observation())
    print(f"   當前資源: {new_obs['resources']}")
    print(f"   遊戲狀態: {'進行中' if not new_obs['game_over'] else '已結束'}")
    
    print("\n完整工作流程演示完成!")


def main():
    """主演示函數"""
    print("=" * 50)
    print("LLM-X4 模擬遊戲 - 完整功能演示")
    print("=" * 50)
    
    try:
        # 基礎功能演示
        demo_basic_game()
        time.sleep(1)
        
        # LLM策略演示
        demo_llm_strategy()
        time.sleep(1)
        
        # API格式演示
        demo_api_format()
        time.sleep(1)
        
        # 分析功能演示
        demo_analysis()
        time.sleep(1)
        
        # 完整工作流程演示
        demo_full_workflow()
        
        print("\n" + "=" * 50)
        print("所有演示完成!")
        print("=" * 50)
        
        print("\n後續可以:")
        print("1. 運行 'python main.py' 進入互動模式")
        print("2. 運行 'python api_server.py' 啟動API服務")
        print("3. 運行 'python llm_example.py simulate 5' 進行批量測試")
        print("4. 運行 './run.sh help' 查看更多選項")
        
    except KeyboardInterrupt:
        print("\n演示被中斷")
    except Exception as e:
        print(f"\n演示過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
