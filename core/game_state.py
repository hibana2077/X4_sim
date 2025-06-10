from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import random
from enum import Enum
from .models import Resources, BuildingType
from .map import GameMap


class EventType(Enum):
    """事件類型"""
    DROUGHT = "drought"      # 乾旱
    PLAGUE = "plague"        # 瘟疫
    HARVEST = "harvest"      # 豐收
    DISCOVERY = "discovery"  # 發現


@dataclass
class GameEvent:
    """遊戲事件"""
    event_type: EventType
    description: str
    effects: Dict[str, Any] = field(default_factory=dict)
    duration: int = 1  # 持續回合數


class GameState:
    """遊戲狀態管理類"""
    
    def __init__(self, map_width: int = 10, map_height: int = 10):
        self.turn: int = 1
        self.max_turns: int = 100
        self.action_points: int = 5
        self.max_action_points: int = 5
        
        # 全域資源庫
        self.global_resources = Resources(ore=50, wood=50, metal=20, food=100)
        
        # 地圖
        self.game_map = GameMap(map_width, map_height)
        
        # 事件系統
        self.active_events: List[GameEvent] = []
        self.event_history: List[GameEvent] = []
        
        # 研究點數和技術
        self.research_points: int = 0
        self.technologies: List[str] = []
        
        # 遊戲結束標誌
        self.game_over: bool = False
        self.victory: bool = False
        
        # 統計數據
        self.stats = {
            "total_ap_used": 0,
            "total_resources_gathered": Resources(),
            "buildings_built": 0,
            "tiles_explored": 0,
            "tiles_expanded": 0,
            "starvation_events": 0
        }
    
    def next_turn(self):
        """進入下一回合"""
        if self.game_over:
            return
        
        # 重置行動點
        self.action_points = self.max_action_points
        
        # 資源產出
        production = self.game_map.get_total_production()
        self.global_resources = self.global_resources + production
        self.stats["total_resources_gathered"] = self.stats["total_resources_gathered"] + production
        
        # 糧食消耗
        food_consumption = self.game_map.get_total_food_consumption()
        self.global_resources.food = max(0, self.global_resources.food - food_consumption)
        
        # 檢查飢荒
        if self.global_resources.food <= 0:
            self._handle_starvation()
        
        # 人口增長
        self._handle_population_growth()
        
        # 處理事件
        self._process_events()
        
        # 隨機事件
        if random.random() < 0.15:  # 15% 機率觸發事件
            self._trigger_random_event()
        
        # 增加回合數
        self.turn += 1
        
        # 檢查遊戲結束條件
        self._check_end_conditions()
    
    def _handle_starvation(self):
        """處理飢荒"""
        self.stats["starvation_events"] += 1
        
        # 減少人口
        controlled_tiles = self.game_map.get_controlled_tiles()
        for tile in controlled_tiles:
            if tile.population > 0:
                population_loss = max(1, tile.population // 10)
                tile.population = max(0, tile.population - population_loss)
        
        # 添加飢荒事件
        event = GameEvent(
            event_type=EventType.PLAGUE,
            description="飢荒導致人口減少",
            effects={"population_loss": True}
        )
        self.event_history.append(event)
    
    def _handle_population_growth(self):
        """處理人口增長"""
        if self.global_resources.food > 50:  # 有足夠糧食才增長
            controlled_tiles = self.game_map.get_controlled_tiles()
            for tile in controlled_tiles:
                if tile.population < tile.max_population:
                    growth_rate = 0.02  # 2% 基礎增長率
                    
                    # 房屋增加增長率
                    if BuildingType.HOUSE in tile.buildings:
                        growth_rate += 0.01
                    
                    growth = max(1, int(tile.population * growth_rate))
                    tile.population = min(tile.max_population, tile.population + growth)
    
    def _process_events(self):
        """處理活躍事件"""
        for event in self.active_events[:]:
            event.duration -= 1
            if event.duration <= 0:
                self.active_events.remove(event)
                self.event_history.append(event)
    
    def _trigger_random_event(self):
        """觸發隨機事件"""
        event_types = [
            (EventType.DROUGHT, "乾旱減少了糧食產出", {"food_reduction": 0.5}),
            (EventType.HARVEST, "豐收增加了糧食產出", {"food_bonus": 50}),
            (EventType.DISCOVERY, "發現了新的礦脈", {"ore_bonus": 30}),
            (EventType.PLAGUE, "瘟疫減少了人口", {"population_reduction": 0.1})
        ]
        
        event_type, description, effects = random.choice(event_types)
        event = GameEvent(
            event_type=event_type,
            description=description,
            effects=effects,
            duration=random.randint(1, 3)
        )
        
        self.active_events.append(event)
        
        # 立即應用效果
        if event_type == EventType.HARVEST:
            self.global_resources.food += effects.get("food_bonus", 0)
        elif event_type == EventType.DISCOVERY:
            self.global_resources.ore += effects.get("ore_bonus", 0)
    
    def _check_end_conditions(self):
        """檢查遊戲結束條件"""
        # 達到最大回合數
        if self.turn >= self.max_turns:
            self.game_over = True
            return
        
        # 勝利條件：累積1000金屬
        if self.global_resources.metal >= 1000:
            self.game_over = True
            self.victory = True
            return
        
        # 失敗條件：所有人口死亡
        if self.game_map.get_total_population() <= 0:
            self.game_over = True
            return
    
    def spend_ap(self, cost: int = 1) -> bool:
        """消耗行動點"""
        if self.action_points >= cost:
            self.action_points -= cost
            self.stats["total_ap_used"] += cost
            return True
        return False
    
    def can_afford(self, cost: Resources) -> bool:
        """檢查是否負擔得起資源消耗"""
        return self.global_resources.can_afford(cost)
    
    def spend_resources(self, cost: Resources) -> bool:
        """消耗資源"""
        if self.can_afford(cost):
            self.global_resources = self.global_resources - cost
            return True
        return False
    
    def get_score(self) -> Dict[str, float]:
        """計算評分"""
        # 資源效率
        total_ap = max(1, self.stats["total_ap_used"])
        total_resources = (self.stats["total_resources_gathered"].ore + 
                         self.stats["total_resources_gathered"].wood + 
                         self.stats["total_resources_gathered"].metal + 
                         self.stats["total_resources_gathered"].food)
        resource_efficiency = total_resources / total_ap
        
        # 人口健康度
        max_possible_population = len(self.game_map.get_controlled_tiles()) * 100
        current_population = self.game_map.get_total_population()
        population_health = current_population / max(1, max_possible_population)
        
        # 目標達成度
        goal_completion = min(1.0, self.global_resources.metal / 1000)
        
        # 策略多樣性（根據統計數據）
        diversity_score = 0.0
        if self.stats["tiles_explored"] > 0:
            diversity_score += 0.25
        if self.stats["tiles_expanded"] > 0:
            diversity_score += 0.25
        if self.stats["buildings_built"] > 0:
            diversity_score += 0.25
        if len(self.technologies) > 0:
            diversity_score += 0.25
        
        return {
            "resource_efficiency": resource_efficiency,
            "population_health": population_health,
            "goal_completion": goal_completion,
            "strategy_diversity": diversity_score,
            "total_score": (resource_efficiency * 0.3 + 
                          population_health * 0.2 + 
                          goal_completion * 0.4 + 
                          diversity_score * 0.1)
        }
    
    def to_dict(self) -> Dict:
        """轉換為字典格式"""
        return {
            "turn": self.turn,
            "max_turns": self.max_turns,
            "action_points": self.action_points,
            "max_action_points": self.max_action_points,
            "global_resources": self.global_resources.to_dict(),
            "research_points": self.research_points,
            "technologies": self.technologies,
            "game_over": self.game_over,
            "victory": self.victory,
            "active_events": [
                {
                    "type": event.event_type.value,
                    "description": event.description,
                    "duration": event.duration
                } for event in self.active_events
            ],
            "recent_events": [
                {
                    "type": event.event_type.value,
                    "description": event.description
                } for event in self.event_history[-3:]  # 最近3個事件
            ],
            "map": self.game_map.to_dict(),
            "stats": {
                "total_ap_used": self.stats["total_ap_used"],
                "total_resources_gathered": self.stats["total_resources_gathered"].to_dict(),
                "buildings_built": self.stats["buildings_built"],
                "tiles_explored": self.stats["tiles_explored"],
                "tiles_expanded": self.stats["tiles_expanded"],
                "starvation_events": self.stats["starvation_events"]
            },
            "score": self.get_score()
        }
