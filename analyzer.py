#!/usr/bin/env python3
"""
遊戲分析工具 - 用於分析遊戲數據和生成報告
"""

import json
import statistics
from typing import Dict, List, Any, Optional, Tuple
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime


class GameAnalyzer:
    """遊戲分析器"""
    
    def __init__(self):
        self.game_records: List[Dict[str, Any]] = []
    
    def add_game_record(self, game_data: Dict[str, Any]):
        """添加遊戲記錄"""
        self.game_records.append({
            "timestamp": datetime.now().isoformat(),
            "data": game_data
        })
    
    def analyze_single_game(self, game_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析單個遊戲"""
        final_score = game_data.get("final_score", {})
        stats = game_data.get("stats", {})
        
        analysis = {
            "game_summary": {
                "turns_played": game_data.get("total_turns", 0),
                "victory": game_data.get("victory", False),
                "final_score": final_score.get("total_score", 0),
                "final_resources": game_data.get("final_resources", {}),
                "final_population": game_data.get("final_population", 0)
            },
            "performance_metrics": {
                "resource_efficiency": final_score.get("resource_efficiency", 0),
                "population_health": final_score.get("population_health", 0),
                "goal_completion": final_score.get("goal_completion", 0),
                "strategy_diversity": final_score.get("strategy_diversity", 0)
            },
            "strategy_analysis": self._analyze_strategy(stats),
            "recommendations": self._generate_recommendations(game_data)
        }
        
        return analysis
    
    def analyze_multiple_games(self, game_records: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """分析多個遊戲"""
        if game_records is None:
            game_records = [record["data"] for record in self.game_records]
        
        if not game_records:
            return {"error": "沒有遊戲記錄可分析"}
        
        # 收集統計數據
        scores = []
        turns = []
        victories = 0
        resource_efficiency = []
        population_health = []
        goal_completion = []
        strategy_diversity = []
        
        for game in game_records:
            final_score = game.get("final_score", {})
            scores.append(final_score.get("total_score", 0))
            turns.append(game.get("total_turns", 0))
            
            if game.get("victory", False):
                victories += 1
            
            resource_efficiency.append(final_score.get("resource_efficiency", 0))
            population_health.append(final_score.get("population_health", 0))
            goal_completion.append(final_score.get("goal_completion", 0))
            strategy_diversity.append(final_score.get("strategy_diversity", 0))
        
        total_games = len(game_records)
        
        analysis = {
            "summary": {
                "total_games": total_games,
                "victories": victories,
                "victory_rate": victories / total_games if total_games > 0 else 0,
                "average_score": statistics.mean(scores) if scores else 0,
                "average_turns": statistics.mean(turns) if turns else 0
            },
            "performance_statistics": {
                "scores": {
                    "mean": statistics.mean(scores) if scores else 0,
                    "median": statistics.median(scores) if scores else 0,
                    "std_dev": statistics.stdev(scores) if len(scores) > 1 else 0,
                    "min": min(scores) if scores else 0,
                    "max": max(scores) if scores else 0
                },
                "resource_efficiency": {
                    "mean": statistics.mean(resource_efficiency) if resource_efficiency else 0,
                    "std_dev": statistics.stdev(resource_efficiency) if len(resource_efficiency) > 1 else 0
                },
                "population_health": {
                    "mean": statistics.mean(population_health) if population_health else 0,
                    "std_dev": statistics.stdev(population_health) if len(population_health) > 1 else 0
                },
                "goal_completion": {
                    "mean": statistics.mean(goal_completion) if goal_completion else 0,
                    "std_dev": statistics.stdev(goal_completion) if len(goal_completion) > 1 else 0
                },
                "strategy_diversity": {
                    "mean": statistics.mean(strategy_diversity) if strategy_diversity else 0,
                    "std_dev": statistics.stdev(strategy_diversity) if len(strategy_diversity) > 1 else 0
                }
            },
            "trends": self._analyze_trends(game_records),
            "best_strategies": self._identify_best_strategies(game_records)
        }
        
        return analysis
    
    def _analyze_strategy(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """分析策略特徵"""
        total_ap = stats.get("total_ap_used", 1)
        
        return {
            "action_efficiency": {
                "total_actions": total_ap,
                "buildings_per_action": stats.get("buildings_built", 0) / total_ap,
                "exploration_rate": stats.get("tiles_explored", 0) / total_ap,
                "expansion_rate": stats.get("tiles_expanded", 0) / total_ap
            },
            "resource_management": {
                "total_resources_gathered": stats.get("total_resources_gathered", {}),
                "starvation_events": stats.get("starvation_events", 0)
            },
            "development_focus": self._categorize_development_focus(stats)
        }
    
    def _categorize_development_focus(self, stats: Dict[str, Any]) -> str:
        """分類發展重點"""
        buildings = stats.get("buildings_built", 0)
        exploration = stats.get("tiles_explored", 0)
        expansion = stats.get("tiles_expanded", 0)
        
        if buildings > exploration and buildings > expansion:
            return "建設導向"
        elif exploration > expansion:
            return "探索導向"
        elif expansion > 0:
            return "擴張導向"
        else:
            return "保守策略"
    
    def _generate_recommendations(self, game_data: Dict[str, Any]) -> List[str]:
        """生成改進建議"""
        recommendations = []
        final_score = game_data.get("final_score", {})
        stats = game_data.get("stats", {})
        
        # 資源效率建議
        if final_score.get("resource_efficiency", 0) < 10:
            recommendations.append("提高資源效率：專注於建造提升產出的建築")
        
        # 人口健康建議
        if final_score.get("population_health", 0) < 0.5:
            recommendations.append("改善人口管理：確保足夠的糧食供應，建造更多房屋")
        
        # 目標達成建議
        if final_score.get("goal_completion", 0) < 0.5:
            recommendations.append("加強金屬生產：建造更多礦場和冶煉廠")
        
        # 策略多樣性建議
        if final_score.get("strategy_diversity", 0) < 0.5:
            recommendations.append("嘗試更多樣化的策略：平衡探索、擴張、建設和研究")
        
        # 飢荒管理建議
        if stats.get("starvation_events", 0) > 2:
            recommendations.append("重視糧食管理：優先建造農場，避免人口過度增長")
        
        return recommendations
    
    def _analyze_trends(self, game_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析趨勢"""
        if len(game_records) < 3:
            return {"message": "需要至少3個遊戲記錄才能分析趨勢"}
        
        # 按時間排序
        sorted_games = sorted(game_records, key=lambda x: x.get("timestamp", ""))
        
        recent_games = sorted_games[-5:]  # 最近5個遊戲
        scores = [game.get("final_score", {}).get("total_score", 0) for game in recent_games]
        
        if len(scores) >= 2:
            trend = "improving" if scores[-1] > scores[0] else "declining"
        else:
            trend = "stable"
        
        return {
            "performance_trend": trend,
            "recent_average": statistics.mean(scores) if scores else 0,
            "improvement_rate": (scores[-1] - scores[0]) / len(scores) if len(scores) > 1 else 0
        }
    
    def _identify_best_strategies(self, game_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """識別最佳策略"""
        if not game_records:
            return {}
        
        # 找出得分最高的遊戲
        best_game = max(game_records, key=lambda x: x.get("final_score", {}).get("total_score", 0))
        best_stats = best_game.get("stats", {})
        
        return {
            "best_score": best_game.get("final_score", {}).get("total_score", 0),
            "best_strategy_characteristics": {
                "development_focus": self._categorize_development_focus(best_stats),
                "buildings_built": best_stats.get("buildings_built", 0),
                "tiles_explored": best_stats.get("tiles_explored", 0),
                "tiles_expanded": best_stats.get("tiles_expanded", 0),
                "total_ap_used": best_stats.get("total_ap_used", 0)
            }
        }
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """生成分析報告"""
        if not self.game_records:
            return "沒有遊戲記錄可生成報告"
        
        analysis = self.analyze_multiple_games()
        
        report_lines = [
            "# LLM-X4 遊戲分析報告",
            f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 總體統計",
            f"- 總遊戲數: {analysis['summary']['total_games']}",
            f"- 勝利次數: {analysis['summary']['victories']}",
            f"- 勝利率: {analysis['summary']['victory_rate']:.1%}",
            f"- 平均得分: {analysis['summary']['average_score']:.2f}",
            f"- 平均回合數: {analysis['summary']['average_turns']:.1f}",
            "",
            "## 性能指標",
            f"- 平均資源效率: {analysis['performance_statistics']['resource_efficiency']['mean']:.2f}",
            f"- 平均人口健康度: {analysis['performance_statistics']['population_health']['mean']:.2%}",
            f"- 平均目標達成度: {analysis['performance_statistics']['goal_completion']['mean']:.2%}",
            f"- 平均策略多樣性: {analysis['performance_statistics']['strategy_diversity']['mean']:.2%}",
            "",
            "## 最佳策略特徵"
        ]
        
        best_strategies = analysis.get("best_strategies", {})
        if best_strategies:
            best_chars = best_strategies.get("best_strategy_characteristics", {})
            report_lines.extend([
                f"- 最高得分: {best_strategies.get('best_score', 0):.2f}",
                f"- 發展重點: {best_chars.get('development_focus', 'N/A')}",
                f"- 建築數量: {best_chars.get('buildings_built', 0)}",
                f"- 探索地塊: {best_chars.get('tiles_explored', 0)}",
                f"- 擴張地塊: {best_chars.get('tiles_expanded', 0)}"
            ])
        
        report = "\n".join(report_lines)
        
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report)
                print(f"報告已保存到: {output_file}")
            except Exception as e:
                print(f"保存報告失敗: {e}")
        
        return report
    
    def save_analysis_data(self, filename: str) -> bool:
        """保存分析數據"""
        try:
            analysis_data = {
                "timestamp": datetime.now().isoformat(),
                "game_records": self.game_records,
                "analysis": self.analyze_multiple_games()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"保存分析數據失敗: {e}")
            return False
    
    def load_analysis_data(self, filename: str) -> bool:
        """載入分析數據"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.game_records = data.get("game_records", [])
            return True
        except Exception as e:
            print(f"載入分析數據失敗: {e}")
            return False


def compare_strategies(strategy_a_records: List[Dict[str, Any]], 
                      strategy_b_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """比較兩種策略"""
    analyzer = GameAnalyzer()
    
    analysis_a = analyzer.analyze_multiple_games(strategy_a_records)
    analysis_b = analyzer.analyze_multiple_games(strategy_b_records)
    
    comparison = {
        "strategy_a": {
            "games": len(strategy_a_records),
            "victory_rate": analysis_a["summary"]["victory_rate"],
            "average_score": analysis_a["summary"]["average_score"]
        },
        "strategy_b": {
            "games": len(strategy_b_records), 
            "victory_rate": analysis_b["summary"]["victory_rate"],
            "average_score": analysis_b["summary"]["average_score"]
        },
        "comparison": {
            "score_difference": analysis_a["summary"]["average_score"] - analysis_b["summary"]["average_score"],
            "victory_rate_difference": analysis_a["summary"]["victory_rate"] - analysis_b["summary"]["victory_rate"],
            "better_strategy": "A" if analysis_a["summary"]["average_score"] > analysis_b["summary"]["average_score"] else "B"
        }
    }
    
    return comparison


if __name__ == "__main__":
    # 示例用法
    analyzer = GameAnalyzer()
    
    # 這裡可以添加一些示例數據進行測試
    print("遊戲分析工具已準備就緒")
    print("使用 analyzer.add_game_record(game_data) 添加遊戲記錄")
    print("使用 analyzer.generate_report() 生成分析報告")
