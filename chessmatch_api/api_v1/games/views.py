from fastapi import APIRouter, Depends
from typing import TYPE_CHECKING
from fastapi import WebSocket

from core.config import settings
from api_v1.fastapi_users_object import current_active_user, get_current_user_from_token
from core.models import User
from api_v1.dependencies.games import Player, Preferences


router = APIRouter(prefix=settings.api.v1.games)


@router.websocket("")
async def websocket_function(websocket: WebSocket, user: User = Depends(get_current_user_from_token)):
    await websocket.accept()
    data = await websocket.receive_text()
    print("User is ", user.email, user.id)
    try:
        preferences = Preferences(data)
    except:
        websocket.close(1000)
    print(preferences)
    player = Player(websocket, user, preferences, settings.matchmaking.initial_elo_difference)
    await websocket.send_text(data)

