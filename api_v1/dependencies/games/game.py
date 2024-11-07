import json
from enum import Enum
from datetime import datetime
from chess import Board, Move
from fastapi import HTTPException, status

from .player import Player, Preferences


class Winner(Enum):
    WHITE = "white"
    BLACK = "black"
    DRAW = "draw"


class Game:
    white_player: Player
    black_player: Player
    current_player: Player
    board: Board
    draw_offered: bool = False
    started_at: datetime
    ended_at: datetime


    def __init__(self, first_player: Player, second_player: Player):
        self.board = Board()
        self.draw_offered = False
        self.started_at = datetime.now()

        if first_player.preferences == Preferences.WHITE or second_player.preferences == Preferences.BLACK:
            self.white_player = first_player
            self.black_player = second_player
        elif first_player.preferences == Preferences.BLACK or second_player.preferences == Preferences.WHITE:
            self.white_player = second_player
            self.black_player = first_player
        elif first_player.preferences == Preferences.ANY and second_player.preferences == Preferences.ANY:
            self.white_player = first_player
            self.black_player = second_player

        message_to_white = json.dumps({"action": "start_game", 
                                       "player_color": "white",
                                       "opponent": {"username": self.black_player.user.username, 
                                                    "rating": self.black_player.user.elo_rating}})
        message_to_black = json.dumps({"action": "start_game", 
                                       "player_color": "black",
                                       "opponent": {"username": self.white_player.user.username, 
                                                    "rating": self.white_player.user.elo_rating}})   
        self.current_player = self.white_player


    def change_current_player():
        if self.current_player == self.white_player:
            self.current_player = self.black_player
        else:
            self.current_player = self.white_player


    async def game_loop():
        while self.board.is_checkmate:
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
                        self.change_current_player()
                    else:
                        self.current_player.send_json_message({"action": "move_error", "detail": "Illegal move"})
            elif action == "offer_draw":
                if not self.draw_offered:
                    self.draw_offered = True
                else:
                    current_player.send_json_message({"action": "message_error", "detail": "Draw has already been offered"})
            elif action == "accept_draw":
                if self.draw_offered:
                   pass 
            elif action == "resign":
                pass


    async def send_message_to_all(self, message: json):
        await self.white_player.send_json_message(message)
        await self.black_player.send_json_message(message)

    
    def is_white_turn(self) -> bool:
        return self.board.turn


    def check_mate(self) -> bool:
        return self.board.is_checkmate()


    def set_draw(self):
        self.ended_at = datetime.now()
        self.winner = Winner.DRAW