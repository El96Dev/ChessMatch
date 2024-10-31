from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from typing import TYPE_CHECKING

from .base import Base
if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from .game import Game


class User(Base, SQLAlchemyBaseUserTable[int]):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    elo_rating: Mapped[int] = mapped_column(default=0) 
    avatar_filename: Mapped[str] = mapped_column(default="default.jpg")
    white_games: Mapped[list["Game"]] = relationship("Game", foreign_keys="[Game.white_player_id]", back_populates="white_player")
    black_games: Mapped[list["Game"]] = relationship("Game", foreign_keys="[Game.black_player_id]", back_populates="black_player")


    @classmethod
    def get_db(cls, session: "AsyncSession"):
        return SQLAlchemyUserDatabase(session, User)
