import json
import yaml
from typing import Dict, Any, List, Optional
from .game_state import GameState
from .map import GameMap


class ObservationBuilder:
    """觀察構建器 - 將遊戲狀態格式化為LLM可讀格式"""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
    
    def build_observation(self, format_type: str = "json") -> str:
        """構建觀察"""
        observation_data = self._build_observation_data()
        
        if format_type.lower() == "yaml":
            return yaml.dump(observation_data, default_flow_style=False, allow_unicode=True)
        else:
            return json.dumps(observation_data, indent=2, ensure_ascii=False)
    
    def _build_observation_data(self) -> Dict[str, Any]:
        """構建觀察數據"""
        return {
            "game_info": self._build_game_info(),
            "resources": self._build_resource_info(),
            "map_overview": self._build_map_overview(),
            "controlled_territories": self._build_controlled_territories(),
            "available_actions": self._build_available_actions(),
            "events": self._build_events_info(),
            "objectives": self._build_objectives(),
            "statistics": self._build_statistics()
        }
    
    def _build_game_info(self) -> Dict[str, Any]:
        """構建遊戲基本信息"""
        return {
            "current_turn": self.game_state.turn,
            "max_turns": self.game_state.max_turns,
            "action_points_remaining": self.game_state.action_points,
            "max_action_points": self.game_state.max_action_points,
            "game_over": self.game_state.game_over,
            "victory": self.game_state.victory
        }
    
    def _build_resource_info(self) -> Dict[str, Any]:
        """構建資源信息"""
        total_production = self.game_state.game_map.get_total_production()
        total_consumption = self.game_state.game_map.get_total_food_consumption()
        
        return {
            "current_resources": self.game_state.global_resources.to_dict(),
            "production_per_turn": total_production.to_dict(),
            "food_consumption_per_turn": total_consumption,
            "net_food_change": total_production.food - total_consumption,
            "research_points": self.game_state.research_points,
            "technologies": self.game_state.technologies
        }
    
    def _build_map_overview(self) -> Dict[str, Any]:
        """構建地圖概覽"""
        controlled_tiles = self.game_state.game_map.get_controlled_tiles()
        explored_tiles = self.game_state.game_map.get_explored_tiles()
        
        # 獲取邊界信息（可探索和可擴張的地塊）
        explorable = []
        expandable = []
        
        for x in range(self.game_state.game_map.width):
            for y in range(self.game_state.game_map.height):
                if self.game_state.game_map.can_explore(x, y):
                    explorable.append((x, y))
                elif self.game_state.game_map.can_expand_to(x, y):
                    expandable.append((x, y))
        
        return {
            "map_size": {
                "width": self.game_state.game_map.width,
                "height": self.game_state.game_map.height
            },
            "controlled_tiles_count": len(controlled_tiles),
            "explored_tiles_count": len(explored_tiles),
            "total_population": self.game_state.game_map.get_total_population(),
            "explorable_positions": explorable[:10],  # 限制數量避免過長
            "expandable_positions": expandable[:10]
        }
    
    def _build_controlled_territories(self) -> List[Dict[str, Any]]:
        """構建受控領土信息"""
        controlled_tiles = self.game_state.game_map.get_controlled_tiles()
        territories = []
        
        for tile in controlled_tiles:
            territory_info = {
                "position": {"x": tile.x, "y": tile.y},
                "terrain": tile.terrain.value,
                "population": tile.population,
                "max_population": tile.max_population,
                "buildings": [building.value for building in tile.buildings],
                "resource_production": tile.get_resource_production().to_dict(),
                "food_consumption": tile.get_food_consumption(),
                "available_resources": tile.resources.to_dict()
            }
            territories.append(territory_info)
        
        return territories
    
    def _build_available_actions(self) -> Dict[str, Any]:
        """構建可用行動信息"""
        return {
            "action_types": [
                {
                    "type": "explore",
                    "cost": 1,
                    "description": "探索新地塊",
                    "parameters": ["target_x", "target_y"]
                },
                {
                    "type": "expand", 
                    "cost": 2,
                    "description": "擴張到已探索地塊",
                    "parameters": ["target_x", "target_y"],
                    "resource_cost": {"food": 20, "wood": 10}
                },
                {
                    "type": "exploit",
                    "cost": 1,
                    "description": "額外開發地塊資源",
                    "parameters": ["target_x", "target_y"]
                },
                {
                    "type": "build",
                    "cost": 2,
                    "description": "建造建築",
                    "parameters": ["target_x", "target_y", "building_type"],
                    "building_types": [
                        {"type": "mine", "cost": {"wood": 20, "metal": 10}, "effect": "增加礦石產出"},
                        {"type": "lumber_mill", "cost": {"wood": 15, "metal": 5}, "effect": "增加木材產出"},
                        {"type": "farm", "cost": {"wood": 10, "ore": 5}, "effect": "增加糧食產出"},
                        {"type": "smelter", "cost": {"wood": 25, "ore": 15}, "effect": "將礦石轉換為金屬"},
                        {"type": "house", "cost": {"wood": 15, "ore": 5}, "effect": "增加人口容量"}
                    ]
                },
                {
                    "type": "research",
                    "cost": 3,
                    "description": "進行技術研究",
                    "resource_cost": {"metal": 15, "food": 10}
                },
                {
                    "type": "migrate",
                    "cost": 1,
                    "description": "在地塊間遷移人口"
                }
            ]
        }
    
    def _build_events_info(self) -> Dict[str, Any]:
        """構建事件信息"""
        return {
            "active_events": [
                {
                    "type": event.event_type.value,
                    "description": event.description,
                    "remaining_duration": event.duration
                } for event in self.game_state.active_events
            ],
            "recent_events": [
                {
                    "type": event.event_type.value,
                    "description": event.description
                } for event in self.game_state.event_history[-5:]  # 最近5個事件
            ]
        }
    
    def _build_objectives(self) -> Dict[str, Any]:
        """構建目標信息"""
        metal_progress = min(1.0, self.game_state.global_resources.metal / 1000)
        
        return {
            "primary_objective": {
                "description": "累積1000金屬以獲得勝利",
                "current_progress": self.game_state.global_resources.metal,
                "target": 1000,
                "completion_percentage": metal_progress * 100
            },
            "secondary_objectives": [
                {
                    "description": "維持人口增長",
                    "current": self.game_state.game_map.get_total_population()
                },
                {
                    "description": "避免飢荒事件",
                    "starvation_events": self.game_state.stats["starvation_events"]
                },
                {
                    "description": "探索更多領土",
                    "explored_tiles": self.game_state.stats["tiles_explored"]
                }
            ]
        }
    
    def _build_statistics(self) -> Dict[str, Any]:
        """構建統計信息"""
        score = self.game_state.get_score()
        
        return {
            "performance_metrics": score,
            "resource_efficiency": f"{score['resource_efficiency']:.2f} 資源/AP",
            "population_health": f"{score['population_health']:.2%}",
            "goal_completion": f"{score['goal_completion']:.2%}",
            "strategy_diversity": f"{score['strategy_diversity']:.2%}",
            "total_score": f"{score['total_score']:.2f}",
            "detailed_stats": {
                "total_ap_used": self.game_state.stats["total_ap_used"],
                "buildings_built": self.game_state.stats["buildings_built"],
                "tiles_explored": self.game_state.stats["tiles_explored"],
                "tiles_expanded": self.game_state.stats["tiles_expanded"],
                "starvation_events": self.game_state.stats["starvation_events"]
            }
        }
    
    def build_simple_observation(self) -> str:
        """構建簡化觀察（用於快速查看）"""
        data = {
            "turn": self.game_state.turn,
            "ap": self.game_state.action_points,
            "resources": self.game_state.global_resources.to_dict(),
            "controlled_tiles": len(self.game_state.game_map.get_controlled_tiles()),
            "population": self.game_state.game_map.get_total_population(),
            "game_over": self.game_state.game_over,
            "victory": self.game_state.victory
        }
        return json.dumps(data, indent=2, ensure_ascii=False)
