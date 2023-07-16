from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from sqlalchemy import update

from config import dp, redis, telegram_group
from db.database import session
from db.models import Debt, Game, Player, Record
from resourses.functions import add_thousand, check_balance_after_game, commit_debts_to_db, commit_game_results_to_db, debt_calculator, \
    debt_informer_by_id, exiting_game_by_player, get_current_game, get_current_game_stats_for_player, get_group_game_report, \
    get_list_of_id_and_names, get_list_of_players_and_buy_ins, get_mvp, get_players, get_remaining_players_in_game, \
    get_telegram_id_from_player_id, get_username_from_player_id
from resourses.keyboards import add_funds_keyboard, add_keyboard, get_paid_button_confirmation
from resourses.replies import answer
from resourses.states import States


@dp.message_handler(Command('game'))
async def game_command(message: types.Message):
    game = await get_current_game()
    if not game:
        await dp.bot.send_message(chat_id=message.from_user.id, text=answer['game_menu_new_game'])
    else:
        text = await get_current_game_stats_for_player(message.from_user.id, game.id)
        await dp.bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=add_funds_keyboard)


@dp.callback_query_handler(text='self add 1000')
async def adding_funds_by_player(call: types.CallbackQuery):
    game = await get_current_game()
    await add_thousand(call.from_user.id, game.id)
    caption = answer['start_game_report'].format(game.id)
    stats = await get_list_of_players_and_buy_ins(game.id)
    text = caption + stats
    group_message_id = redis.get('group_message_id')
    personal_message_id = redis.get('personal_message_id')
    await dp.bot.edit_message_text(chat_id=telegram_group, text=text, message_id=group_message_id, reply_markup=add_keyboard)
    add_funds_report = answer['add_funds_report'].format(game.id)
    text = add_funds_report + stats
    await dp.bot.edit_message_text(chat_id=call.from_user.id, text=text, message_id=personal_message_id)
    await dp.bot.send_message(chat_id=call.from_user.id, text=add_funds_report)
    await call.answer()


@dp.callback_query_handler(text='new game')
async def game_starter(call: types.CallbackQuery):
    await States.missing_playsers.set()
    text = await get_list_of_id_and_names() + '\n' + answer["players_reply"]
    await dp.bot.send_message(chat_id=call.from_user.id, text=text)


@dp.message_handler(state=States.missing_playsers)
async def missing_players_input(message: types.Message, state: FSMContext):
    missing_players = [int(num) for num in str(message.text).strip().split()]
    if 0 in missing_players:
        await dp.bot.send_message(chat_id=message.from_user.id, text=answer["host_game"])
        await States.host_selection.set()
    else:
        await state.update_data(missing_players=missing_players)
        await dp.bot.send_message(chat_id=message.from_user.id, text=answer["host_game_with_missing_players"]
                                  .format(missing_players))
        await States.host_selection.set()


@dp.message_handler(state=States.host_selection)
async def host_choosing(message: types.Message, state: FSMContext):
    host = message.text
    data = await state.get_data()
    try:
        missing_players = data['missing_players']
        attending_players = await get_players(exluded=missing_players)
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
    caption = answer['start_game_report'].format(game.id)
    text = await get_list_of_players_and_buy_ins(game.id)
    group_message = await dp.bot.send_message(chat_id=telegram_group, text=caption + text, reply_markup=add_keyboard)
    personal_message = await dp.bot.send_message(chat_id=message.from_user.id, text=caption + text, reply_markup=add_keyboard)
    redis.set('group_message_id', group_message.message_id)
    redis.set('personal_message_id', personal_message.message_id)
    await state.reset_state()


@dp.callback_query_handler(text='exit game')
async def quit_game(call: types.CallbackQuery):
    await dp.bot.send_message(chat_id=call.from_user.id, text=answer['exit_game_by_player_reply'])
    await States.enter_remaining_balance.set()


@dp.message_handler(state=States.enter_remaining_balance)
async def remaining_balance_input(message: types.Message, state: FSMContext):
    game = await get_current_game()
    try:
        balance = int(message.text)
        await exiting_game_by_player(telegram_id=message.from_user.id, buy_out=balance)
        text = await get_current_game_stats_for_player(message.from_user.id, game.id)
        await dp.bot.send_message(chat_id=message.from_user.id, text=text)
        await state.reset_state()
    except ValueError:
        await dp.bot.send_message(chat_id=message.from_user.id, text=answer['value_error_reply'])


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
            transactions = await debt_calculator(game.id)
            MVP = await get_mvp(game.id)
            await commit_game_results_to_db(game.id, results.total_pot, MVP)
            await commit_debts_to_db(transactions)
            await debt_informer_by_id(game.id)
            await dp.bot.send_message(chat_id=telegram_group, text=await get_group_game_report())
            await dp.bot.send_message(chat_id=call.from_user.id, text=await get_group_game_report())


@dp.callback_query_handler(lambda c: c.data.startswith('debt_'))
async def debt_mark_us_paid(call: types.CallbackQuery):
    debt_id = int(call.data[5:])
    debt = session.query(Debt).filter(Debt.id == debt_id).scalar()
    mark_as_paid = update(Debt).where(Debt.id == debt_id).values(paid=True)
    session.execute(mark_as_paid)
    session.commit()
    session.close()
    await dp.bot.send_message(chat_id=await get_telegram_id_from_player_id(debt.creditor_id), text=answer['debt_marked_as_paid'].format(
        debt.game_id, debt.id, await get_username_from_player_id(debt.debtor_id), debt.amount),
                              reply_markup=await get_paid_button_confirmation(debt.id))


@dp.callback_query_handler(lambda c: c.data.endswith('_debt'))
async def debt_mark_us_paid(call: types.CallbackQuery):
    debt_id = int(call.data[:-5])
    debt = session.query(Debt).filter(Debt.id == debt_id).scalar()
    if call.message.reply_markup.inline_keyboard[0][0].text == 'YEAH':
        marked_as_paid = update(Debt).where(Debt.id == debt_id).values(paid_at=datetime.utcnow())
        session.execute(marked_as_paid)
        session.commit()
        session.close()
        await dp.bot.send_message(chat_id=await get_telegram_id_from_player_id(debt.creditor_id), text=answer['debt_complete'].format(
            debt.game_id, debt.id, await get_username_from_player_id(debt.creditor_id)))
        await call.answer()
    if call.message.reply_markup.inline_keyboard[0][1].text == 'NOPE':
        await dp.bot.send_message(chat_id=await get_telegram_id_from_player_id(debt.creditor_id), text=answer['debt_incomplete'].format(
            debt.game_id, debt.id, await get_username_from_player_id(debt.creditor_id)))
        await call.answer()
