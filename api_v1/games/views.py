import asyncio
import json
from fastapi import APIRouter, Depends, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import TYPE_CHECKING
from fastapi import WebSocket

from core.config import settings
from api_v1.dependencies.games.gamemanager import game_manager
from api_v1.dependencies.games.matchmaking import matchmaking_system
from api_v1.fastapi_users_object import current_active_user, get_current_user_from_token
from core.models import User, db_helper
from api_v1.dependencies.games import Player, Preferences
from . import crud


router = APIRouter(prefix=settings.api.v1.games, tags=["Games"])


@router.get("")
async def get_user_games(user: User = Depends(current_active_user), session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    games = await crud.get_user_games(user, session)
    return games


@router.websocket("")
async def websocket_function(websocket: WebSocket, 
                             user: User = Depends(get_current_user_from_token), 
                             session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    try:
        await websocket.accept()
        data = await websocket.receive_json()
        if "action" not in data:
            raise KeyError("'action' field is required")
        if "preferences" not in data:
            raise KeyError("'preferences' field is required")
        if data["preferences"] not in ['WHITE', 'BLACK', 'ANY']:
            raise KeyError("'preferences' must be one of the following values: 'WHITE', 'BLACK', 'ANY'")
        if data["action"] == "start_waiting":
            player = Player(websocket, user, data["preferences"])
            await matchmaking_system.add_player(player, session)

        while True:
            data = await websocket.receive_json()
            await game_manager.on_json_message(user.username, websocket, data, session)


    except json.JSONDecodeError as e:
        await websocket.send_json({"action": "json_error", "detail": e.msg})
    except KeyError as k:   
        await websocket.send_json({"action": "message_error", "detail": str(k)})
        await websocket.close()
    except WebSocketDisconnect:
        if not await matchmaking_system.remove_websocket_if_needed(websocket):
            await game_manager.on_websocket_disconnected(websocket, session)


