from fastapi import WebSocket
from typing import TYPE_CHECKING
from datetime import datetime
from enum import Enum

from core.models import User


class Preferences(Enum):
    WHITE = "white"
    BLACK = "black"
    ANY = "any"


class Player():
    user: User
    websocket: WebSocket
    last_elo_increment: datetime
    preferences: Preferences
    elo_difference: int


    def __init__(self, websocket: WebSocket, user: User, preferences: str, elo_difference: int) -> None:
        self.websocket = websocket
        self.user = user
        self.last_elo_increment = datetime.now()
        self.preferences = preferences
        self.elo_difference = elo_difference


    def increase_elo_difference(self, elo_step: int, max_elo_diff: int, step_seconds_interval: int):
        waiting_seconds = (datetime.now() - self.last_elo_increment).total_seconds()
        if waiting_seconds >= step_seconds_interval:
            if self.elo_difference + elo_step <= max_elo_diff:
                self.elo_difference += elo_step
                self.last_elo_increment = datetime.now()
    

    def check_for_match(self, opponent: 'Player') -> bool:
        if self.preferences != opponent.preferences:
            elo_diff = abs(self.user.elo_rating - opponent.user.elo_rating)
            if self.elo_difference >= elo_diff and opponent.elo_difference >= elo_diff:
                return True
        return False
    
