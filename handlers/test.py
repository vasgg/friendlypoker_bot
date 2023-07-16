from aiogram import types
from aiogram.dispatcher.filters import Command

from config import dp
from resourses.keyboards import get_paid_button


@dp.message_handler(Command('test'))
async def testing_stuff(message: types.Message):
    text = 'just testing'
    await dp.bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=await get_paid_button(1))
