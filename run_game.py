#!/usr/bin/env python3
"""
X4 Conquest Game Runner
Run the game step by step or in full auto mode
"""

import sys
import time
from x4_game import X4Game
import os

def main():
    print("🎮 歡迎來到 X4 征服遊戲!")
    print("=" * 50)
    
    # Check for API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("⚠️  未找到 OpenRouter API Key")
        print("請設置環境變數: export OPENROUTER_API_KEY='your_key_here'")
        print("現在將使用簡單AI模式運行演示")
        api_key = "demo_key"
    else:
        print("✅ 找到 OpenRouter API Key，將使用真實LLM對戰!")
    
    # Initialize game
    game = X4Game(api_key)
    
    print("\n🎯 遊戲設置:")
    print("- 3個AI玩家")
    print("- 12塊領土")
    print("- 15回合限制")
    print("- 人口每回合增長2.5倍")
    print("- 勝利條件: 控制60%領土或50%人口")
    
    game.initialize_game(num_players=3, map_size=12, max_turns=15)
    
    print("\n🚀 遊戲開始!")
    game.display_game_state()
    
    # Game mode selection
    print("選擇遊戲模式:")
    print("1. 自動運行 (全自動)")
    print("2. 回合制 (按Enter繼續)")
    print("3. 只初始化 (查看初始狀態)")
    
    try:
        choice = input("請選擇 (1-3): ").strip()
    except KeyboardInterrupt:
        choice = "3"
    
    if choice == "1":
        # Auto play
        print("\n🤖 自動運行模式...")
        while not game.game_state.winner and game.game_state.turn <= game.game_state.max_turns:
            print(f"\n⏰ 執行第 {game.game_state.turn} 回合...")
            game.play_turn()
            time.sleep(2)  # Pause for readability
            
        game.display_game_state()
        
    elif choice == "2":
        # Turn by turn
        print("\n👆 回合制模式 - 按 Enter 繼續下一回合，Ctrl+C 結束")
        try:
            while not game.game_state.winner and game.game_state.turn <= game.game_state.max_turns:
                input(f"\n⏰ 準備執行第 {game.game_state.turn} 回合... (按 Enter 繼續)")
                game.play_turn()
                game.display_game_state()
        except KeyboardInterrupt:
            print("\n\n🛑 遊戲被用戶中斷")
            
    else:
        print("\n📋 遊戲已初始化，查看以下文件:")
        print("- game_state.yaml (人類可讀)")
        print("- game_state.json (程序使用)")
        print("\n要繼續遊戲，請再次運行此腳本。")
    
    print(f"\n💾 遊戲狀態已保存到:")
    print(f"- game_state.yaml")
    print(f"- game_state.json")
    print(f"\n感謝遊玩! 🎮")

if __name__ == "__main__":
    main()
