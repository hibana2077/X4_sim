#!/usr/bin/env python3
"""
交互式 X4 遊戲運行器
支持不同的遊戲模式和自定義設置
"""

import sys
import time
import json
from x4_game import X4Game
import os

class GameRunner:
    def __init__(self):
        self.game = None
        self.api_key = os.getenv('OPENROUTER_API_KEY', 'demo_key')
        
    def display_banner(self):
        print("🎮" + "=" * 60 + "🎮")
        print("           歡迎來到 X4 征服遊戲!")
        print("        多LLM AI策略對戰模擬器")
        print("🎮" + "=" * 60 + "🎮")
        
    def setup_game(self):
        """遊戲設置"""
        print("\n🎯 遊戲設置")
        print("-" * 30)
        
        try:
            players = int(input("玩家數量 (2-6, 預設4): ") or "4")
            players = max(2, min(6, players))
        except ValueError:
            players = 4
            
        try:
            territories = int(input("領土數量 (8-20, 預設12): ") or "12")
            territories = max(8, min(20, territories))
        except ValueError:
            territories = 12
            
        try:
            max_turns = int(input("最大回合數 (5-30, 預設15): ") or "15")
            max_turns = max(5, min(30, max_turns))
        except ValueError:
            max_turns = 15
            
        print(f"\n✅ 設定完成:")
        print(f"   玩家: {players}")
        print(f"   領土: {territories}")
        print(f"   回合: {max_turns}")
        
        if self.api_key == 'demo_key':
            print(f"   AI模式: 簡單AI (未設置OpenRouter API Key)")
        else:
            print(f"   AI模式: 真實LLM對戰 ✨")
            
        return players, territories, max_turns
    
    def choose_game_mode(self):
        """選擇遊戲模式"""
        print("\n🚀 選擇遊戲模式:")
        print("1. 快速演示 (3回合自動)")
        print("2. 自動運行 (全自動到結束)")
        print("3. 回合制 (手動繼續每回合)")
        print("4. 只初始化 (查看初始狀態)")
        print("5. 觀察模式 (慢速自動，詳細顯示)")
        
        try:
            choice = input("\n請選擇 (1-5): ").strip()
            return choice
        except KeyboardInterrupt:
            return "4"
    
    def run_quick_demo(self):
        """快速演示模式"""
        print("\n🏃‍♂️ 快速演示模式 - 3回合")
        players, territories, max_turns = 4, 10, 3
        
        self.game = X4Game(self.api_key)
        self.game.initialize_game(players, territories, max_turns)
        self.game.display_game_state()
        
        for turn in range(max_turns):
            print(f"\n⚡ 快速執行第 {self.game.game_state.turn} 回合...")
            self.game.play_turn()
            time.sleep(1)
            
        self.game.display_game_state()
        
    def run_auto_mode(self, players, territories, max_turns):
        """自動運行模式"""
        print("\n🤖 自動運行模式")
        
        self.game = X4Game(self.api_key)
        self.game.initialize_game(players, territories, max_turns)
        self.game.display_game_state()
        
        while not self.game.game_state.winner and self.game.game_state.turn <= max_turns:
            print(f"\n⏰ 執行第 {self.game.game_state.turn} 回合...")
            self.game.play_turn()
            
            # 簡短狀態更新
            if self.game.game_state.turn % 3 == 0:  # 每3回合顯示一次
                self.display_brief_status()
                
        self.game.display_game_state()
        
    def run_turn_by_turn(self, players, territories, max_turns):
        """回合制模式"""
        print("\n👆 回合制模式 - 按 Enter 繼續下一回合")
        
        self.game = X4Game(self.api_key)
        self.game.initialize_game(players, territories, max_turns)
        self.game.display_game_state()
        
        try:
            while not self.game.game_state.winner and self.game.game_state.turn <= max_turns:
                input(f"\n⏰ 準備執行第 {self.game.game_state.turn} 回合... (按 Enter 繼續, Ctrl+C 退出)")
                self.game.play_turn()
                self.game.display_game_state()
                
                if self.game.game_state.winner:
                    input("\n🎉 遊戲結束！按 Enter 查看最終結果...")
                    
        except KeyboardInterrupt:
            print("\n\n🛑 遊戲被用戶中斷")
            
    def run_observation_mode(self, players, territories, max_turns):
        """觀察模式"""
        print("\n👀 觀察模式 - 慢速詳細顯示")
        
        self.game = X4Game(self.api_key)
        self.game.initialize_game(players, territories, max_turns)
        self.game.display_game_state()
        
        while not self.game.game_state.winner and self.game.game_state.turn <= max_turns:
            print(f"\n{'='*20} 第 {self.game.game_state.turn} 回合開始 {'='*20}")
            
            # 顯示每個玩家的思考過程
            for player_id, player in self.game.game_state.players.items():
                if player.territories_owned:
                    print(f"\n{player.color} {player.name} 正在思考...")
                    time.sleep(1)
                    
            self.game.play_turn()
            self.display_detailed_status()
            time.sleep(3)  # 給時間觀察
            
        self.game.display_game_state()
        
    def display_brief_status(self):
        """簡短狀態顯示"""
        print(f"\n📊 第 {self.game.game_state.turn-1} 回合結果:")
        for player_id, player in self.game.game_state.players.items():
            territories = len(player.territories_owned)
            total_pop = sum(self.game.game_state.territories[tid].population 
                           for tid in player.territories_owned 
                           if tid in self.game.game_state.territories)
            print(f"  {player.color} {player.name}: {territories}領土, {total_pop:,}人口")
            
    def display_detailed_status(self):
        """詳細狀態顯示"""
        print(f"\n📈 詳細狀態 (第 {self.game.game_state.turn-1} 回合後):")
        
        for player_id, player in self.game.game_state.players.items():
            if player.territories_owned:
                print(f"\n{player.color} {player.name}:")
                print(f"  行動: {player.last_action}")
                for territory_id in player.territories_owned:
                    territory = self.game.game_state.territories[territory_id]
                    print(f"  - {territory.name}: {territory.population:,} 人口")
                    
    def show_final_stats(self):
        """顯示最終統計"""
        if not self.game or not self.game.game_state:
            return
            
        print(f"\n📊 最終統計")
        print("-" * 40)
        
        players_stats = []
        for player_id, player in self.game.game_state.players.items():
            territories = len(player.territories_owned)
            total_pop = sum(self.game.game_state.territories[tid].population 
                           for tid in player.territories_owned 
                           if tid in self.game.game_state.territories)
            players_stats.append((player, territories, total_pop))
            
        # 按領土數排序
        players_stats.sort(key=lambda x: x[1], reverse=True)
        
        for i, (player, territories, total_pop) in enumerate(players_stats, 1):
            rank_emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣"][min(i-1, 5)]
            print(f"{rank_emoji} {player.color} {player.name}: {territories} 領土, {total_pop:,} 人口")
            
    def save_game_replay(self):
        """保存遊戲回放"""
        if not self.game or not self.game.game_state:
            return
            
        replay_data = {
            "game_info": {
                "players": len(self.game.game_state.players),
                "territories": len(self.game.game_state.territories),
                "total_turns": self.game.game_state.turn - 1,
                "winner": self.game.game_state.winner
            },
            "game_log": self.game.game_state.game_log,
            "final_state": self.game.game_state.to_dict()
        }
        
        replay_file = f"/Users/lixuanhao/Desktop/專案/X4_sim/game_replay_{int(time.time())}.json"
        with open(replay_file, 'w', encoding='utf-8') as f:
            json.dump(replay_data, f, ensure_ascii=False, indent=2)
            
        print(f"\n💾 遊戲回放已保存到: {replay_file}")
        
    def run(self):
        """主運行函數"""
        self.display_banner()
        
        if self.api_key == 'demo_key':
            print("\n⚠️  未檢測到 OpenRouter API Key")
            print("   設置方法: export OPENROUTER_API_KEY='your_key_here'")
            print("   現在使用簡單AI模式運行演示\n")
        else:
            print(f"\n✅ 檢測到 OpenRouter API Key，使用真實LLM對戰!\n")
            
        try:
            mode = self.choose_game_mode()
            
            if mode == "1":
                self.run_quick_demo()
            elif mode == "2":
                players, territories, max_turns = self.setup_game()
                self.run_auto_mode(players, territories, max_turns)
            elif mode == "3":
                players, territories, max_turns = self.setup_game()
                self.run_turn_by_turn(players, territories, max_turns)
            elif mode == "4":
                players, territories, max_turns = self.setup_game()
                self.game = X4Game(self.api_key)
                self.game.initialize_game(players, territories, max_turns)
                self.game.display_game_state()
                print("\n📋 遊戲已初始化，查看 game_state.yaml 和 game_state.json")
            elif mode == "5":
                players, territories, max_turns = self.setup_game()
                self.run_observation_mode(players, territories, max_turns)
            else:
                print("❌ 無效選擇")
                return
                
            self.show_final_stats()
            self.save_game_replay()
            
        except KeyboardInterrupt:
            print("\n\n👋 感謝遊玩!")
            
        print(f"\n💾 遊戲文件:")
        print(f"   - game_state.yaml (人類可讀)")
        print(f"   - game_state.json (程序數據)")
        print(f"\n🎮 X4 征服遊戲結束!")

if __name__ == "__main__":
    runner = GameRunner()
    runner.run()
