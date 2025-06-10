from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import json
from .models import ActionType, BuildingType, Resources
from .game_state import GameState


@dataclass
class Action:
    """行動類"""
    action_type: ActionType
    target_x: Optional[int] = None
    target_y: Optional[int] = None
    building_type: Optional[BuildingType] = None
    amount: Optional[int] = None
    parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


class ActionEngine:
    """行動引擎 - 處理LLM指令並執行"""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        
        # 建築成本
        self.building_costs = {
            BuildingType.MINE: Resources(wood=20, metal=10),
            BuildingType.LUMBER_MILL: Resources(wood=15, metal=5),
            BuildingType.FARM: Resources(wood=10, ore=5),
            BuildingType.SMELTER: Resources(wood=25, ore=15),
            BuildingType.HOUSE: Resources(wood=15, ore=5)
        }
    
    def parse_action(self, action_data: Dict[str, Any]) -> Optional[Action]:
        """解析行動數據"""
        try:
            action_type_str = action_data.get("action_type", "").lower()
            action_type = None
            
            # 解析行動類型
            for at in ActionType:
                if at.value == action_type_str:
                    action_type = at
                    break
            
            if not action_type:
                return None
            
            # 解析建築類型
            building_type = None
            building_type_str = action_data.get("building_type", "")
            if building_type_str:
                for bt in BuildingType:
                    if bt.value == building_type_str.lower():
                        building_type = bt
                        break
            
            return Action(
                action_type=action_type,
                target_x=action_data.get("target_x"),
                target_y=action_data.get("target_y"),
                building_type=building_type,
                amount=action_data.get("amount"),
                parameters=action_data.get("parameters", {})
            )
        except Exception as e:
            print(f"解析行動時發生錯誤: {e}")
            return None
    
    def execute_action(self, action: Action) -> Dict[str, Any]:
        """執行行動"""
        if self.game_state.game_over:
            return {"success": False, "message": "遊戲已結束"}
        
        if action.action_type == ActionType.EXPLORE:
            return self._execute_explore(action)
        elif action.action_type == ActionType.EXPAND:
            return self._execute_expand(action)
        elif action.action_type == ActionType.EXPLOIT:
            return self._execute_exploit(action)
        elif action.action_type == ActionType.BUILD:
            return self._execute_build(action)
        elif action.action_type == ActionType.RESEARCH:
            return self._execute_research(action)
        elif action.action_type == ActionType.MIGRATE:
            return self._execute_migrate(action)
        else:
            return {"success": False, "message": f"未知的行動類型: {action.action_type}"}
    
    def _execute_explore(self, action: Action) -> Dict[str, Any]:
        """執行探索行動"""
        if not self.game_state.spend_ap(1):
            return {"success": False, "message": "行動點不足"}
        
        if action.target_x is None or action.target_y is None:
            return {"success": False, "message": "探索需要指定目標座標"}
        
        if not self.game_state.game_map.can_explore(action.target_x, action.target_y):
            return {"success": False, "message": "無法探索該位置"}
        
        success = self.game_state.game_map.explore_tile(action.target_x, action.target_y)
        if success:
            self.game_state.stats["tiles_explored"] += 1
            tile = self.game_state.game_map.get_tile(action.target_x, action.target_y)
            return {
                "success": True,
                "message": f"成功探索了位置 ({action.target_x}, {action.target_y})",
                "discovered": {
                    "terrain": tile.terrain.value,
                    "resources": tile.resources.to_dict(),
                    "population": tile.population
                }
            }
        else:
            return {"success": False, "message": "探索失敗"}
    
    def _execute_expand(self, action: Action) -> Dict[str, Any]:
        """執行擴張行動"""
        if not self.game_state.spend_ap(2):
            return {"success": False, "message": "行動點不足"}
        
        if action.target_x is None or action.target_y is None:
            return {"success": False, "message": "擴張需要指定目標座標"}
        
        if not self.game_state.game_map.can_expand_to(action.target_x, action.target_y):
            return {"success": False, "message": "無法擴張到該位置"}
        
        # 擴張成本
        expansion_cost = Resources(food=20, wood=10)
        if not self.game_state.spend_resources(expansion_cost):
            return {"success": False, "message": "資源不足以擴張"}
        
        success = self.game_state.game_map.expand_to_tile(action.target_x, action.target_y)
        if success:
            self.game_state.stats["tiles_expanded"] += 1
            return {
                "success": True,
                "message": f"成功擴張到位置 ({action.target_x}, {action.target_y})",
                "cost": expansion_cost.to_dict()
            }
        else:
            return {"success": False, "message": "擴張失敗"}
    
    def _execute_exploit(self, action: Action) -> Dict[str, Any]:
        """執行開發行動（額外資源採集）"""
        if not self.game_state.spend_ap(1):
            return {"success": False, "message": "行動點不足"}
        
        if action.target_x is None or action.target_y is None:
            return {"success": False, "message": "開發需要指定目標座標"}
        
        tile = self.game_state.game_map.get_tile(action.target_x, action.target_y)
        if not tile or not tile.controlled:
            return {"success": False, "message": "只能開發受控制的地塊"}
        
        # 額外採集資源
        bonus_resources = tile.get_resource_production() * 0.5
        self.game_state.global_resources = self.game_state.global_resources + bonus_resources
        
        return {
            "success": True,
            "message": f"成功開發位置 ({action.target_x}, {action.target_y})",
            "gained_resources": bonus_resources.to_dict()
        }
    
    def _execute_build(self, action: Action) -> Dict[str, Any]:
        """執行建造行動"""
        if not self.game_state.spend_ap(2):
            return {"success": False, "message": "行動點不足"}
        
        if action.target_x is None or action.target_y is None:
            return {"success": False, "message": "建造需要指定目標座標"}
        
        if not action.building_type:
            return {"success": False, "message": "建造需要指定建築類型"}
        
        tile = self.game_state.game_map.get_tile(action.target_x, action.target_y)
        if not tile or not tile.controlled:
            return {"success": False, "message": "只能在受控制的地塊建造"}
        
        if not tile.can_build(action.building_type):
            return {"success": False, "message": "無法在此地塊建造該建築"}
        
        # 檢查建造成本
        cost = self.building_costs.get(action.building_type, Resources())
        if not self.game_state.spend_resources(cost):
            return {"success": False, "message": "資源不足以建造"}
        
        # 建造建築
        tile.buildings.append(action.building_type)
        self.game_state.stats["buildings_built"] += 1
        
        # 特殊建築效果
        if action.building_type == BuildingType.HOUSE:
            tile.max_population += 50
        
        return {
            "success": True,
            "message": f"成功建造了{action.building_type.value}",
            "cost": cost.to_dict()
        }
    
    def _execute_research(self, action: Action) -> Dict[str, Any]:
        """執行研究行動"""
        if not self.game_state.spend_ap(3):
            return {"success": False, "message": "行動點不足"}
        
        # 簡化的研究系統
        research_cost = Resources(metal=15, food=10)
        if not self.game_state.spend_resources(research_cost):
            return {"success": False, "message": "資源不足以進行研究"}
        
        self.game_state.research_points += 10
        
        # 解鎖技術
        technologies = ["高效農業", "先進採礦", "金屬冶煉", "人口管理"]
        available_tech = [tech for tech in technologies if tech not in self.game_state.technologies]
        
        if available_tech and self.game_state.research_points >= 30:
            new_tech = available_tech[0]
            self.game_state.technologies.append(new_tech)
            self.game_state.research_points -= 30
            return {
                "success": True,
                "message": f"研究成功，解鎖了技術：{new_tech}",
                "technology": new_tech,
                "cost": research_cost.to_dict()
            }
        else:
            return {
                "success": True,
                "message": "研究進展順利，獲得了研究點數",
                "research_points": self.game_state.research_points,
                "cost": research_cost.to_dict()
            }
    
    def _execute_migrate(self, action: Action) -> Dict[str, Any]:
        """執行遷移行動"""
        if not self.game_state.spend_ap(1):
            return {"success": False, "message": "行動點不足"}
        
        # 簡化的遷移系統 - 在受控地塊間移動人口
        controlled_tiles = self.game_state.game_map.get_controlled_tiles()
        if len(controlled_tiles) < 2:
            return {"success": False, "message": "需要至少控制2個地塊才能遷移"}
        
        # 找到人口最多和最少的地塊
        max_pop_tile = max(controlled_tiles, key=lambda t: t.population)
        min_pop_tile = min(controlled_tiles, key=lambda t: t.population)
        
        if max_pop_tile.population > min_pop_tile.population + 5:
            migrate_amount = min(5, max_pop_tile.population // 4)
            max_pop_tile.population -= migrate_amount
            min_pop_tile.population = min(min_pop_tile.max_population, 
                                        min_pop_tile.population + migrate_amount)
            
            return {
                "success": True,
                "message": f"成功遷移了{migrate_amount}人口",
                "from": (max_pop_tile.x, max_pop_tile.y),
                "to": (min_pop_tile.x, min_pop_tile.y),
                "amount": migrate_amount
            }
        else:
            return {"success": False, "message": "沒有適合的遷移目標"}
    
    def execute_actions(self, actions_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """執行多個行動"""
        results = []
        
        for action_data in actions_data:
            action = self.parse_action(action_data)
            if action:
                result = self.execute_action(action)
                results.append(result)
            else:
                results.append({"success": False, "message": "無法解析行動"})
                
            # 如果行動點用完，停止執行
            if self.game_state.action_points <= 0:
                break
        
        return results
