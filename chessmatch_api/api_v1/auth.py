from fastapi import APIRouter

from .fastapi_users_object import fastapi_users_obj
from api_v1.dependencies.authentication.backend import auth_backend


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

router.include_router(
    router=fastapi_users_obj.get_auth_router(auth_backend),
)