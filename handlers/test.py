from aiogram import types
from aiogram.dispatcher.filters import Command

from config import dp
from resourses.functions import commit_debts_to_db, debt_calculator


@dp.message_handler(Command('test'))
async def testing_stuff(message: types.Message):
    transactions = await debt_calculator(1)
    text = 'just testing'
    await dp.bot.send_message(chat_id=message.from_user.id, text=text)
    await commit_debts_to_db(transactions)
