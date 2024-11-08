import asyncio
from datetime import datetime
from fastapi import Depends
from threading import Lock

from core.config import settings
from api_v1.games import crud
from core.models import db_helper
from .game import Game
from .player import Preferences, Player


lock = Lock()

players = []
games = []


async def find_matches():
    try:
        print("Find matches call")
        with lock:
            players_to_remove = []
            if len(players) >= 2:
                for i in range(len(players)):
                    if not players[i].is_connected():
                        players_to_remove.append(players[i])
                    if players[i] in players_to_remove:
                        continue
                    for j in range(i+1, len(players)):
                        if not players[j].is_connected():
                            players_to_remove.append(players[j])
                        if players[j] in players_to_remove:
                            continue
                        if players[i].check_for_match(players[j]):
                            players_to_remove.append(players[i])
                            players_to_remove.append(players[j])
                            current_datetime = datetime.now()
                            if (players[i].preferences == Preferences.WHITE or players[j].preferences == Preferences.BLACK or 
                               (players[i].preferences == Preferences.ANY and players[j].preferences == Preferences.ANY)):
                                white_player = players[i]
                                black_player = players[j]
                            elif players[i].preferences == Preferences.BLACK or players[j].preferences == Preferences.WHITE:
                                white_player = players[j]
                                black_player = players[i]
                            game_orm = await crud.create_game(white_player_id=white_player.user.id, black_player_id=black_player.user.id,
                                                              started_at=current_datetime, session=Depends(db_helper.scoped_session_dependency))
                            game = Game(game_orm.id, white_player, black_player, current_datetime)
                            games.append(game)
                for player in players_to_remove:
                    players.remove(player)
        print("Find matches ended!")

    except Exception as e:
        print(f"An exception occurred: {e}")


async def update_elo_diff():
    print("Update elo!")
    try:
        with lock:
            print("Len players" + str(len(players)), "Len end")
            print(len(players))
            for player in players:
                player.update_elo_difference(settings.matchmaking.elo_step, 
                                             settings.matchmaking.max_elo_diff, 
                                             settings.matchmaking.step_seconds_interval)
            if len(players) >= 2:
                asyncio.create_task(find_matches())

    except Exception as e:
        print(f"An exception occurred: {e}")