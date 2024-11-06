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
    def __init__(self, first_player: Player, second_player: Player):
        print("Inside Game __init__", first_player.user.username, second_player.user.username)
        self.board = Board()
        self.started_at = datetime.now()
        print("Started at", self.started_at)

        if first_player.preferences == Preferences.WHITE or second_player.preferences == Preferences.BLACK:
            self.white_player = first_player
            self.black_player = second_player
        elif first_player.preferences == Preferences.BLACK or second_player.preferences == Preferences.WHITE:
            self.white_player = second_player
            self.black_player = first_player
        elif first_player.preferences == Preferences.ANY and second_player.preferences == Preferences.ANY:
            self.white_player = first_player
            self.black_player = second_player
        
        print("Game created! white:", self.white_player.user.username, " black", self.black_player.user.username)

        self.started_at = datetime.now()
        print("Started at ", self.started_at)

    
    def check_mate(self) -> bool:
        return self.board.is_checkmate()


    def set_draw(self):
        self.ended_at = datetime.now()
        self.winner = Winner.DRAW