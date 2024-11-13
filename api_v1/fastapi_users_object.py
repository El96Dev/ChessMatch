from fastapi import Depends, HTTPException, WebSocket, status
from fastapi_users import FastAPIUsers
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from .dependencies.authentication.users import get_user_db
from core.models import User
from .games import crud
from core.models import db_helper
from .dependencies.authentication.user_manager import get_user_manager
from .dependencies.authentication.backend import auth_backend
from core.config import settings


fastapi_users_obj = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)


current_active_user = fastapi_users_obj.current_user(active=True)


async def get_current_user_from_token(websocket: WebSocket, 
                                      session: AsyncSession = Depends(db_helper.scoped_session_dependency)) -> User | None:
    headers = websocket.headers
    auth_token = headers.get("authorization")

    if not auth_token:
        await websocket.close(code=1008, reason="Missing token")
        return None
    
    token = auth_token.split(" ")[1] if " " in auth_token else auth_token
    try:
        user = await crud.get_user_by_token(token, session)
        return user
    except HTTPException as e:
        await websocket.close(code=1008, reason=e.detail)