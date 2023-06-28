from aiogram import types
from aiogram.dispatcher import FSMContext

from config import dp
from db.database import session
from db.models import Game, Player, Record
from resourses.functions import get_current_game, get_list_of_id_and_names, get_players
from resourses.replies import answer
from resourses.states import States


# from bot.utils.keyboards import tools


@dp.callback_query_handler(text='new game')
async def game_starter(call: types.CallbackQuery):
    await States.Missing_playsers.set()
    text = await get_list_of_id_and_names() + '\n' + answer["players_reply"]
    await dp.bot.send_message(chat_id=call.from_user.id, text=text)


@dp.message_handler(state=States.Missing_playsers)
async def missing_players_input(message: types.Message, state: FSMContext):
    missing_players = [int(num) for num in str(message.text).strip().split()]
    if 0 in missing_players:
        await dp.bot.send_message(chat_id=message.from_user.id, text=answer["host_game"])
        await States.Host_selection.set()

    else:
        await state.update_data(missing_players=missing_players)

        await dp.bot.send_message(chat_id=message.from_user.id, text=answer["host_game_with_missing_players"]
                                  .format(missing_players))
        await States.Host_selection.set()


@dp.message_handler(state=States.Host_selection)
async def host_choosing(message: types.Message, state: FSMContext):
    host = message.text
    data = await state.get_data()
    try:
        ans = data['missing_players']
        attending_players = await get_players(exluded=ans)
    except KeyError:
        attending_players = await get_players()
    admin = session.query(Player.id).where(Player.telegram_id == message.from_user.id)
    game = Game(host=host,
                admin=admin)

    session.add(game)
    session.commit()

    game = await get_current_game()

    for player in attending_players:
        record = Record(player_id=player.id,
                        player_telegram_id=player.telegram_id,
                        game_id=game.id,
                        buy_in=1000)
        session.add(record)

    session.commit()
    session.close()
    await dp.bot.send_message(chat_id=message.from_user.id, text='ready game and records')
    await state.reset_state()
