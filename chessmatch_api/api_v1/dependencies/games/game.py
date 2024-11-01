from enum import Enum
from typing import TYPE_CHECKING
from datetime import datetime
from chess import Board, Move
from fastapi import HTTPException, status

if TYPE_CHECKING:
    from .player import Player, Preferences
    from core.models import User


class Winner(Enum):
    WHITE = "white"
    BLACK = "black"
    DRAW = "draw"


class Game():
    white_player: "Player"
    black_player: "Player"
    started_at: datetime
    ended_at: datetime
    winner: Winner
    board: Board


    def __init__(self, first_player: "Player", second_player: "Player"):
        if first_player.preferences == "white":
            self.white_player = first_player
            self.black_player = second_player
        elif second_player.preferences == "white":
            self.white_player = second_player
            self.black_player = first_player
        
        self.started_at = datetime.now()
    

    # def make_move(self, move_str: str, user: User):
    #     move = Move.from_uci(move_str)
    #     if user.username not in [self.white_player.username, self.black_player.username]:
    #         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You're not allowed to make moves in this game!")
    #     if self.board.turn:
    #         if user.username == self.white_player:
    #             if not self.board.is_legal(move):
    #                 raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="This move in unacceptable")
    #             else:
    #                 self.board.push(move)
    #         else:
    #             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="It's not your turn to make move!")
    #     else:
    #         if user.username == self.black_player:
    #             if not self.board.is_legal(move):
    #                 raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="This move in unacceptable")
    #             else:
    #                 self.board.push(move)
    #         else:
    #             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="It's not your turn to make move!")

    
    def check_mate(self) -> bool:
        return self.board.is_checkmate()


    def set_draw(self):
        self.ended_at = datetime.now()
        self.winner = Winner.DRAW