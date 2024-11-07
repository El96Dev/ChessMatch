import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status

from .dependencies import check_if_game_exists
from api_v1.dependencies.games.game import GameResult
from core.models import User, Game, Move, db_helper, AccessToken


async def get_user_by_token(token: str, session: AsyncSession):
    id_stmt = select(AccessToken.user_id).where(AccessToken.token==token)
    id_result = await session.execute(id_stmt)
    user_id = id_result.scalars().one_or_none()
    
    user_stmt = select(User).where(User.id==user_id)
    user_result = await session.execute(user_stmt)
    user = user_result.scalars().one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found!")
    
    return user


async def create_game(white_player_id: int, black_player_id: int, started_at: datetime, session: AsyncSession):
    game = Game(white_player_id=white_player_id, black_player_id=black_player_id, started_at=started_at)
    session.add(game)
    await session.commit()
    return game


async def add_move(game_id: int, move_str: str, sequence_number: int, session: AsyncSession):
    game_exists = await check_if_game_exists(game_id, session)
    if game_exists:
        move = Move(game_id=game_id, sequence_number=sequence_number, move=move_str)
        session.add(move)
        await session.commit()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Game with id {game_id} was not found!")


async def set_game_results(game_id: int, ended_at: datetime, game_result: GameResult, session: AsyncSession):
    stmt = select(Game).where(Game.id==game_id)
    result = await session.execute(stmt)
    game = result.scalars().one_or_none()
    if game:
        game.ended_at = ended_at
        game.result = game_result
        await session.commit()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Game with id {game_id} was not found!")
