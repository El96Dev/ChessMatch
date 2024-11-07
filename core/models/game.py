from enum import Enum
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, DateTime, func, Enum as SqlAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
if TYPE_CHECKING:
    from .user import User


class GameResult(Enum):
    WHITE = "WHITE"
    BLACK = "BLACK"
    DRAW = "DRAW"


class Game(Base):
    __tablename__ = "games"

    moves: Mapped[list["Move"]] = relationship("Move", back_populates="game")
    white_player_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    white_player: Mapped["User"] = relationship("User", foreign_keys=[white_player_id], back_populates="white_games")
    black_player_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    black_player: Mapped["User"] = relationship("User", foreign_keys=[black_player_id], back_populates="black_games")
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    ended_at: Mapped[datetime] = mapped_column(nullable=True)
    result: Mapped[GameResult] = mapped_column(SqlAlchemyEnum(GameResult), nullable=True)


class Move(Base):
    __tablename__ = "moves"

    move: Mapped[str] = mapped_column(nullable=False)
    sequence_number: Mapped[int] = mapped_column(nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False)
    game: Mapped[Game] = relationship("Game", back_populates="moves")    
