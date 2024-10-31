from fastapi import APIRouter, Depends
from typing import TYPE_CHECKING

from core.config import settings
from api_v1.fastapi_users_object import current_active_user
if TYPE_CHECKING:
    from core.models import User


router = APIRouter(prefix=settings.api.v1.games)

@router.post("")
def start_waiting(user: User = Depends(current_active_user)):
    pass
