from typing import Dict, List, Tuple, Optional
import random
import numpy as np
from .models import Tile, TerrainType, Resources


class GameMap:
    """遊戲地圖類"""
    
    def __init__(self, width: int = 10, height: int = 10):
        self.width = width
        self.height = height
        self.tiles: Dict[Tuple[int, int], Tile] = {}
        self._generate_map()
    
    def _generate_map(self):
        """生成地圖"""
        # 地形分布權重
        terrain_weights = {
            TerrainType.PLAINS: 0.4,
            TerrainType.FOREST: 0.3,
            TerrainType.MOUNTAIN: 0.2,
            TerrainType.LAKE: 0.1
        }
        
        terrains = list(terrain_weights.keys())
        weights = list(terrain_weights.values())
        
        for x in range(self.width):
            for y in range(self.height):
                terrain = np.random.choice(terrains, p=weights)
                tile = Tile(x=x, y=y, terrain=terrain)
                
                # 添加一些隨機人口（模擬原住民）
                if random.random() < 0.3:
                    tile.population = random.randint(5, 25)
                
                self.tiles[(x, y)] = tile
        
        # 確保起始位置是平原且有一定人口
        start_tile = self.tiles[(self.width//2, self.height//2)]
        start_tile.terrain = TerrainType.PLAINS
        start_tile.population = 20
        start_tile.explored = True
        start_tile.controlled = True
    
    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """獲取指定位置的地塊"""
        return self.tiles.get((x, y))
    
    def get_neighbors(self, x: int, y: int) -> List[Tile]:
        """獲取相鄰地塊"""
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbors.append(self.tiles[(nx, ny)])
        return neighbors
    
    def get_controlled_tiles(self) -> List[Tile]:
        """獲取所有受控制的地塊"""
        return [tile for tile in self.tiles.values() if tile.controlled]
    
    def get_explored_tiles(self) -> List[Tile]:
        """獲取所有已探索的地塊"""
        return [tile for tile in self.tiles.values() if tile.explored]
    
    def can_explore(self, x: int, y: int) -> bool:
        """檢查是否可以探索指定位置"""
        tile = self.get_tile(x, y)
        if not tile or tile.explored:
            return False
        
        # 必須相鄰於已控制的地塊
        neighbors = self.get_neighbors(x, y)
        return any(neighbor.controlled for neighbor in neighbors)
    
    def can_expand_to(self, x: int, y: int) -> bool:
        """檢查是否可以擴張到指定位置"""
        tile = self.get_tile(x, y)
        if not tile or tile.controlled or not tile.explored:
            return False
        
        # 必須相鄰於已控制的地塊
        neighbors = self.get_neighbors(x, y)
        return any(neighbor.controlled for neighbor in neighbors)
    
    def explore_tile(self, x: int, y: int) -> bool:
        """探索地塊"""
        if not self.can_explore(x, y):
            return False
        
        tile = self.get_tile(x, y)
        tile.explored = True
        return True
    
    def expand_to_tile(self, x: int, y: int) -> bool:
        """擴張到地塊"""
        if not self.can_expand_to(x, y):
            return False
        
        tile = self.get_tile(x, y)
        tile.controlled = True
        return True
    
    def get_total_resources(self) -> Resources:
        """計算所有受控地塊的總資源儲量"""
        total = Resources()
        for tile in self.get_controlled_tiles():
            total = total + tile.resources
        return total
    
    def get_total_population(self) -> int:
        """計算總人口"""
        return sum(tile.population for tile in self.get_controlled_tiles())
    
    def get_total_production(self) -> Resources:
        """計算總產出"""
        total = Resources()
        for tile in self.get_controlled_tiles():
            total = total + tile.get_resource_production()
        return total
    
    def get_total_food_consumption(self) -> int:
        """計算總糧食消耗"""
        return sum(tile.get_food_consumption() for tile in self.get_controlled_tiles())
    
    def to_dict(self) -> Dict:
        """轉換為字典格式"""
        return {
            "width": self.width,
            "height": self.height,
            "tiles": {f"{x},{y}": tile.to_dict() for (x, y), tile in self.tiles.items()},
            "controlled_tiles": len(self.get_controlled_tiles()),
            "explored_tiles": len(self.get_explored_tiles()),
            "total_population": self.get_total_population(),
            "total_resources": self.get_total_resources().to_dict(),
            "total_production": self.get_total_production().to_dict(),
            "total_food_consumption": self.get_total_food_consumption()
        }
