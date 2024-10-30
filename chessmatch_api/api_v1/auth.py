from fastapi import APIRouter

from .fastapi_users_object import fastapi_users_obj
from core.config import settings
from core.schemas.user import UserRead, UserCreate
from dependencies.authentication.backend import auth_backend


router = APIRouter(
    prefix=settings.api.v1.auth,
    tags=["Auth"]
)

router.include_router(
    router=fastapi_users_obj.get_auth_router(auth_backend),
)

router.include_router(
    router=fastapi_users_obj.get_register_router(UserRead, UserCreate)
)