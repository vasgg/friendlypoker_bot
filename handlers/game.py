from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from sqlalchemy import update

from config import dp, redis, telegram_group, logger
from db.CRUD.debt import (
    commit_debts_to_db,
    debt_calculator,
    debt_informer_by_id)
from db.CRUD.game import (check_game_balance, commit_game_results_to_db, exiting_game_by_player, get_current_game,
                          get_current_game_stats_for_player, get_group_game_report, get_remaining_players_in_game)
from db.CRUD.player import (add_thousand, get_list_of_id_and_names, get_list_of_players_and_buy_ins, get_mvp, get_player_from_id,
                            get_players)
from db.database import session
from db.models import Debt, Game, Player, Record
from resourses.keyboards import (
    add_funds_keyboard,
    add_keyboard,
    get_paid_button_confirmation,
)
from resourses.replies import answer
from resourses.states import States


@dp.message_handler(Command('game'))
async def game_command(message: types.Message):
    game = await get_current_game()
    if not game:
        await dp.bot.send_message(
            chat_id=message.from_user.id, text=answer['game_menu_new_game']
        )
    else:
        text = await get_current_game_stats_for_player(message.from_user.id, game.id)
        await dp.bot.send_message(
            chat_id=message.from_user.id, text=text, reply_markup=add_funds_keyboard
        )


@dp.callback_query_handler(text='self add 1000')
async def adding_funds_by_player(call: types.CallbackQuery):
    game = await get_current_game()
    await add_thousand(call.from_user.id, game.id)
    caption = answer['start_game_report'].format(game.id)
    stats = await get_list_of_players_and_buy_ins(game.id)
    text = caption + stats
    group_message_id = redis.get('group_message_id')
    personal_message_id = redis.get(f'personal_message_id{call.from_user.id}')
    try:
        await dp.bot.edit_message_text(
            chat_id=telegram_group,
            text=text,
            message_id=group_message_id,
            reply_markup=add_keyboard,
        )
    except Exception as e:
        logger.debug(
            answer['value_error_log'], call.from_user.full_name, e, call.id
        )
    add_funds_report = answer['add_funds_report'].format(game.id)
    text = add_funds_report + stats
    await dp.bot.edit_message_text(
        chat_id=call.from_user.id, text=text, message_id=personal_message_id
    )
    await dp.bot.send_message(chat_id=call.from_user.id, text=add_funds_report)
    await call.answer()


@dp.callback_query_handler(text='new game')
async def game_starter(call: types.CallbackQuery):
    await States.missing_playsers.set()
    text = await get_list_of_id_and_names('all') + '\n' + answer['players_reply']
    await dp.bot.send_message(chat_id=call.from_user.id, text=text)
    await call.answer()


@dp.message_handler(state=States.missing_playsers)
async def missing_players_input(message: types.Message, state: FSMContext):
    missing_players = [int(num) for num in str(message.text).strip().split()]
    if 0 in missing_players:
        attending_players = await get_players()
    else:
        attending_players = await get_players(exluded=missing_players)
    admin = session.query(Player.id).where(Player.telegram_id == message.from_user.id)
    game = Game(admin=admin)
    session.add(game)
    session.commit()
    game = await get_current_game()
    caption = answer['start_game_report'].format(game.id)
    text = await get_list_of_players_and_buy_ins(game.id)
    for player in attending_players:
        record = Record(
            player_id=player.id,
            player_telegram_id=player.telegram_id,
            game_id=game.id,
            buy_in=1000,
        )
        session.add(record)
        personal_message = await dp.bot.send_message(chat_id=player.telegram_id, text=caption + text, reply_markup=add_keyboard)
        redis.set(f'personal_message_id{player.telegram_id}', personal_message.message_id)
    session.commit()
    session.close()
    group_message = await dp.bot.send_message(chat_id=telegram_group, text=caption + text, reply_markup=add_keyboard)
    redis.set('group_message_id', group_message.message_id)
    await state.reset_state()


@dp.callback_query_handler(text='exit game')
async def quit_game(call: types.CallbackQuery):
    await dp.bot.send_message(chat_id=call.from_user.id, text=answer['exit_game_by_player_reply'])
    await States.enter_remaining_balance.set()
    await call.answer()


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
        results = await check_game_balance(game.id)
        if results.delta != 0:
            await dp.bot.send_message(chat_id=call.from_user.id, text=answer['exit_game_wrong_total_sum'].format(results.delta))
        else:
            transactions = await debt_calculator(game.id)
            MVP = await get_mvp(game.id)
            await commit_game_results_to_db(game.id, results.total_pot, MVP)
            text = await get_group_game_report()
            await commit_debts_to_db(transactions)
            await debt_informer_by_id(game.id)
            await dp.bot.send_message(chat_id=telegram_group, text=text)
            await dp.bot.send_message(chat_id=call.from_user.id, text=text)
    await call.answer()


@dp.callback_query_handler(lambda c: c.data.startswith('debt_'))
async def debt_mark_us_paid(call: types.CallbackQuery):
    debt_id = int(call.data[5:])
    debt = session.query(Debt).filter(Debt.id == debt_id).scalar()
    mark_as_paid = update(Debt).where(Debt.id == debt_id).values(paid=True)
    session.execute(mark_as_paid)
    session.commit()
    session.close()
    creditor = await get_player_from_id(debt.creditor_id)
    debtor = await get_player_from_id(debt.debtor_id)
    paid_message = await dp.bot.send_message(
        chat_id=creditor.telegram_id,
        text=answer['debt_marked_as_paid'].format(debt.game_id, debt.id, '@' + debtor.username, debt.amount / 100),
        reply_markup=await get_paid_button_confirmation(debt.id),
    )
    redis.set(f'debt{debt_id}_paid_message_id', paid_message.message_id)
    # redis.set(f'debt{debt_id}_paid_message_id', paid_message.chat.id)
    redis.set(f'debt{debt_id}_paid_message_chat_id', paid_message.chat.id)
    # redis.set(f'debt{debt_id}_paid_message_chat_id', creditor.telegram_id)
    await call.answer()


@dp.callback_query_handler(lambda c: c.data.endswith('_yeah_debt'))
async def coplete_debt(call: types.CallbackQuery):
    debt_id = int(call.data[:-10])
    debt = session.query(Debt).filter(Debt.id == debt_id).scalar()
    marked_as_paid = update(Debt).where(Debt.id == debt_id).values(paid=True, paid_at=datetime.utcnow())
    session.execute(marked_as_paid)
    session.commit()
    session.close()
    creditor = await get_player_from_id(debt.creditor_id)
    debtor = await get_player_from_id(debt.debtor_id)
    await dp.bot.send_message(
        chat_id=debtor.telegram_id,
        text=answer['debt_complete'].format(debt.game_id, debt.id, '@' + creditor.username),
        reply_markup=None,
    )
    paid_message_id = redis.get(f'debt{debt_id}_paid_message_id')
    paid_message_chat_id = redis.get(f'debt{debt_id}_paid_message_chat_id')
    await dp.bot.delete_message(chat_id=paid_message_chat_id, message_id=paid_message_id)
    await call.answer()


@dp.callback_query_handler(lambda c: c.data.endswith('_nope_debt'))
async def incoplete_debt(call: types.CallbackQuery):
    debt_id = int(call.data[:-10])
    debt = session.query(Debt).filter(Debt.id == debt_id).scalar()
    mark_as_unpaid = update(Debt).where(Debt.id == debt_id).values(paid=False, paid_at=None)
    session.execute(mark_as_unpaid)
    session.commit()
    session.close()
    creditor = await get_player_from_id(debt.creditor_id)
    debtor = await get_player_from_id(debt.debtor_id)
    await dp.bot.send_message(
        chat_id=debtor.telegram_id,
        text=answer['debt_incomplete'].format(debt.game_id, debt.id, '@' + creditor.telegram_id),
        reply_markup=None,
    )
    await call.answer()
