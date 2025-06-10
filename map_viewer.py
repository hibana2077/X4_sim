#!/usr/bin/env python3
"""
X4遊戲地圖可視化工具
生成ASCII地圖和統計圖表
"""

import json
import yaml
from typing import Dict, List
import os

class MapVisualizer:
    def __init__(self, game_state_file: str = "game_state.yaml"):
        self.game_state_file = game_state_file
        self.game_state = None
        self.load_game_state()
        
    def load_game_state(self):
        """載入遊戲狀態"""
        try:
            if self.game_state_file.endswith('.yaml'):
                with open(self.game_state_file, 'r', encoding='utf-8') as f:
                    self.game_state = yaml.safe_load(f)
            else:
                with open(self.game_state_file, 'r', encoding='utf-8') as f:
                    self.game_state = json.load(f)
        except FileNotFoundError:
            print(f"❌ 找不到遊戲狀態文件: {self.game_state_file}")
            return False
        return True
    
    def get_terrain_emoji(self, terrain_type: str) -> str:
        """獲取地形emoji"""
        terrain_map = {
            "plains": "🌾",
            "forest": "🌲", 
            "mountain": "⛰️",
            "coast": "🏖️",
            "desert": "🏜️"
        }
        return terrain_map.get(terrain_type, "❓")
    
    def get_player_color_emoji(self, player_id: str) -> str:
        """獲取玩家顏色emoji"""
        if not player_id or player_id not in self.game_state['players']:
            return "⚪"  # 未佔領
        return self.game_state['players'][player_id]['color']
    
    def display_territory_grid(self):
        """顯示領土網格地圖"""
        if not self.game_state:
            return
            
        print("🗺️  領土地圖")
        print("=" * 60)
        
        territories = self.game_state['territories']
        territory_list = list(territories.items())
        
        # 創建4x3網格 (可調整)
        cols = 4
        rows = (len(territory_list) + cols - 1) // cols
        
        for row in range(rows):
            # 領土名稱行
            name_line = ""
            for col in range(cols):
                idx = row * cols + col
                if idx < len(territory_list):
                    territory_id, territory = territory_list[idx]
                    owner_emoji = self.get_player_color_emoji(territory.get('owner'))
                    terrain_emoji = self.get_terrain_emoji(territory['terrain_type'])
                    name = territory['name'].split('(')[0].strip()[:12]
                    name_line += f"{owner_emoji}{terrain_emoji} {name:<12} "
                else:
                    name_line += " " * 17
            print(name_line)
            
            # 人口信息行
            pop_line = ""
            for col in range(cols):
                idx = row * cols + col
                if idx < len(territory_list):
                    territory_id, territory = territory_list[idx]
                    pop = territory['population']
                    if pop >= 1000:
                        pop_str = f"{pop//1000}K"
                    else:
                        pop_str = str(pop)
                    pop_line += f"   {pop_str:<12} "
                else:
                    pop_line += " " * 17
            print(pop_line)
            
            # 分隔線
            if row < rows - 1:
                print("-" * 60)
    
    def display_player_territories(self):
        """顯示各玩家的領土詳情"""
        if not self.game_state:
            return
            
        print(f"\n👥 玩家領土詳情 (第 {self.game_state['turn']} 回合)")
        print("=" * 60)
        
        for player_id, player in self.game_state['players'].items():
            if not player['territories_owned']:
                continue
                
            print(f"\n{player['color']} {player['name']}")
            print(f"最後行動: {player.get('last_action', '無')}")
            print("-" * 30)
            
            total_pop = 0
            for territory_id in player['territories_owned']:
                if territory_id in self.game_state['territories']:
                    territory = self.game_state['territories'][territory_id]
                    terrain_emoji = self.get_terrain_emoji(territory['terrain_type'])
                    pop = territory['population']
                    total_pop += pop
                    
                    # 計算容量使用率
                    size = territory['size']
                    terrain_multipliers = {
                        "plains": 1.2, "forest": 1.0, "mountain": 0.7,
                        "coast": 1.1, "desert": 0.6
                    }
                    capacity = int(size * 1000 * terrain_multipliers.get(territory['terrain_type'], 1.0))
                    usage_pct = (pop / capacity * 100) if capacity > 0 else 0
                    
                    print(f"  {terrain_emoji} {territory['name']:<20} {pop:>6,} 人口 ({usage_pct:.0f}%)")
            
            print(f"  {'總計':<23} {total_pop:>6,} 人口")
    
    def display_game_statistics(self):
        """顯示遊戲統計"""
        if not self.game_state:
            return
            
        print(f"\n📊 遊戲統計")
        print("=" * 40)
        
        # 基本信息
        print(f"回合: {self.game_state['turn']}/{self.game_state['max_turns']}")
        
        # 玩家統計
        player_stats = []
        total_pop = 0
        total_territories = len(self.game_state['territories'])
        
        for player_id, player in self.game_state['players'].items():
            territories_count = len(player['territories_owned'])
            player_pop = sum(
                self.game_state['territories'][tid]['population']
                for tid in player['territories_owned']
                if tid in self.game_state['territories']
            )
            total_pop += player_pop
            player_stats.append((player, territories_count, player_pop))
        
        # 按領土數排序
        player_stats.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n排名:")
        for i, (player, territories, pop) in enumerate(player_stats, 1):
            territory_pct = (territories / total_territories * 100) if total_territories > 0 else 0
            pop_pct = (pop / total_pop * 100) if total_pop > 0 else 0
            print(f"{i}. {player['color']} {player['name']}: "
                  f"{territories}領土({territory_pct:.0f}%) "
                  f"{pop:,}人口({pop_pct:.0f}%)")
        
        # 地形統計
        terrain_count = {}
        for territory in self.game_state['territories'].values():
            terrain = territory['terrain_type']
            terrain_count[terrain] = terrain_count.get(terrain, 0) + 1
        
        print(f"\n地形分布:")
        for terrain, count in terrain_count.items():
            emoji = self.get_terrain_emoji(terrain)
            print(f"  {emoji} {terrain}: {count} 塊")
    
    def display_recent_events(self):
        """顯示近期事件"""
        if not self.game_state or 'game_log' not in self.game_state:
            return
            
        print(f"\n📜 近期事件")
        print("=" * 50)
        
        # 顯示最近10個事件
        recent_events = self.game_state['game_log'][-10:]
        for event in recent_events:
            print(f"  {event}")
    
    def generate_progress_chart(self):
        """生成進度圖表（ASCII版本）"""
        if not self.game_state:
            return
            
        print(f"\n📈 領土控制進度")
        print("=" * 50)
        
        total_territories = len(self.game_state['territories'])
        
        for player_id, player in self.game_state['players'].items():
            if not player['territories_owned']:
                continue
                
            territories = len(player['territories_owned'])
            percentage = territories / total_territories
            bar_length = 30
            filled_length = int(bar_length * percentage)
            
            bar = "█" * filled_length + "░" * (bar_length - filled_length)
            print(f"{player['color']} {player['name']:<10} |{bar}| {territories:>2}/{total_territories} ({percentage*100:.1f}%)")
    
    def save_map_report(self):
        """保存地圖報告到文件"""
        if not self.game_state:
            return
            
        import io
        import sys
        from contextlib import redirect_stdout
        
        report_file = f"/Users/lixuanhao/Desktop/專案/X4_sim/map_report_turn_{self.game_state['turn']}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            with redirect_stdout(f):
                print(f"X4征服遊戲地圖報告 - 第 {self.game_state['turn']} 回合")
                print("=" * 60)
                print()
                
                self.display_game_statistics()
                print()
                self.display_player_territories()
                print()
                self.display_territory_grid()
                print()
                self.generate_progress_chart()
                print()
                self.display_recent_events()
        
        print(f"📋 地圖報告已保存到: {report_file}")
    
    def interactive_map_viewer(self):
        """交互式地圖查看器"""
        if not self.game_state:
            print("❌ 無法載入遊戲狀態")
            return
            
        while True:
            print(f"\n🗺️  X4地圖查看器 - 第 {self.game_state['turn']} 回合")
            print("=" * 40)
            print("1. 顯示領土地圖")
            print("2. 顯示玩家詳情")
            print("3. 顯示遊戲統計")
            print("4. 顯示進度圖表")
            print("5. 顯示近期事件")
            print("6. 保存報告")
            print("7. 重新載入狀態")
            print("0. 退出")
            
            try:
                choice = input("\n請選擇 (0-7): ").strip()
                
                if choice == "1":
                    self.display_territory_grid()
                elif choice == "2":
                    self.display_player_territories()
                elif choice == "3":
                    self.display_game_statistics()
                elif choice == "4":
                    self.generate_progress_chart()
                elif choice == "5":
                    self.display_recent_events()
                elif choice == "6":
                    self.save_map_report()
                elif choice == "7":
                    if self.load_game_state():
                        print("✅ 遊戲狀態已重新載入")
                    else:
                        print("❌ 載入失敗")
                elif choice == "0":
                    print("👋 退出地圖查看器")
                    break
                else:
                    print("❌ 無效選擇")
                    
            except KeyboardInterrupt:
                print("\n👋 退出地圖查看器")
                break

def main():
    print("🗺️  X4遊戲地圖可視化工具")
    
    # 檢查遊戲狀態文件
    state_files = ["game_state.yaml", "game_state.json"]
    available_files = [f for f in state_files if os.path.exists(f)]
    
    if not available_files:
        print("❌ 找不到遊戲狀態文件")
        print("請先運行遊戲生成 game_state.yaml 或 game_state.json")
        return
    
    # 使用第一個可用文件
    visualizer = MapVisualizer(available_files[0])
    visualizer.interactive_map_viewer()

if __name__ == "__main__":
    main()
