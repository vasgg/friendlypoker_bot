from aiogram import types
from aiogram.dispatcher.filters import Command

from config import dp
from resourses.replies import answer
from resourses.functions import add_thousand, get_current_game, get_current_game_stats_for_player
from resourses.keyboards import add_funds_keyboard


@dp.message_handler(Command('game'))
async def game_command(message: types.Message):
    if not await get_current_game():
        await dp.bot.send_message(chat_id=message.from_user.id,
                                  text=answer['game_menu_new_game'])
    else:
        text = await get_current_game_stats_for_player(message.from_user.id)
        await dp.bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=add_funds_keyboard)


@dp.callback_query_handler(text='self add 1000')
async def adding_funds_by_player(call: types.CallbackQuery):
    await add_thousand(call.from_user.id)
    text = await get_current_game_stats_for_player(call.from_user.id)
    await dp.bot.send_message(chat_id=call.from_user.id, text=text)
    # await call.answer()
