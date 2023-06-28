from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Integer
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    __table_args__ = {'extend_existing': True}


class Player(Base):
    __tablename__ = "players"

    id = mapped_column(Integer, primary_key=True)
    telegram_id = mapped_column(BigInteger, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(32))
    fullname: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(insert_default=func.now())
    is_admin: Mapped[bool]

    # games: Mapped[Optional[List["Game"]]] = relationship('Game', back_populates='players')
    # records: Mapped[Optional[List["Record"]]] = relationship(back_populates='records')


class Record(Base):
    __tablename__ = "records"

    id = mapped_column(Integer, primary_key=True)
    player_id = mapped_column(ForeignKey("players.id"))
    game_id = mapped_column(ForeignKey("games.id"))
    buy_in: Mapped[int]
    buy_out: Mapped[Optional[int]]


class Game(Base):
    __tablename__ = "games"

    id = mapped_column(Integer, primary_key=True)
    start_time: Mapped[datetime] = mapped_column(insert_default=func.now())
    finish_time: Mapped[Optional[datetime]]
    total_pot: Mapped[Optional[int]]
    chip_leader = mapped_column(ForeignKey("players.id"))
    host = mapped_column(ForeignKey("players.id"))
    admin = mapped_column(ForeignKey("players.id"))

    # players: Mapped[List["Player"]] = relationship('Player', back_populates='games')
    # records: Mapped[Optional[List["Record"]]] = relationship(back_populates='records')


class Debt(Base):
    __tablename__ = "debts"

    id = mapped_column(Integer, primary_key=True)
    game = mapped_column(ForeignKey("games.id"))
    creditor = mapped_column(ForeignKey("players.id"))
    debtor = mapped_column(ForeignKey("players.id"))
    amount = Mapped[int]
