from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from config import dp
from db.database import session
from db.models import Player
from resourses.replies import answer


@dp.message_handler(CommandStart())
async def start_command(message: types.Message):
    player = session.query(Player).filter(Player.telegram_id == message.from_user.id).scalar()
    name = player.username if player.username else player.fullname
    reply = answer['start_reply'].format(name, player.id)
    await dp.bot.send_message(chat_id=message.from_user.id, text=reply)
