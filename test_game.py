#!/usr/bin/env python3
"""
測試套件 - 驗證遊戲系統各組件
"""

import unittest
import json
from core.models import *
from core.map import GameMap
from core.game_state import GameState
from core.action_engine import ActionEngine
from core.observation_builder import ObservationBuilder


class TestModels(unittest.TestCase):
    """測試基礎模型"""
    
    def test_resources_operations(self):
        """測試資源運算"""
        r1 = Resources(ore=10, wood=20, metal=5, food=15)
        r2 = Resources(ore=5, wood=10, metal=3, food=8)
        
        # 加法
        r3 = r1 + r2
        self.assertEqual(r3.ore, 15)
        self.assertEqual(r3.wood, 30)
        
        # 減法
        r4 = r1 - r2
        self.assertEqual(r4.ore, 5)
        self.assertEqual(r4.wood, 10)
        
        # 乘法
        r5 = r1 * 0.5
        self.assertEqual(r5.ore, 5)
        self.assertEqual(r5.wood, 10)
        
        # 負擔能力檢查
        self.assertTrue(r1.can_afford(r2))
        self.assertFalse(r2.can_afford(r1))
    
    def test_tile_creation(self):
        """測試地塊創建"""
        tile = Tile(x=0, y=0, terrain=TerrainType.MOUNTAIN)
        self.assertEqual(tile.terrain, TerrainType.MOUNTAIN)
        self.assertGreater(tile.resources.ore, 0)  # 山脈應該有礦石
        
        tile2 = Tile(x=1, y=1, terrain=TerrainType.FOREST)
        self.assertGreater(tile2.resources.wood, 0)  # 森林應該有木材
    
    def test_tile_production(self):
        """測試地塊產出"""
        tile = Tile(x=0, y=0, terrain=TerrainType.PLAINS)
        tile.population = 10
        
        production = tile.get_resource_production()
        self.assertGreater(production.food, 0)
        
        # 添加建築後產出應該增加
        tile.buildings.append(BuildingType.FARM)
        production_with_farm = tile.get_resource_production()
        self.assertGreater(production_with_farm.food, production.food)


class TestGameMap(unittest.TestCase):
    """測試遊戲地圖"""
    
    def setUp(self):
        self.game_map = GameMap(width=5, height=5)
    
    def test_map_creation(self):
        """測試地圖創建"""
        self.assertEqual(self.game_map.width, 5)
        self.assertEqual(self.game_map.height, 5)
        self.assertEqual(len(self.game_map.tiles), 25)
        
        # 起始位置應該被控制
        start_tile = self.game_map.get_tile(2, 2)
        self.assertTrue(start_tile.controlled)
        self.assertTrue(start_tile.explored)
    
    def test_neighbors(self):
        """測試相鄰地塊"""
        neighbors = self.game_map.get_neighbors(2, 2)
        self.assertEqual(len(neighbors), 4)  # 中心位置有4個鄰居
        
        # 邊角位置
        corner_neighbors = self.game_map.get_neighbors(0, 0)
        self.assertEqual(len(corner_neighbors), 2)  # 邊角只有2個鄰居
    
    def test_exploration(self):
        """測試探索機制"""
        # 相鄰於起始位置的地塊應該可以探索
        self.assertTrue(self.game_map.can_explore(1, 2))
        self.assertTrue(self.game_map.can_explore(3, 2))
        self.assertTrue(self.game_map.can_explore(2, 1))
        self.assertTrue(self.game_map.can_explore(2, 3))
        
        # 遠離起始位置的地塊不能直接探索
        self.assertFalse(self.game_map.can_explore(0, 0))
        
        # 執行探索
        success = self.game_map.explore_tile(1, 2)
        self.assertTrue(success)
        
        tile = self.game_map.get_tile(1, 2)
        self.assertTrue(tile.explored)


class TestGameState(unittest.TestCase):
    """測試遊戲狀態"""
    
    def setUp(self):
        self.game_state = GameState(map_width=5, map_height=5)
    
    def test_initial_state(self):
        """測試初始狀態"""
        self.assertEqual(self.game_state.turn, 1)
        self.assertEqual(self.game_state.action_points, 5)
        self.assertFalse(self.game_state.game_over)
        self.assertGreater(self.game_state.global_resources.food, 0)
    
    def test_ap_spending(self):
        """測試行動點消耗"""
        initial_ap = self.game_state.action_points
        success = self.game_state.spend_ap(2)
        self.assertTrue(success)
        self.assertEqual(self.game_state.action_points, initial_ap - 2)
        
        # 消耗超出限制
        success = self.game_state.spend_ap(10)
        self.assertFalse(success)
    
    def test_resource_spending(self):
        """測試資源消耗"""
        cost = Resources(wood=10, food=20)
        initial_wood = self.game_state.global_resources.wood
        initial_food = self.game_state.global_resources.food
        
        if self.game_state.can_afford(cost):
            success = self.game_state.spend_resources(cost)
            self.assertTrue(success)
            self.assertEqual(self.game_state.global_resources.wood, initial_wood - 10)
            self.assertEqual(self.game_state.global_resources.food, initial_food - 20)
    
    def test_turn_progression(self):
        """測試回合進展"""
        initial_turn = self.game_state.turn
        self.game_state.next_turn()
        self.assertEqual(self.game_state.turn, initial_turn + 1)
        self.assertEqual(self.game_state.action_points, self.game_state.max_action_points)


class TestActionEngine(unittest.TestCase):
    """測試行動引擎"""
    
    def setUp(self):
        self.game_state = GameState(map_width=5, map_height=5)
        self.action_engine = ActionEngine(self.game_state)
    
    def test_action_parsing(self):
        """測試行動解析"""
        action_data = {
            "action_type": "explore",
            "target_x": 1,
            "target_y": 2
        }
        
        action = self.action_engine.parse_action(action_data)
        self.assertIsNotNone(action)
        self.assertEqual(action.action_type, ActionType.EXPLORE)
        self.assertEqual(action.target_x, 1)
        self.assertEqual(action.target_y, 2)
    
    def test_explore_action(self):
        """測試探索行動"""
        action_data = {
            "action_type": "explore",
            "target_x": 1,
            "target_y": 2
        }
        
        action = self.action_engine.parse_action(action_data)
        result = self.action_engine.execute_action(action)
        
        self.assertTrue(result["success"])
        self.assertIn("discovered", result)
        self.assertIn("terrain", result["discovered"])
    
    def test_build_action(self):
        """測試建造行動"""
        # 先確保有足夠資源
        self.game_state.global_resources.wood = 100
        self.game_state.global_resources.ore = 100
        
        action_data = {
            "action_type": "build",
            "target_x": 2,
            "target_y": 2,  # 起始位置
            "building_type": "farm"
        }
        
        action = self.action_engine.parse_action(action_data)
        result = self.action_engine.execute_action(action)
        
        self.assertTrue(result["success"])
        
        # 檢查建築是否已建造
        tile = self.game_state.game_map.get_tile(2, 2)
        self.assertIn(BuildingType.FARM, tile.buildings)


class TestObservationBuilder(unittest.TestCase):
    """測試觀察構建器"""
    
    def setUp(self):
        self.game_state = GameState(map_width=5, map_height=5)
        self.observation_builder = ObservationBuilder(self.game_state)
    
    def test_observation_building(self):
        """測試觀察構建"""
        observation_str = self.observation_builder.build_observation()
        observation = json.loads(observation_str)
        
        # 檢查必要字段
        self.assertIn("game_info", observation)
        self.assertIn("resources", observation)
        self.assertIn("map_overview", observation)
        self.assertIn("controlled_territories", observation)
        self.assertIn("available_actions", observation)
        
        # 檢查遊戲信息
        game_info = observation["game_info"]
        self.assertEqual(game_info["current_turn"], 1)
        self.assertEqual(game_info["action_points_remaining"], 5)
    
    def test_simple_observation(self):
        """測試簡化觀察"""
        simple_obs_str = self.observation_builder.build_simple_observation()
        simple_obs = json.loads(simple_obs_str)
        
        self.assertIn("turn", simple_obs)
        self.assertIn("ap", simple_obs)
        self.assertIn("resources", simple_obs)
        self.assertIn("controlled_tiles", simple_obs)


class TestGameIntegration(unittest.TestCase):
    """整合測試"""
    
    def test_complete_game_flow(self):
        """測試完整遊戲流程"""
        game_state = GameState(map_width=5, map_height=5)
        action_engine = ActionEngine(game_state)
        observation_builder = ObservationBuilder(game_state)
        
        # 1. 獲取初始觀察
        observation = json.loads(observation_builder.build_observation())
        self.assertEqual(observation["game_info"]["current_turn"], 1)
        
        # 2. 執行一些行動
        actions = [
            {"action_type": "explore", "target_x": 1, "target_y": 2},
            {"action_type": "explore", "target_x": 3, "target_y": 2}
        ]
        
        for action_data in actions:
            action = action_engine.parse_action(action_data)
            result = action_engine.execute_action(action)
            self.assertTrue(result["success"])
        
        # 3. 進入下一回合
        game_state.next_turn()
        self.assertEqual(game_state.turn, 2)
        self.assertEqual(game_state.action_points, 5)  # 行動點應該重置
        
        # 4. 檢查更新後的觀察
        new_observation = json.loads(observation_builder.build_observation())
        self.assertEqual(new_observation["game_info"]["current_turn"], 2)


def run_tests():
    """運行所有測試"""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()
