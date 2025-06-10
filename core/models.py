from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import random
import json
import yaml


class TerrainType(Enum):
    """地形類型"""
    PLAINS = "plains"      # 平原 - 適合農業
    FOREST = "forest"      # 森林 - 木材豐富
    MOUNTAIN = "mountain"  # 山脈 - 礦石豐富
    LAKE = "lake"         # 湖泊 - 提供水源


class ResourceType(Enum):
    """資源類型"""
    ORE = "ore"           # 礦石
    WOOD = "wood"         # 木材  
    METAL = "metal"       # 金屬
    FOOD = "food"         # 糧食


class BuildingType(Enum):
    """建築類型"""
    MINE = "mine"           # 礦場 - 提升礦石產出
    LUMBER_MILL = "lumber_mill"  # 伐木場 - 提升木材產出
    FARM = "farm"           # 農場 - 提升糧食產出
    SMELTER = "smelter"     # 冶煉廠 - 將礦石轉換為金屬
    HOUSE = "house"         # 房屋 - 增加人口容量


class ActionType(Enum):
    """行動類型"""
    EXPLORE = "explore"     # 探索
    EXPAND = "expand"       # 擴張
    EXPLOIT = "exploit"     # 開發
    EXTERMINATE = "exterminate"  # 消滅
    BUILD = "build"         # 建造
    RESEARCH = "research"   # 研究
    MIGRATE = "migrate"     # 遷移


@dataclass
class Resources:
    """資源儲存類"""
    ore: int = 0
    wood: int = 0
    metal: int = 0
    food: int = 0
    
    def __add__(self, other: 'Resources') -> 'Resources':
        return Resources(
            ore=self.ore + other.ore,
            wood=self.wood + other.wood,
            metal=self.metal + other.metal,
            food=self.food + other.food
        )
    
    def __sub__(self, other: 'Resources') -> 'Resources':
        return Resources(
            ore=max(0, self.ore - other.ore),
            wood=max(0, self.wood - other.wood),
            metal=max(0, self.metal - other.metal),
            food=max(0, self.food - other.food)
        )
    
    def __mul__(self, multiplier: float) -> 'Resources':
        return Resources(
            ore=int(self.ore * multiplier),
            wood=int(self.wood * multiplier),
            metal=int(self.metal * multiplier),
            food=int(self.food * multiplier)
        )
    
    def can_afford(self, cost: 'Resources') -> bool:
        """檢查是否有足夠資源"""
        return (self.ore >= cost.ore and 
                self.wood >= cost.wood and 
                self.metal >= cost.metal and 
                self.food >= cost.food)
    
    def to_dict(self) -> Dict:
        return {
            "ore": self.ore,
            "wood": self.wood,
            "metal": self.metal,
            "food": self.food
        }


@dataclass
class Tile:
    """地圖格子類"""
    x: int
    y: int
    terrain: TerrainType
    resources: Resources = field(default_factory=Resources)
    population: int = 0
    max_population: int = 100
    buildings: List[BuildingType] = field(default_factory=list)
    explored: bool = False
    controlled: bool = False
    
    def __post_init__(self):
        """初始化時根據地形設定基礎資源"""
        if self.terrain == TerrainType.MOUNTAIN:
            self.resources.ore = random.randint(50, 200)
        elif self.terrain == TerrainType.FOREST:
            self.resources.wood = random.randint(80, 150)
        elif self.terrain == TerrainType.PLAINS:
            self.resources.food = random.randint(30, 100)
        elif self.terrain == TerrainType.LAKE:
            self.resources.food = random.randint(40, 80)
    
    def get_resource_production(self) -> Resources:
        """計算每回合資源產出"""
        base_production = Resources()
        
        # 基礎產出（根據地形）
        if self.terrain == TerrainType.MOUNTAIN:
            base_production.ore = 5
        elif self.terrain == TerrainType.FOREST:
            base_production.wood = 8
        elif self.terrain == TerrainType.PLAINS:
            base_production.food = 6
        elif self.terrain == TerrainType.LAKE:
            base_production.food = 4
        
        # 人口影響產出
        population_multiplier = 1 + (self.population * 0.01)
        base_production = base_production * population_multiplier
        
        # 建築影響產出
        building_multiplier = 1.0
        for building in self.buildings:
            if building == BuildingType.MINE and self.terrain == TerrainType.MOUNTAIN:
                building_multiplier += 0.5
            elif building == BuildingType.LUMBER_MILL and self.terrain == TerrainType.FOREST:
                building_multiplier += 0.5
            elif building == BuildingType.FARM:
                base_production.food += 10
        
        base_production = base_production * building_multiplier
        return base_production
    
    def get_food_consumption(self) -> int:
        """計算人口糧食消耗"""
        return self.population * 2
    
    def can_build(self, building: BuildingType) -> bool:
        """檢查是否可以建造建築"""
        if building in self.buildings:
            return False
        
        if building == BuildingType.MINE and self.terrain != TerrainType.MOUNTAIN:
            return False
        elif building == BuildingType.LUMBER_MILL and self.terrain != TerrainType.FOREST:
            return False
        
        return True
    
    def to_dict(self) -> Dict:
        return {
            "x": self.x,
            "y": self.y,
            "terrain": self.terrain.value,
            "resources": self.resources.to_dict(),
            "population": self.population,
            "max_population": self.max_population,
            "buildings": [b.value for b in self.buildings],
            "explored": self.explored,
            "controlled": self.controlled,
            "resource_production": self.get_resource_production().to_dict(),
            "food_consumption": self.get_food_consumption()
        }
