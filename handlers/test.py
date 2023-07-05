from aiogram import types
from aiogram.dispatcher.filters import Command

from config import dp
from resourses.functions import debt_counter


@dp.message_handler(Command('test'))
async def testing_stuff(message: types.Message):
    await debt_counter(1)
    text = 'just testing'
    await dp.bot.send_message(chat_id=message.from_user.id, text=text)
