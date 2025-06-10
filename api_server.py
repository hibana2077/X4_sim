#!/usr/bin/env python3
"""
API服務器 - 提供HTTP API接口供LLM調用
"""

import json
import threading
import time
from flask import Flask, request, jsonify
from main import LLMX4Game


app = Flask(__name__)

# 遊戲實例管理
games = {}
game_lock = threading.Lock()


@app.route('/game/new', methods=['POST'])
def create_new_game():
    """創建新遊戲"""
    try:
        data = request.get_json() or {}
        width = data.get('width', 10)
        height = data.get('height', 10)
        
        game_id = f"game_{int(time.time())}"
        
        with game_lock:
            games[game_id] = LLMX4Game(width, height)
        
        return jsonify({
            'success': True,
            'game_id': game_id,
            'message': f'新遊戲已創建，地圖大小: {width}x{height}'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/game/<game_id>/observation', methods=['GET'])
def get_observation(game_id):
    """獲取遊戲觀察"""
    try:
        if game_id not in games:
            return jsonify({'error': '遊戲不存在'}), 404
        
        game = games[game_id]
        format_type = request.args.get('format', 'json')
        simple = request.args.get('simple', 'false').lower() == 'true'
        
        if simple:
            observation_str = game.get_simple_observation()
        else:
            observation_str = game.get_observation(format_type)
        
        if format_type.lower() == 'yaml':
            return observation_str, 200, {'Content-Type': 'text/yaml'}
        else:
            return json.loads(observation_str)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/game/<game_id>/action', methods=['POST'])
def execute_actions(game_id):
    """執行行動"""
    try:
        if game_id not in games:
            return jsonify({'error': '遊戲不存在'}), 404
        
        game = games[game_id]
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '缺少行動數據'}), 400
        
        # 支持單個行動或行動列表
        if isinstance(data, dict):
            actions = [data]
        else:
            actions = data
        
        results = game.execute_actions(actions)
        
        return jsonify({
            'success': True,
            'results': results,
            'remaining_ap': game.game_state.action_points
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/game/<game_id>/next_turn', methods=['POST'])
def next_turn(game_id):
    """進入下一回合"""
    try:
        if game_id not in games:
            return jsonify({'error': '遊戲不存在'}), 404
        
        game = games[game_id]
        result = game.next_turn()
        
        return jsonify({
            'success': True,
            'turn_result': result
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/game/<game_id>/status', methods=['GET'])
def get_game_status(game_id):
    """獲取遊戲狀態"""
    try:
        if game_id not in games:
            return jsonify({'error': '遊戲不存在'}), 404
        
        game = games[game_id]
        
        return jsonify({
            'game_id': game_id,
            'turn': game.game_state.turn,
            'max_turns': game.game_state.max_turns,
            'action_points': game.game_state.action_points,
            'game_over': game.game_state.game_over,
            'victory': game.game_state.victory,
            'resources': game.game_state.global_resources.to_dict(),
            'controlled_tiles': len(game.game_state.game_map.get_controlled_tiles()),
            'population': game.game_state.game_map.get_total_population()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/game/<game_id>/score', methods=['GET'])
def get_score(game_id):
    """獲取遊戲得分"""
    try:
        if game_id not in games:
            return jsonify({'error': '遊戲不存在'}), 404
        
        game = games[game_id]
        
        if game.game_state.game_over:
            score = game.get_final_score()
        else:
            score = {
                'current_score': game.game_state.get_score(),
                'game_ongoing': True
            }
        
        return jsonify(score)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/game/<game_id>/delete', methods=['DELETE'])
def delete_game(game_id):
    """刪除遊戲"""
    try:
        with game_lock:
            if game_id in games:
                del games[game_id]
                return jsonify({
                    'success': True,
                    'message': '遊戲已刪除'
                })
            else:
                return jsonify({'error': '遊戲不存在'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/games', methods=['GET'])
def list_games():
    """列出所有遊戲"""
    try:
        game_list = []
        with game_lock:
            for game_id, game in games.items():
                game_list.append({
                    'game_id': game_id,
                    'turn': game.game_state.turn,
                    'game_over': game.game_state.game_over,
                    'victory': game.game_state.victory
                })
        
        return jsonify({
            'games': game_list,
            'total': len(game_list)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """健康檢查"""
    return jsonify({
        'status': 'healthy',
        'service': 'LLM-X4 API Server',
        'active_games': len(games)
    })


@app.route('/api/help', methods=['GET'])
def api_help():
    """API幫助文檔"""
    help_doc = {
        'title': 'LLM-X4 API Documentation',
        'version': '1.0',
        'endpoints': {
            'POST /game/new': {
                'description': '創建新遊戲',
                'parameters': {
                    'width': '地圖寬度 (預設: 10)',
                    'height': '地圖高度 (預設: 10)'
                }
            },
            'GET /game/{game_id}/observation': {
                'description': '獲取遊戲觀察',
                'parameters': {
                    'format': 'json 或 yaml (預設: json)',
                    'simple': 'true 或 false (預設: false)'
                }
            },
            'POST /game/{game_id}/action': {
                'description': '執行行動',
                'body': '行動對象或行動對象數組'
            },
            'POST /game/{game_id}/next_turn': {
                'description': '進入下一回合'
            },
            'GET /game/{game_id}/status': {
                'description': '獲取遊戲狀態'
            },
            'GET /game/{game_id}/score': {
                'description': '獲取遊戲得分'
            },
            'DELETE /game/{game_id}/delete': {
                'description': '刪除遊戲'
            },
            'GET /games': {
                'description': '列出所有遊戲'
            }
        },
        'action_examples': {
            'explore': {
                'action_type': 'explore',
                'target_x': 5,
                'target_y': 5
            },
            'expand': {
                'action_type': 'expand',
                'target_x': 5,
                'target_y': 5
            },
            'build': {
                'action_type': 'build',
                'target_x': 5,
                'target_y': 5,
                'building_type': 'farm'
            },
            'exploit': {
                'action_type': 'exploit',
                'target_x': 5,
                'target_y': 5
            },
            'research': {
                'action_type': 'research'
            },
            'migrate': {
                'action_type': 'migrate'
            }
        }
    }
    
    return jsonify(help_doc)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='LLM-X4 API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host address')
    parser.add_argument('--port', type=int, default=5000, help='Port number')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    print(f"LLM-X4 API Server starting on {args.host}:{args.port}")
    print(f"API documentation available at: http://{args.host}:{args.port}/api/help")
    
    app.run(host=args.host, port=args.port, debug=args.debug)
