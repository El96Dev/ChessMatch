from typing import TYPE_CHECKING
from fastapi import Depends
from fastapi_users.authentication.strategy.db import DatabaseStrategy

from core.config import settings
from .access_tokens import get_access_token_db
if TYPE_CHECKING:
    from core.models import AccessToken
    from fastapi_users.authentication.strategy.db import AccessTokenDatabase


def get_database_strategy(
    access_token_db: "AccessTokenDatabase[AccessToken]" = Depends(get_access_token_db)
) -> DatabaseStrategy:
    return DatabaseStrategy(
        access_token_db, 
        lifetime_seconds=settings.access_token.lifetime_seconds,
    )