from aiogram import types

from config import dp, telegram_group
from resourses.functions import *
from resourses.replies import answer


@dp.callback_query_handler(text='end game')
async def game_finisher(call: types.CallbackQuery):
    game: Game = await get_current_game()
    remaining_players = await get_remaining_players_in_game()
    if remaining_players:
        await dp.bot.send_message(chat_id=call.from_user.id, text=answer['remaining_players_in_game'].format(str(remaining_players)))
    else:
        results = await check_balance_after_game()
        if results.delta != 0:
            await dp.bot.send_message(chat_id=call.from_user.id, text=answer['exit_game_wrong_total_sum'].format(results.delta))
        else:
            king = await get_king_of_kush(game.id)
            await commit_game_results_to_db(game.id, results.total_pot, king)
            await dp.bot.send_message(chat_id=telegram_group, text='game over')
