from typing import TYPE_CHECKING
from fastapi import Depends

from core.models import db_helper, User
if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_db(session: "AsyncSession" = Depends(db_helper.scoped_session_dependency)):
    yield User.get_db(session)