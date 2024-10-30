from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from .base import Base


class User(Base, SQLAlchemyBaseUserTable[int]):
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    elo_rating: Mapped[int] = mapped_column(default=0) 
    avatar_filename: Mapped[str] = mapped_column(default="default.jpg")
