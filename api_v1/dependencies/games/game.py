import json
from enum import Enum
from datetime import datetime
from chess import Board, Move
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Depends, WebSocket, WebSocketDisconnect

from api_v1.games import crud
from core.models.game import GameResult
from core.models import db_helper
from .player import Player, Preferences


class Game:
    game_id: int
    white_player: Player
    black_player: Player
    current_player: Player
    board: Board
    draw_offered_by: str | None = None
    sequence_number: int = 1
    started_at: datetime
    ended_at: datetime | None = None


    def __init__(self, game_id: int, white_player: Player, black_player: Player, current_datetime: datetime):
        self.game_id = game_id
        self.white_player = white_player
        self.black_player = black_player
        self.board = Board()
        self.draw_offered = False
        self.started_at = current_datetime


    def is_game_member(self, username: str) -> bool:
        return self.white_player.user.username == username or self.black_player.user.username == username


    async def send_game_start_messages(self):
        try:
            message_to_white = {"action": "start_game", 
                                "player_color": "white",
                                "game_id": str(self.game_id),
                                "opponent": {"username": self.black_player.user.username, 
                                            "rating": self.black_player.user.elo_rating}}
            message_to_black = {"action": "start_game", 
                                "player_color": "black",
                                "game_id": str(self.game_id),
                                "opponent": {"username": self.white_player.user.username, 
                                            "rating": self.white_player.user.elo_rating}} 
            print(self.white_player.is_connected(), "white connection")
            print(self.black_player.is_connected(), "black connection")
            await self.white_player.send_json_message(message_to_white)
            await self.black_player.send_json_message(message_to_black)
        except WebSocketDisconnect:
            print("Websocket disconnect!")
        except RuntimeError as e:
            print("Runtime error", e)
                                                                            

    async def broadcast(self, message: json):
        await self.white_player.send_json_message(message)
        await self.black_player.send_json_message(message)

    
    def is_white_turn(self) -> bool:
        return self.board.turn


    async def on_move(self, move: Move, username: str, websocket: WebSocket):
        if self.draw_offered_by is not None and self.draw_offered_by != username:
            await websocket.send_json({"action": "move_error", "detail": "Draw has been offered. Accept or refuse it first."})
        elif (username == self.white_player.user.username and not self.board.turn) or \
             (username == self.black_player.user.username and self.board.turn):
            await websocket.send_json({"action": "move_error", "detail": "It's not your turn"}) 
        elif not self.board.is_legal(move):
            await websocket.send_json({"action": "move_error", "detail": "Illegal move"})
        else:
            self.board.push(move)
            await self.broadcast({"action": "move", "move": move.uci()})
            if self.board.is_checkmate():
                await self.on_checkmate()


    async def on_checkmate(self):
        self.ended_at = datetime.now()
        if self.board.turn:
            self.game_result = GameResult.BLACK
        else:
            self.game_result = GameResult.WHITE
        await self.update_elo_rating()
        await crud.set_game_results(self.game_id, self.ended_at, self.game_result, session = Depends(db_helper.scoped_session_dependency))
        await self.send_game_over_messages()
        

    async def on_draw(self, session: AsyncSession):
        self.ended_at = datetime.now()
        self.game_result = GameResult.DRAW
        await self.update_elo_rating()
        await crud.set_game_results(self.game_id, self.ended_at, self.game_result, session = Depends(db_helper.scoped_session_dependency))
        await self.send_game_over_messages()


    async def on_draw_offered(self, username: str, websocket: WebSocket):
        if self.draw_offered_by is not None:
            await websocket.send_json({"action": "draw_offered_error", "detail": "Draw has been offered. Accept or refuse it first."})
        else:
            self.draw_offered_by = username
            await self.broadcast({"action": "draw_offered", "username": username})

    
    async def on_draw_accepted(self, username: str, websocket: WebSocket, session: AsyncSession):
        if self.draw_offered_by is None:
            await websocket.send_json({"action": "draw_accepted_error", "detail": "Draw hasn't been offered."})
        else:
            await self.on_draw(session)


    async def on_resign(self, username: str, session: AsyncSession):
        self.ended_at = datetime.now()
        if username == self.white_player.user.username:
            self.game_result = GameResult.BLACK
        elif username == self.black_player.user.username:
            self.game_result = GameResult.WHITE
        await self.update_elo_rating()
        await crud.set_game_results(self.game_id, self.ended_at, self.game_result, session)
        self.send_game_over_messages()
        

    async def update_elo_rating(self, session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
        white_expected = 1//(1 + 10**((self.black_player.user.elo_rating-self.white_player.user.elo_rating)//400))
        black_expected = 1//(1 + 10**((self.white_player.user.elo_rating-self.black_player.user.elo_rating)//400))
        if self.white_player.user.elo_rating >= 2400:
            white_k = 10
        elif self.white_player.total_games_played > 30:
            white_k = 20
        elif self.white_player.total_games_played <= 30:
            white_k = 40

        if self.black_player.user.elo_rating >= 2400:
            black_k = 10
        elif self.black_player.total_games_played > 30:
            black_k = 20
        elif self.black_player.total_games_played <= 30:
            black_k = 40

        if self.game_result == GameResult.WHITE:
            new_white_elo = self.white_player.user.elo_rating + white_k*(1 - white_expected)
            new_black_elo = self.black_player.user.elo_rating + black_k*(0 - black_expected)
        elif self.game_result == GameResult.BLACK:
            new_white_elo = self.white_player.user.elo_rating + white_k*(0 - white_expected)
            new_black_elo = self.black_player.user.elo_rating + black_k*(1 - black_expected)
        elif self.game_result == GameResult.DRAW:
            new_white_elo = self.white_player.user.elo_rating + white_k*(0.5 - white_expected)
            new_black_elo = self.black_player.user.elo_rating + black_k*(0.5 - black_expected)

        self.white_player.user.elo_rating = new_white_elo
        self.black_player.user.elo_rating = new_black_elo
        await session.commit()

    
    def send_game_over_messages(self):
        if self.game_result == GameResult.WHITE:
            self.broadcast({"action": "game_ended", "result": "White wins"})
        elif self.game_result == GameResult.BLACK:
            self.broadcast({"action": "game_ended", "result": "Black wins"})
        elif self.game_result == GameResult.DRAW:
            self.broadcast({"action": "game_ended", "result": "Draw"})