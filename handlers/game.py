from aiogram import types
from aiogram.dispatcher.filters import Command

from config import dp
from resourses.replies import answer
from resourses.functions import get_current_game
from resourses.keyboards import add_funds_keyboard


@dp.message_handler(Command('game'))
async def game_command(message: types.Message):
    if not await get_current_game():
        await dp.bot.send_message(chat_id=message.from_user.id,
                                  text=answer['game_menu_new_game'])
    else:
        await dp.bot.send_message(chat_id=message.from_user.id,
                                  text=answer["game_menu_current_game"], reply_markup=add_funds_keyboard)
