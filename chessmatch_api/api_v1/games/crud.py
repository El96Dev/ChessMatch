import select
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status

from core.models import User, db_helper, AccessToken


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




