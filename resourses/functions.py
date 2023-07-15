from collections import namedtuple
from datetime import datetime

import arrow
import humanize as humanize
from sqlalchemy import func, update

from config import dp
from db.database import session
from db.models import Debt, Game, Player, Record
from resourses.keyboards import get_paid_button
from resourses.replies import answer


async def get_current_game():
    current_game = session.query(Game).filter(Game.finish_time == None).scalar()
    if current_game:
        return current_game


async def get_last_game():
    last_game = session.query(Game).filter(Game.finish_time != None).order_by(Game.id.desc()).first()
    return last_game


async def get_players(exluded: list[int] = None) -> list[Player]:
    all_players_query = session.query(Player)
    all_players = session.execute(all_players_query).fetchall()
    filtered_players = []
    for i in all_players:
        player = i[0]
        if not exluded or player.id not in exluded:
            filtered_players.append(player)
    return filtered_players


async def get_list_of_id_and_names() -> str:
    all_players_query = session.query(Player)
    all_players = session.execute(all_players_query).fetchall()
    all_players_reply = ''
    for i in sorted(all_players):
        player = i[0]
        player_str = f'{player.id}. {player.fullname}\n'
        all_players_reply += player_str
    return all_players_reply


async def get_list_of_players_and_buy_ins(game_id: int) -> str:
    all_records = session.query(Record).filter(Record.game_id == game_id)
    result = ''
    summ = 0
    for record in sorted(all_records, reverse=True):
        name = str(await get_fullname_from_player_id(record.player_id))
        newname = name.ljust(18)
        score = record.buy_in

        formatted_string = "{}: {}\n".format(newname, score)
        summ += record.buy_in
        result += formatted_string
    last_string = 'TOTAL POT '.rjust(18)
    res = '<code>' + result + f'{last_string}: {summ} </code>'
    return res


async def get_telegram_id_from_player_id(player_id: int) -> int:
    telegram_id = session.query(Player.telegram_id).filter(Player.id == player_id).scalar()
    return telegram_id


async def get_username_from_player_id(player_id: int) -> str:
    username = session.query(Player.username).filter(Player.id == player_id).scalar()
    return "@" + username


async def get_fullname_from_player_id(player_id: int) -> str:
    fullname = session.query(Player.fullname).filter(Player.id == player_id).scalar()
    return fullname


async def get_current_game_stats_for_admin() -> str:
    game: Game = await get_current_game()
    all_players = session.query(Record).filter(Record.game_id == game.id)
    table_size = all_players.count()
    start = arrow.get(game.start_time)
    started = start.humanize()
    total_pot_query = session.query(func.sum(Record.buy_in)).filter(Record.game_id == game.id)
    total_pot = total_pot_query.scalar()
    total_games_by_admin_query = session.query(Game).filter(Game.admin == game.admin)
    total_games_by_admin = total_games_by_admin_query.count()
    total_games_by_host_query = session.query(Game).filter(Game.host == game.host)
    total_games_by_host = total_games_by_host_query.count()
    current_game_stats_for_admin = answer['current_game_stats_admin_reply'].format(game.id, table_size, started, total_pot, game.admin,
                                                                                   total_games_by_admin, game.host, total_games_by_host)
    return current_game_stats_for_admin


async def get_current_game_stats_for_player(telegram_id: int, game_id: int) -> str:
    record: Record = session.query(Record).filter(Record.game_id == game_id, Record.player_telegram_id == telegram_id).scalar()
    start = arrow.get(record.connected_at)
    started = start.humanize()

    total_pot = session.query(func.sum(Record.buy_in)).filter(Record.game_id == game_id).scalar()
    buy_in = record.buy_in
    buy_out = record.buy_out
    if not buy_out:
        game_stats_for_player = answer['current_game_stats_player_reply'].format(game_id, record.player_id, started, buy_in, total_pot)
    else:
        net_profit = record.net_profit
        ROI = record.ROI
        finish = arrow.get(record.exited_at)
        duration = finish - start
        game_stats_for_player = answer['exited_game_stats_player_reply'].format(game_id, humanize.precisedelta(
            duration, minimum_unit='minutes', format='%0.2d'), buy_in, buy_out, net_profit, ROI)
    return game_stats_for_player


async def get_group_game_report() -> str:
    game: Game = await get_last_game()
    duration = arrow.get(game.start_time) - arrow.get(game.finish_time)
    text = answer['global_game_report'].format(game.id, humanize.precisedelta(duration, minimum_unit='minutes', format='%0.2d'),
                                               game.table_size,
                                               game.total_pot,
                                               await get_username_from_player_id(game.host), await get_username_from_player_id(game.MVP))
    return text


async def add_thousand(telegram_id: int, game_id: int):
    buy_in_query = session.query(Record.buy_in).filter(Record.game_id == game_id, Record.player_telegram_id == telegram_id)
    buy_in = buy_in_query.scalar()
    add_1000 = update(Record).where(Record.game_id == game_id, Record.player_telegram_id == telegram_id).values(
        buy_in=int(buy_in) + 1000)
    session.execute(add_1000)
    session.commit()
    session.close()


async def get_remaining_players_in_game() -> list:
    game: Game = await get_current_game()
    try:
        remaining_players = session.query(Record).filter(Record.game_id == game.id, Record.buy_out == None)
        remaining_players_ids = []
        if remaining_players:
            for player in remaining_players:
                remaining_players_ids.append(player.id)
        return remaining_players_ids
    except AttributeError:
        pass


async def check_balance_after_game() -> namedtuple:
    game: Game = await get_current_game()
    try:
        total_pot = session.query(func.sum(Record.buy_in).filter(Record.game_id == game.id)).scalar()
        total_buy_outs = session.query(func.sum(Record.buy_out).filter(Record.game_id == game.id)).scalar()
        delta = total_pot - total_buy_outs
        Results = namedtuple('Results', ['total_pot', 'delta'])
        results = Results(total_pot, delta)
        return results
    except AttributeError:
        pass


async def get_mvp(game_id: int):
    MVP = session.query(Record.player_id).filter(Record.game_id == game_id).order_by(Record.net_profit.desc()).first()
    return MVP[0]


async def get_admin_telegram_id(game_id: int):
    admin_telegram_id = session.query(Record.player_telegram_id).filter(Record.game_id == game_id).first()
    return admin_telegram_id[0]


async def exiting_game_by_player(telegram_id: int, buy_out: int):
    game: Game = await get_current_game()
    buy_in_query = session.query(Record.buy_in).filter(Record.game_id == game.id, Record.player_telegram_id == telegram_id)
    buy_in = buy_in_query.scalar()
    net_profit = buy_out - buy_in
    ROI = round((net_profit / buy_in) * 100)
    record = update(Record).where(Record.game_id == int(game.id), Record.player_telegram_id == telegram_id).values(
        buy_out=buy_out, net_profit=net_profit, ROI=ROI, exited_at=datetime.utcnow())
    session.execute(record)
    session.commit()
    session.close()


async def commit_game_results_to_db(game_id: int, total_pot: int, MVP: int):
    table_size_query = session.query(Record).filter(Record.game_id == game_id)
    table_size = table_size_query.count()
    close_game = update(Game).where(Game.id == game_id).values(finish_time=datetime.utcnow(),
                                                               total_pot=total_pot,
                                                               table_size=table_size,
                                                               MVP=MVP)
    session.execute(close_game)
    session.commit()
    session.close()


async def equalizer(debtors: list, creditors: list, game_id: int, transactions=[]) -> list[Debt]:
    for debtor in debtors:
        for creditor in creditors:
            if abs(debtor[1]) == creditor[1]:
                debt = Debt(game_id=game_id,
                            creditor_id=creditor[0],
                            debtor_id=debtor[0],
                            amount=creditor[1])
                transactions.append(debt)
                debtors.remove(debtor)
                creditors.remove(creditor)
                return await equalizer(debtors, creditors, game_id)

    sorted_creditors = sorted(creditors, key=lambda x: x[1], reverse=True)
    sorted_debtors = sorted(debtors, key=lambda x: x[1])

    while sorted_debtors:
        if abs(sorted_debtors[0][1]) < sorted_creditors[0][1]:
            debt = Debt(game_id=game_id,
                        creditor_id=sorted_creditors[0][0],
                        debtor_id=sorted_debtors[0][0],
                        amount=abs(sorted_debtors[0][1]))
            transactions.append(debt)
            sorted_creditors[0][1] = sorted_creditors[0][1] - abs(sorted_debtors[0][1])
            del sorted_debtors[0]
            return await equalizer(sorted_debtors, sorted_creditors, game_id)
        else:
            debt = Debt(game_id=game_id,
                        creditor_id=sorted_creditors[0][0],
                        debtor_id=sorted_debtors[0][0],
                        amount=sorted_creditors[0][1])
            transactions.append(debt)
            sorted_debtors[0][1] = sorted_debtors[0][1] + sorted_creditors[0][1]
            del sorted_creditors[0]
            return await equalizer(sorted_debtors, sorted_creditors, game_id)
    return transactions


async def debt_calculator(game_id: int) -> list[Debt]:
    records = session.query(Record).filter(Record.game_id == game_id).all()
    creditors = [[record.player_id, record.net_profit] for record in records if record.net_profit > 0]
    debtors = [[record.player_id, record.net_profit] for record in records if record.net_profit < 0]
    transactions = await equalizer(debtors, creditors, game_id)
    return transactions


async def commit_debts_to_db(transactions: list[Debt]) -> None:
    for transaction in transactions:
        session.add(transaction)
    session.commit()
    session.close()


async def debt_informer_by_id(game_id: int) -> None:
    debts = session.query(Debt).filter(Debt.game_id == game_id).all()
    for debt in debts:
        debtor_telegram_id = await get_telegram_id_from_player_id(debt.debtor_id)
        creditor_telegram_id = await get_telegram_id_from_player_id(debt.creditor_id)
        debtor_username = await get_username_from_player_id(debt.debtor_id)
        creditor_username = await get_username_from_player_id(debt.creditor_id)
        await dp.bot.send_message(chat_id=debtor_telegram_id,
                                  text=answer['debtor_personal_game_report'].format(
                                      debt.game_id, debt.id, debt.amount / 100, creditor_username),
                                  reply_markup=await get_paid_button(debt.id))
        await dp.bot.send_message(chat_id=creditor_telegram_id,
                                  text=answer['creditor_personal_game_report'].format(
                                      debt.game_id, debt.id, debtor_username, debt.amount / 100))
