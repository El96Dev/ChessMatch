from typing import Dict
from datetime import datetime
from threading import RLock
from fastapi import WebSocket
from chess import Move
from sqlalchemy.ext.asyncio import AsyncSession

from .game import Game
from .player import Player
from api_v1.games import crud


class GameManager:
    games: Dict[int, Game]
    lock: RLock


    def __init__(self):
        self.games = dict()
        self.lock = RLock()

    
    async def create_game(self, white_player: Player, black_player: Player, session: AsyncSession):
        with self.lock:
            current_datetime = datetime.now()
            game_orm = await crud.create_game(white_player_id=white_player.user.id, black_player_id=black_player.user.id,
                                              started_at=current_datetime, session=session)
            game = Game(game_orm.id, white_player, black_player, current_datetime)
            self.games[game.game_id] = game
            await self.games[game.game_id].send_game_start_messages()


    async def on_json_message(self, username: str, websocket: WebSocket, data: Dict, session: AsyncSession):
        if "action" not in data:
            await websocket.send_json({"action": "message_error", "detail": "'action' field is required"})
            return
        elif "game_id" not in data:
            await websocket.send_json({"action": "message_error", "detail": "'game_id' field is required"})
            return 

        game_id = int(data["game_id"])

        if game_id in self.games:
            if not self.games[game_id].is_game_member(username):
                await websocket.send_json({"action": "message_error", "detail": "You are not a game member"})
        else:
            await websocket.send_json({"action": "message_error", "detail": "Game wasn't found"})
            return 

        action = data["action"]

        if action == "move":
            if "move" not in data:
                websocket.send_json_message({"action": "message_error", "detail": "'move' field is required"})
                return 
            else:
                move_str = data["move"]
                try:
                    move = Move.from_uci(move_str)
                    await self.games[game_id].on_move(move, username, websocket)
                except ValueError:
                    websocket.send_json({"action": "move_error", "detail": "Incorrect move syntax"})
        elif action == "offer_draw":
            await self.games[game_id].on_draw_offered(username, websocket, session)
        elif action == "accept_draw":
            await self.games[game_id].on_draw_accepted(username, websocket, session)
        elif action == "resign":
            await self.games[game_id].on_resign(username, session)

        if self.games[game_id].ended_at is not None:
            del self.games[game_id]


    async def on_websocket_disconnected(self, websocket: WebSocket, session: AsyncSession):
        with self.lock:
            for game in self.games:
                if game.contains_websocket(websocket):
                    game.on_websocket_disconnected(websocket, session)


game_manager = GameManager()