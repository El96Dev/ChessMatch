import json
from enum import Enum
from datetime import datetime
from chess import Board, Move
from fastapi import HTTPException, status, Depends

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
    draw_offered: bool = False
    sequence_number: int = 1
    started_at: datetime
    ended_at: datetime


    async def __init__(self, game_id: int, white_player: Player, black_player: Player, current_datetime: datetime):
        self.game_id = game_id
        self.white_player = white_player
        self.black_player = black_player
        self.board = Board()
        self.draw_offered = False
        self.started_at = current_datetime

        message_to_white = json.dumps({"action": "start_game", 
                                       "player_color": "white",
                                       "opponent": {"username": self.black_player.user.username, 
                                                    "rating": self.black_player.user.elo_rating}})
        message_to_black = json.dumps({"action": "start_game", 
                                       "player_color": "black",
                                       "opponent": {"username": self.white_player.user.username, 
                                                    "rating": self.white_player.user.elo_rating}})   
        self.white_player.send_json_message(message_to_white)
        self.black_player.send_json_message(message_to_black)
        self.current_player = self.white_player


    def change_current_player(self):
        if self.current_player == self.white_player:
            self.current_player = self.black_player
        else:
            self.current_player = self.white_player


    async def game_loop(self):
        while not self.board.is_game_over:
            json_message = await self.current_player.get_json_message()
            await self.process_message(json_message)                                                                                       


    async def process_message(self, json_message: json):
        try:
            data = json.loads(json_message)
        except json.JSONDecodeError as e:   
            self.current_player.send_json_message({"action": "json_error", "detail": e})

        if "action" not in data:
            self.current_player.send_json_message({"action": "message_error", "detail": "Action field required"})
        else:
            action = data["action"]
            if action == "move":
                if "move" not in data:
                    self.current_player.send_json_message({"action": "message_error", "detail": "Move field required"})
                else:
                    move_str = data["move"]
                    move = Move(move_str)
                    if self.board.is_valid(move):
                        self.board.push(move)
                        await crud.add_move(self.game_id, move_str, self.sequence_number, 
                                            session=Depends(db_helper.scoped_session_dependency))
                        self.sequence_number += 1
                        self.change_current_player()
                    else:
                        self.current_player.send_json_message({"action": "move_error", "detail": "Illegal move"})
            elif action == "offer_draw":
                if not self.draw_offered:
                    self.draw_offered = True
                else:
                    self.current_player.send_json_message({"action": "message_error", "detail": "Draw has already been offered"})
            elif action == "accept_draw":
                if self.draw_offered:
                    self.on_draw()
                else:
                    self.current_player.send_json_message({"action": "message_error", "detail": "Draw hasn't been offered"})
            elif action == "resign":
                pass


    async def send_message_to_all(self, message: json):
        await self.white_player.send_json_message(message)
        await self.black_player.send_json_message(message)

    
    def is_white_turn(self) -> bool:
        return self.board.turn


    def check_mate(self) -> bool:
        return self.board.is_checkmate()


    def on_draw(self):
        self.ended_at = datetime.now()
        self.game_result = GameResult.DRAW
        await self.update_elo_rating()
        await crud.set_game_results(self.game_id, self.ended_at, self.game_result, session = Depends(db_helper.scoped_session_dependency))
        self.send_game_over_messages()


    def on_resign(self):
        self.ended_at = datetime.now()
        if self.current_player == self.white_player:
            self.game_result = GameResult.BLACK
        elif self.current_player == self.black_player:
            self.game_result = GameResult.WHITE
        await self.update_elo_rating()
        await crud.set_game_results(self.game_id, self.ended_at, self.game_result, session = Depends(db_helper.scoped_session_dependency))
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
            self.white_player.send_json_message({"action": "game_ended", "result": "White wins"})
            self.black_player.send_json_message({"action": "game_ended", "result": "White wins"})
        elif self.game_result == GameResult.BLACK:
            self.white_player.send_json_message({"action": "game_ended", "result": "Black wins"})
            self.white_player.send_json_message({"action": "game_ended", "result": "Black wins"})
        elif self.game_result == GameResult.DRAW:
            self.white_player.send_json_message({"action": "game_ended", "result": "Draw"})
            self.white_player.send_json_message({"action": "game_ended", "result": "Draw"})