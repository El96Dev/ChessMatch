from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    username: str
    elo_rating: int
    avatar_filename: str


class UserCreate(schemas.BaseUserCreate):
    username: str


class UserUpdate(schemas.BaseUserUpdate):
    username: str
