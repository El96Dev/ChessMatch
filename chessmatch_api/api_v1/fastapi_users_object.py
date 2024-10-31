from fastapi_users import FastAPIUsers

from core.models import User
from .dependencies.authentication.user_manager import get_user_manager
from .dependencies.authentication.backend import auth_backend


fastapi_users_obj = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users_obj.current_user(active=True)