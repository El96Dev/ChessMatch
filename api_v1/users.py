from fastapi import APIRouter

from api_v1.fastapi_users_object import fastapi_users_obj
from core.config import settings
from core.schemas.user import UserRead, UserUpdate


router = APIRouter(
    prefix=settings.api.v1.users,
    tags=["Users"]
)

router.include_router(
    router=fastapi_users_obj.get_users_router(UserRead, UserUpdate)
)