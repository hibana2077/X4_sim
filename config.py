#!/usr/bin/env python3
"""
配置文件 - 遊戲參數設定
"""

# 遊戲基本設定
GAME_CONFIG = {
    "default_map_width": 10,
    "default_map_height": 10,
    "max_turns": 100,
    "action_points_per_turn": 5,
    "victory_metal_target": 1000
}

# 資源相關設定
RESOURCE_CONFIG = {
    "initial_resources": {
        "ore": 50,
        "wood": 50, 
        "metal": 20,
        "food": 100
    },
    "terrain_base_resources": {
        "mountain": {"ore": (50, 200)},
        "forest": {"wood": (80, 150)},
        "plains": {"food": (30, 100)},
        "lake": {"food": (40, 80)}
    },
    "terrain_base_production": {
        "mountain": {"ore": 5},
        "forest": {"wood": 8},
        "plains": {"food": 6},
        "lake": {"food": 4}
    }
}

# 建築設定
BUILDING_CONFIG = {
    "costs": {
        "mine": {"wood": 20, "metal": 10},
        "lumber_mill": {"wood": 15, "metal": 5},
        "farm": {"wood": 10, "ore": 5},
        "smelter": {"wood": 25, "ore": 15},
        "house": {"wood": 15, "ore": 5}
    },
    "effects": {
        "mine": {"ore_multiplier": 1.5},
        "lumber_mill": {"wood_multiplier": 1.5},
        "farm": {"food_bonus": 10},
        "smelter": {"ore_to_metal_ratio": 2},
        "house": {"population_capacity_bonus": 50, "growth_rate_bonus": 0.01}
    }
}

# 行動設定
ACTION_CONFIG = {
    "costs": {
        "explore": 1,
        "expand": 2,
        "exploit": 1,
        "build": 2,
        "research": 3,
        "migrate": 1
    },
    "resource_costs": {
        "expand": {"food": 20, "wood": 10},
        "research": {"metal": 15, "food": 10}
    }
}

# 人口設定
POPULATION_CONFIG = {
    "initial_population_range": (5, 25),
    "initial_population_chance": 0.3,
    "starting_population": 20,
    "base_growth_rate": 0.02,
    "food_consumption_per_person": 2,
    "population_production_multiplier": 0.01,
    "starvation_population_loss_rate": 0.1
}

# 事件設定
EVENT_CONFIG = {
    "event_chance_per_turn": 0.15,
    "event_types": {
        "drought": {
            "description": "乾旱減少了糧食產出",
            "effects": {"food_reduction": 0.5},
            "duration_range": (1, 3)
        },
        "harvest": {
            "description": "豐收增加了糧食產出",
            "effects": {"food_bonus": 50},
            "duration_range": (1, 1)
        },
        "discovery": {
            "description": "發現了新的礦脈",
            "effects": {"ore_bonus": 30},
            "duration_range": (1, 1)
        },
        "plague": {
            "description": "瘟疫減少了人口",
            "effects": {"population_reduction": 0.1},
            "duration_range": (1, 2)
        }
    }
}

# 評分設定
SCORING_CONFIG = {
    "weights": {
        "resource_efficiency": 0.3,
        "population_health": 0.2,
        "goal_completion": 0.4,
        "strategy_diversity": 0.1
    },
    "research_points_per_action": 10,
    "research_cost_for_technology": 30
}

# 地圖生成設定
MAP_CONFIG = {
    "terrain_distribution": {
        "plains": 0.4,
        "forest": 0.3,
        "mountain": 0.2,
        "lake": 0.1
    },
    "ensure_starting_area": True,
    "starting_terrain": "plains"
}

# API設定
API_CONFIG = {
    "default_host": "0.0.0.0",
    "default_port": 5000,
    "max_games_per_instance": 50,
    "game_timeout_hours": 24
}

# 調試設定
DEBUG_CONFIG = {
    "verbose_actions": False,
    "log_events": True,
    "show_detailed_production": False,
    "enable_cheats": False
}
