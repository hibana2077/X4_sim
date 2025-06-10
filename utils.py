#!/usr/bin/env python3
"""
工具函數 - 通用輔助函數
"""

import json
import yaml
import random
import hashlib
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta


def generate_game_id() -> str:
    """生成唯一的遊戲ID"""
    timestamp = str(int(time.time() * 1000))
    random_part = str(random.randint(1000, 9999))
    return f"game_{timestamp}_{random_part}"


def calculate_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    """計算兩點間距離"""
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


def get_neighbors_coordinates(x: int, y: int, width: int, height: int) -> List[Tuple[int, int]]:
    """獲取相鄰座標列表"""
    neighbors = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < width and 0 <= ny < height:
            neighbors.append((nx, ny))
    return neighbors


def format_resources(resources_dict: Dict[str, int]) -> str:
    """格式化資源顯示"""
    return f"礦石:{resources_dict.get('ore', 0)}, 木材:{resources_dict.get('wood', 0)}, 金屬:{resources_dict.get('metal', 0)}, 糧食:{resources_dict.get('food', 0)}"


def parse_coordinates(coord_str: str) -> Optional[Tuple[int, int]]:
    """解析座標字符串 "x,y" -> (x, y)"""
    try:
        parts = coord_str.split(',')
        if len(parts) == 2:
            return int(parts[0].strip()), int(parts[1].strip())
    except ValueError:
        pass
    return None


def save_json(data: Any, filename: str, pretty: bool = True) -> bool:
    """保存數據為JSON文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"保存JSON文件失敗: {e}")
        return False


def load_json(filename: str) -> Optional[Any]:
    """載入JSON文件"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"載入JSON文件失敗: {e}")
        return None


def save_yaml(data: Any, filename: str) -> bool:
    """保存數據為YAML文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        return True
    except Exception as e:
        print(f"保存YAML文件失敗: {e}")
        return False


def load_yaml(filename: str) -> Optional[Any]:
    """載入YAML文件"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"載入YAML文件失敗: {e}")
        return None


def validate_action_data(action_data: Dict[str, Any]) -> Tuple[bool, str]:
    """驗證行動數據格式"""
    if not isinstance(action_data, dict):
        return False, "行動數據必須是字典格式"
    
    if "action_type" not in action_data:
        return False, "缺少必要字段: action_type"
    
    action_type = action_data["action_type"]
    
    # 檢查需要座標的行動
    if action_type in ["explore", "expand", "exploit", "build"]:
        if "target_x" not in action_data or "target_y" not in action_data:
            return False, f"行動 {action_type} 需要 target_x 和 target_y 參數"
        
        try:
            int(action_data["target_x"])
            int(action_data["target_y"])
        except (ValueError, TypeError):
            return False, "target_x 和 target_y 必須是整數"
    
    # 檢查建造行動的建築類型
    if action_type == "build":
        if "building_type" not in action_data:
            return False, "建造行動需要 building_type 參數"
    
    return True, "驗證通過"


def calculate_shannon_entropy(action_counts: Dict[str, int]) -> float:
    """計算Shannon熵值（策略多樣性指標）"""
    if not action_counts:
        return 0.0
    
    total = sum(action_counts.values())
    if total == 0:
        return 0.0
    
    entropy = 0.0
    for count in action_counts.values():
        if count > 0:
            probability = count / total
            entropy -= probability * (probability ** 0.5).bit_length()  # 簡化的熵計算
    
    return entropy


def format_time_duration(seconds: float) -> str:
    """格式化時間持續時間"""
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分鐘"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}小時"


def clamp(value: float, min_val: float, max_val: float) -> float:
    """限制數值範圍"""
    return max(min_val, min(max_val, value))


def weighted_random_choice(choices: Dict[Any, float]) -> Any:
    """根據權重隨機選擇"""
    if not choices:
        return None
    
    total_weight = sum(choices.values())
    if total_weight <= 0:
        return random.choice(list(choices.keys()))
    
    rand_val = random.random() * total_weight
    cumulative = 0.0
    
    for choice, weight in choices.items():
        cumulative += weight
        if rand_val <= cumulative:
            return choice
    
    return list(choices.keys())[-1]  # 備用返回


def create_grid_string(grid_data: Dict[Tuple[int, int], str], width: int, height: int, default: str = ".") -> str:
    """創建網格字符串表示"""
    lines = []
    for y in range(height):
        line = ""
        for x in range(width):
            line += grid_data.get((x, y), default)
        lines.append(line)
    return "\n".join(lines)


def parse_version_string(version: str) -> Tuple[int, int, int]:
    """解析版本字符串 "1.2.3" -> (1, 2, 3)"""
    try:
        parts = version.split('.')
        if len(parts) >= 3:
            return int(parts[0]), int(parts[1]), int(parts[2])
        elif len(parts) == 2:
            return int(parts[0]), int(parts[1]), 0
        elif len(parts) == 1:
            return int(parts[0]), 0, 0
    except ValueError:
        pass
    return 0, 0, 0


def generate_map_hash(map_data: Dict[str, Any]) -> str:
    """生成地圖的雜湊值，用於識別相同地圖"""
    map_str = json.dumps(map_data, sort_keys=True)
    return hashlib.md5(map_str.encode()).hexdigest()[:8]


def calculate_completion_percentage(current: float, target: float) -> float:
    """計算完成百分比"""
    if target <= 0:
        return 100.0 if current > 0 else 0.0
    return min(100.0, (current / target) * 100.0)


def format_large_number(number: int) -> str:
    """格式化大數字顯示"""
    if number >= 1000000:
        return f"{number/1000000:.1f}M"
    elif number >= 1000:
        return f"{number/1000:.1f}K"
    else:
        return str(number)


def get_current_timestamp() -> str:
    """獲取當前時間戳字符串"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def is_expired(timestamp: str, hours: int) -> bool:
    """檢查時間戳是否已過期"""
    try:
        ts = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        expiry_time = ts + timedelta(hours=hours)
        return datetime.now() > expiry_time
    except ValueError:
        return True  # 無法解析則視為過期


class GameLogger:
    """簡單的遊戲日誌記錄器"""
    
    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file
        self.logs: List[Dict[str, Any]] = []
    
    def log(self, level: str, message: str, data: Optional[Dict[str, Any]] = None):
        """記錄日誌"""
        log_entry = {
            "timestamp": get_current_timestamp(),
            "level": level.upper(),
            "message": message,
            "data": data or {}
        }
        
        self.logs.append(log_entry)
        
        # 輸出到控制台
        print(f"[{log_entry['timestamp']}] {log_entry['level']}: {message}")
        
        # 輸出到文件
        if self.log_file:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            except Exception as e:
                print(f"寫入日誌文件失敗: {e}")
    
    def info(self, message: str, data: Optional[Dict[str, Any]] = None):
        self.log("INFO", message, data)
    
    def warning(self, message: str, data: Optional[Dict[str, Any]] = None):
        self.log("WARNING", message, data)
    
    def error(self, message: str, data: Optional[Dict[str, Any]] = None):
        self.log("ERROR", message, data)
    
    def debug(self, message: str, data: Optional[Dict[str, Any]] = None):
        self.log("DEBUG", message, data)
    
    def get_logs(self, level: Optional[str] = None, last_n: Optional[int] = None) -> List[Dict[str, Any]]:
        """獲取日誌"""
        logs = self.logs
        
        if level:
            logs = [log for log in logs if log["level"] == level.upper()]
        
        if last_n:
            logs = logs[-last_n:]
        
        return logs
