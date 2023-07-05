from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from config import dp
from resourses.functions import add_thousand, exiting_game_by_player, get_current_game, get_current_game_stats_for_player
from resourses.keyboards import add_funds_keyboard
from resourses.replies import answer
from resourses.states import States


@dp.message_handler(Command('game'))
async def game_command(message: types.Message):
    if not await get_current_game():
        await dp.bot.send_message(chat_id=message.from_user.id, text=answer['game_menu_new_game'])
    else:
        text = await get_current_game_stats_for_player(message.from_user.id)
        await dp.bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=add_funds_keyboard)


@dp.callback_query_handler(text='self add 1000')
async def adding_funds_by_player(call: types.CallbackQuery):
    await add_thousand(call.from_user.id)
    text = await get_current_game_stats_for_player(call.from_user.id)
    await dp.bot.send_message(chat_id=call.from_user.id, text=text)
    await call.answer()


@dp.callback_query_handler(text='exit game')
async def quit_game(call: types.CallbackQuery):
    await dp.bot.send_message(chat_id=call.from_user.id, text=answer['exit_game_by_player_reply'])
    await States.enter_remaining_balance.set()


@dp.message_handler(state=States.enter_remaining_balance)
async def remaining_balance_input(message: types.Message, state: FSMContext):
    try:
        balance = int(message.text)
        await exiting_game_by_player(telegram_id=message.from_user.id, buy_out=balance)
        text = await get_current_game_stats_for_player(message.from_user.id)
        await message.answer(text=text)
        await state.reset_state()
    except ValueError:
        await message.answer(text=answer['value_error_reply'])
