from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from api_v1.fastapi_users_object import current_active_user
from api_v1.dependencies.images import get_image_filepath
from core.models.db_helper import db_helper
from core.models import User
from . import crud


router = APIRouter(prefix=settings.api.v1.profile, tags=["Profile"])

@router.get("/{user_id}")
async def get_user_profile(user_id: int,
                           user: User = Depends(current_active_user), 
                           session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    user_data = await crud.get_profile_data_by_id(user_id, session)
    return user_data


@router.get("/{user_id}/avatar")
async def get_user_avatar(user_id: int, 
                          user: User = Depends(current_active_user),
                          session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    avatar_filepath = get_image_filepath(user_id)
    return FileResponse(avatar_filepath)


@router.get("/me/avatar")
async def get_avatar(user: User = Depends(current_active_user)):
    avatar_filepath = get_image_filepath(user.id)
    return FileResponse(avatar_filepath)


@router.post("/me/avatar")
async def post_avatar(avatar: UploadFile,
                      user: User = Depends(current_active_user),
                      session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    await crud.set_avatar(user, avatar, session)


@router.delete("/me/avatar")
async def delete_avatar(user: User = Depends(current_active_user),
                        session: AsyncSession = Depends(db_helper.scoped_session_dependency)):
    await crud.delete_avatar(user, session)

