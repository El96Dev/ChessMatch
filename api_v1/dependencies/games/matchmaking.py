import asyncio
from collections import deque
from datetime import datetime
from threading import RLock
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, WebSocketDisconnect

from core.config import settings
from api_v1.games import crud
from core.models import db_helper, Game
from .game import Game
from .gamemanager import game_manager
from .player import Preferences, Player


class MatchmakingSystem:
    
    def __init__(self):
        self.deque = deque()
        self.lock = RLock()


    async def add_player(self, player: Player, session: AsyncSession):
        with self.lock:
            self.deque.append(player)
            await player.send_json_message({"action": "start_waiting", "preferences": player.preferences.value})
            await self.match_players(session)


    async def match_players(self, session: AsyncSession):
        player1 = self.deque[-1]
        for player2 in self.deque:
            if player1 == player2:
                continue
            if abs(player1.user.elo_rating - player2.user.elo_rating) <= settings.matchmaking.max_elo_diff:
                if ((player1.preferences == Preferences.WHITE or player2.preferences == Preferences.BLACK) and player1.preferences != player2.preferences) or \
                   (player1.preferences == Preferences.ANY and player2.preferences == Preferences.ANY):
                   print("Found match", player1.user.email, player2.user.email)
                   await game_manager.create_game(player1.user.id, player2.user.id, session)
                   self.deque.remove(player1)
                   self.deque.remove(player2)

                elif (player1.preferences == Preferences.BLACK or player2.preferences == Preferences.WHITE) and player1.preferences != player2.preferences:
                    print("Found match", player1.user.email, player2.user.email)
                    await game_manager.create_game(player2.user.id, player1.user.id, session)
                    self.deque.remove(player1)
                    self.deque.remove(player2)
                


matchmaking_system = MatchmakingSystem()
