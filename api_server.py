# api_server.py
#!/usr/bin/env python3
"""
API 服務器 (FastAPI) - 提供 HTTP API 介面供 LLM 調用
"""
from fastapi import FastAPI, HTTPException, Request, Query, Body
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
import threading
import time
import json
import yaml
from main import LLMX4Game

app = FastAPI(title="LLM-X4 API Server", version="1.0")

# 遊戲實例管理
games: dict[str, LLMX4Game] = {}
game_lock = threading.Lock()


class NewGameParams(BaseModel):
    width: int = 10
    height: int = 10


class Action(BaseModel):
    action_type: str
    target_x: int | None = None
    target_y: int | None = None
    building_type: str | None = None


@app.post("/game/new")
def create_new_game(params: NewGameParams):
    """創建新遊戲"""
    game_id = f"game_{int(time.time())}"
    with game_lock:
        games[game_id] = LLMX4Game(params.width, params.height)
    return {
        "success": True,
        "game_id": game_id,
        "message": f"新遊戲已創建，地圖大小: {params.width}x{params.height}",
    }


@app.get("/game/{game_id}/observation")
def get_observation(
    game_id: str,
    format: str = Query("json", description="json or yaml"),
    simple: bool = Query(False, description="是否使用簡化觀察"),
):
    """獲取遊戲觀察"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="遊戲不存在")
    game = games[game_id]
    if simple:
        obs = game.get_simple_observation()
    else:
        obs = game.get_observation(format)
    if format.lower() == "yaml":
        return PlainTextResponse(obs, media_type="text/yaml")
    # JSONResponse expects dict/list, not string
    return JSONResponse(json.loads(obs))


@app.post("/game/{game_id}/action")
def execute_actions(game_id: str, actions: Action | list[Action] = Body(...)):
    """執行行動"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="遊戲不存在")
    game = games[game_id]
    acts = actions if isinstance(actions, list) else [actions]
    results = game.execute_actions([act.dict() for act in acts])
    return {
        "success": True,
        "results": results,
        "remaining_ap": game.game_state.action_points,
    }


@app.post("/game/{game_id}/next_turn")
def next_turn(game_id: str):
    """進入下一回合"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="遊戲不存在")
    result = games[game_id].next_turn()
    return {"success": True, "turn_result": result}


@app.get("/game/{game_id}/status")
def get_game_status(game_id: str):
    """獲取遊戲狀態"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="遊戲不存在")
    gs = games[game_id].game_state
    return {
        "game_id": game_id,
        "turn": gs.turn,
        "max_turns": gs.max_turns,
        "action_points": gs.action_points,
        "game_over": gs.game_over,
        "victory": gs.victory,
        "resources": gs.global_resources.to_dict(),
        "controlled_tiles": len(gs.game_map.get_controlled_tiles()),
        "population": gs.game_map.get_total_population(),
    }


@app.get("/game/{game_id}/score")
def get_score(game_id: str):
    """獲取遊戲得分"""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="遊戲不存在")
    game = games[game_id]
    if game.game_state.game_over:
        return game.get_final_score()
    return {"current_score": game.game_state.get_score(), "game_ongoing": True}


@app.delete("/game/{game_id}/delete")
def delete_game(game_id: str):
    """刪除遊戲"""
    with game_lock:
        if game_id not in games:
            raise HTTPException(status_code=404, detail="遊戲不存在")
        del games[game_id]
    return {"success": True, "message": "遊戲已刪除"}


@app.get("/games")
def list_games():
    """列出所有遊戲"""
    with game_lock:
        game_list = [
            {
                "game_id": gid,
                "turn": g.game_state.turn,
                "game_over": g.game_state.game_over,
                "victory": g.game_state.victory,
            }
            for gid, g in games.items()
        ]
    return {"games": game_list, "total": len(game_list)}


@app.get("/health")
def health_check():
    """健康檢查"""
    return {"status": "healthy", "service": "LLM-X4 API Server", "active_games": len(games)}


@app.get("/api/help")
def api_help():
    """API 幫助文檔"""
    help_doc = {
        "title": "LLM-X4 API Documentation",
        "version": "1.0",
        "endpoints": {
            "POST /game/new": {
                "description": "創建新遊戲",
                "parameters": {"width": "地圖寬度 (預設: 10)", "height": "地圖高度 (預設: 10)"},
            },
            "GET /game/{game_id}/observation": {
                "description": "獲取遊戲觀察",
                "parameters": {"format": "json 或 yaml (預設: json)", "simple": "true 或 false (預設: false)"},
            },
            "POST /game/{game_id}/action": {"description": "執行行動", "body": "行動對象或行動對象數組"},
            "POST /game/{game_id}/next_turn": {"description": "進入下一回合"},
            "GET /game/{game_id}/status": {"description": "獲取遊戲狀態"},
            "GET /game/{game_id}/score": {"description": "獲取遊戲得分"},
            "DELETE /game/{game_id}/delete": {"description": "刪除遊戲"},
            "GET /games": {"description": "列出所有遊戲"},
        },
        "action_examples": {
            "explore": {"action_type": "explore", "target_x": 5, "target_y": 5},
            "expand": {"action_type": "expand", "target_x": 5, "target_y": 5},
            "build": {"action_type": "build", "target_x": 5, "target_y": 5, "building_type": "farm"},
            "exploit": {"action_type": "exploit", "target_x": 5, "target_y": 5},
            "research": {"action_type": "research"},
            "migrate": {"action_type": "migrate"},
        },
    }
    return help_doc


if __name__ == "__main__":
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser(description="LLM-X4 API Server (FastAPI)")
    parser.add_argument("--host", default="0.0.0.0", help="Host address")
    parser.add_argument("--port", type=int, default=5000, help="Port number")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    print(f"LLM-X4 API Server starting on {args.host}:{args.port}")
    print(f"API documentation available at: http://{args.host}:{args.port}/docs")
    uvicorn.run("api_server:app", host=args.host, port=args.port, log_level="debug" if args.debug else "info")
