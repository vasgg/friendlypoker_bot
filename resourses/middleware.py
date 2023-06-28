from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message
from sqlalchemy import literal

from db.database import session
from db.models import Player


class AuthMiddleware(BaseMiddleware):
    @staticmethod
    async def on_process_message(message: Message, data: dict) -> None:
        player = session.query(Player).filter(Player.telegram_id == message.from_user.id)
        user_exist = session.query(literal(True)).filter(player.exists()).scalar()
        if not user_exist:
            player = Player(telegram_id=message.from_user.id,
                            username=message.from_user.username,
                            fullname=message.from_user.full_name,
                            is_admin=False)
            session.add(player)
            session.commit()
            session.close()
