import asyncio
from threading import Lock

from core.config import settings
from .list import ThreadSafeList
from .game import Game
from .player import Player


lock = Lock()

players = []
games = []


async def find_matches():
    try:
        print("Find matches call")
        with lock:
            matched_players = []
            if len(players) >= 2:
                for i in range(len(players)):
                    if players[i] in matched_players:
                        continue
                    for j in range(i+1, len(players)):
                        if players[j] in matched_players:
                            continue
                        if players[i].check_for_match(players[j]):
                            matched_players.append(players[i])
                            matched_players.append(players[j])
                            game = Game(players[i], players[j])
                            games.append(game)
                for player in matched_players:
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