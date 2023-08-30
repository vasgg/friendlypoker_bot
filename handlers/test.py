from aiogram import types
from aiogram.dispatcher.filters import Command

from config import dp


@dp.message_handler(Command('test'))
async def testing_stuff(message: types.Message):
    text = '++++++'
    await dp.bot.send_message(chat_id=message.from_user.id, text=text)
    print(text)
