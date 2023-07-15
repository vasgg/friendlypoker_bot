from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, Integer
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    __table_args__ = {'extend_existing': True}


class Player(Base):
    __tablename__ = "players"

    id = mapped_column(Integer, primary_key=True)
    telegram_id = mapped_column(BigInteger, nullable=False, unique=True)
    username: Mapped[Optional[str]] = mapped_column(String(32))
    fullname: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(insert_default=datetime.utcnow())
    is_admin: Mapped[bool] = mapped_column(insert_default=False)

    # games: Mapped[Optional[List["Game"]]] = relationship('Game', back_populates='players')
    # records: Mapped[Optional[List["Record"]]] = relationship(back_populates='records')

    def __lt__(self, other):
        return self.id < other.id


class Record(Base):
    __tablename__ = "records"

    id = mapped_column(Integer, primary_key=True)
    player_id = mapped_column(ForeignKey("players.id"))
    player_telegram_id = mapped_column(ForeignKey("players.telegram_id"))
    game_id = mapped_column(ForeignKey("games.id"))
    buy_in: Mapped[int]
    buy_out: Mapped[Optional[int]]
    net_profit: Mapped[Optional[int]]
    ROI: Mapped[Optional[int]]
    connected_at: Mapped[datetime] = mapped_column(insert_default=datetime.utcnow())
    exited_at: Mapped[Optional[datetime]]

    def __lt__(self, other):
        return self.buy_in < other.buy_in


class Game(Base):
    __tablename__ = "games"

    id = mapped_column(Integer, primary_key=True)
    start_time: Mapped[datetime] = mapped_column(insert_default=datetime.utcnow())
    finish_time: Mapped[Optional[datetime]]
    total_pot: Mapped[Optional[int]]
    table_size: Mapped[Optional[int]]
    MVP = mapped_column(ForeignKey("players.id"))
    host = mapped_column(ForeignKey("players.id"))
    admin = mapped_column(ForeignKey("players.id"))

    # players: Mapped[List["Player"]] = relationship('Player', back_populates='games')
    # records: Mapped[Optional[List["Record"]]] = relationship(back_populates='records')


class Debt(Base):
    __tablename__ = "debts"

    id = mapped_column(Integer, primary_key=True)
    game_id = mapped_column(ForeignKey("games.id"), nullable=False)
    creditor_id = mapped_column(ForeignKey("players.id"))
    debtor_id = mapped_column(ForeignKey("players.id"))
    amount = mapped_column(Integer)
    paid = mapped_column(Boolean, insert_default=False)
    created_at: Mapped[datetime] = mapped_column(insert_default=datetime.utcnow())
    paid_at: Mapped[Optional[datetime]]

    # def __repr__(self):
    #     return f"<New debt. {self.debtor_id} dued {self.amount} to {self.creditor_id}>"
