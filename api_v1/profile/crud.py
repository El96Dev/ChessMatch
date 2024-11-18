from sqlalchemy import select, func
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, UploadFile
from fastapi.responses import FileResponse

from core.models import User, Game
from core.config import settings
from api_v1.dependencies.images import check_image_size, save_avatar, delete_avatar, get_image_filepath


async def get_profile_data_by_id(user_id: int, session: AsyncSession):
    white_game_alias = aliased(Game)
    black_game_alias = aliased(Game)
    
    stmt = select(User, (func.count(white_game_alias.id).filter(white_game_alias.white_player_id == user_id) + \
                         func.count(black_game_alias.id).filter(black_game_alias.black_player_id == user_id)).label("total_games_played")). \
                         outerjoin(white_game_alias, User.id == white_game_alias.white_player_id). \
                         outerjoin(black_game_alias, User.id == black_game_alias.black_player_id).where(User.id == user_id).group_by(User.id)
    result = await session.execute(stmt)
    user, total_games_played = result.first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} was not found!")

    user.total_games_played = total_games_played
    return user


async def get_user_avatar(user_id: int, session: AsyncSession):
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalars().one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} was not found!")
    
    return FileResponse(get_image_filepath(user_id))


async def set_avatar(user: User, avatar: UploadFile, session: AsyncSession):
    if avatar.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Image must be in jpeg or png format!")
    
    if not check_image_size(avatar, settings.images.kb_image_limit):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Image size must be less than {settings.images.kb_image_limit} Kb!")

    save_avatar(user.id, avatar)
    User.avatar_filename = str(user.id) + "." + avatar.content_type.split("/")[-1]
    await session.commit()


async def delete_user_avatar(user: User, session: AsyncSession):
    delete_avatar(user.id)
    user.avatar_filename = "default"
    await session.commit()
    

async def check_if_user_exists(user_id: int, session: AsyncSession):
    stmt = select(User).where(User.id == user_id).exists()
    return await session.scalar(select(stmt))