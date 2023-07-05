from collections import namedtuple
from datetime import datetime

import arrow
import humanize as humanize
from sqlalchemy import func, update

from db.database import session
from db.models import Game, Player, Record
from resourses.replies import answer


async def get_current_game():
    current_game = session.query(Game).filter(Game.finish_time == None).scalar()
    if current_game:
        return current_game
    else:
        return 0


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
    for i in all_players:
        player = i[0]
        player_str = f'{player.id}. {player.fullname}\n'
        all_players_reply += player_str
    return all_players_reply


async def get_current_game_stats_for_admin() -> str:
    game: Game = await get_current_game()
    all_players = session.query(Record).filter(Record.game_id == game.id)
    table_size = all_players.count()
    start = arrow.get(game.start_time, 'Asia/Tbilisi')
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


async def get_current_game_stats_for_player(telegram_id: int) -> str:
    game: Game = await get_current_game()
    record: Record = session.query(Record).filter(Record.game_id == game.id, Record.player_telegram_id == telegram_id).scalar()
    player_id = record.player_id
    start = arrow.get(game.start_time, 'Asia/Karachi')
    started = start.humanize()

    total_pot = session.query(func.sum(Record.buy_in)).filter(Record.game_id == game.id).scalar()
    buy_in = record.buy_in
    buy_out = record.buy_out
    if not buy_out:
        game_stats_for_player = answer['current_game_stats_player_reply'].format(game.id, player_id, started, buy_in, total_pot)
    else:
        net_profit = record.net_profit
        # ROI = record.ROI
        finish = arrow.get(record.exited_at, 'Asia/Tbilisi')
        duration = finish - start
        game_stats_for_player = answer['exited_game_stats_player_reply'].format(game.id, humanize.naturaldelta(duration), buy_in, buy_out,
                                                                                net_profit)

    return game_stats_for_player


async def add_thousand(telegram_id: int):
    game: Game = await get_current_game()
    buy_in_query = session.query(Record.buy_in).filter(Record.game_id == game.id, Record.player_telegram_id == telegram_id)
    buy_in = buy_in_query.scalar()

    add_1000 = update(Record).where(Record.game_id == int(game.id), Record.player_telegram_id == telegram_id).values(
        buy_in=int(buy_in) + 1000)
    session.execute(add_1000)
    session.commit()
    session.close()


async def get_remaining_players_in_game() -> list:
    game: Game = await get_current_game()
    remaining_players = session.query(Record).filter(Record.game_id == game.id, Record.buy_out == None)
    remaining_players_ids = []
    if remaining_players:
        for player in remaining_players:
            remaining_players_ids.append(player.id)
    return remaining_players_ids


async def check_balance_after_game() -> namedtuple:
    game: Game = await get_current_game()
    total_pot = session.query(func.sum(Record.buy_in).filter(Record.game_id == game.id)).scalar()
    total_buy_outs = session.query(func.sum(Record.buy_out).filter(Record.game_id == game.id)).scalar()
    delta = total_pot - total_buy_outs
    Results = namedtuple('Results', ['total_pot', 'delta'])
    results = Results(total_pot, delta)
    return results


async def get_king_of_kush(game_id: int):
    king_of_kush_id = session.query(Record.id).filter(Record.game_id == game_id).order_by(Record.net_profit.desc()).first()
    return king_of_kush_id[0]


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


async def commit_game_results_to_db(game_id: int, total_pot: int, king_id: int):
    close_game = update(Game).where(Game.id == game_id).values(finish_time=datetime.utcnow(),
                                                               total_pot=total_pot,
                                                               king_of_kush=king_id)
    session.execute(close_game)
    session.commit()
    session.close()


async def equalizer(debtors, creditors):
    # if len(debtors) == 0 or len(creditors) == 0:
    #     return 1
    # for i in debtors:
    #     val = abs(i[1])
    #     for j in creditors:
    #         if val == j[1]:
    #             text = f'{i[0]} otdaet {j[0]} {val} deneg'
    #             print('==============================', text)
    #             del j
    #             del i
    #             if len(debtors) or len(creditors) != 0:
    #
    #                 return await equalizer(debtors, creditors)
    # # print(creditors, debtors)
    b = sorted(debtors, key=lambda x: x[1])
    a = sorted(creditors, key=lambda x: x[1], reverse=True)
    print('creditors = ', a, '\ndebtors', b)

    if len(b) == 0 or len(a) == 0:
        return 1
    else:
        if abs(b[0][1]) == a[0][1]:
            del a[0]
            del b[0]

            return await equalizer(b, a)
        elif abs(b[0][1]) < a[0][1]:
            text = f'{b[0][0]} otdaet {a[0][0]} {abs(b[0][1])} deneg'
            print(text)

            a[0][1] = a[0][1] - abs(b[0][1])
            del b[0]

            return await equalizer(b, a)
        elif abs(b[0][1]) > a[0][1]:
            text = f'{b[0][0]} otdaet {a[0][0]} {a[0][1]} deneg'
            print(text)
            b[0][1] = b[0][1] + a[0][1]
            del a[0]
            return await equalizer(b, a)


async def debt_counter(game_id: int):
    records = session.query(Record).filter(Record.game_id == game_id).all()
    creditors = []
    debtors = []
    transactions = []
    for record in records:

        player = [record.player_id, record.net_profit]
        if record.net_profit > 0:
            creditors.append(player)
        else:
            debtors.append(player)

    full_dolg = sum(item[1] for item in debtors)
    print(creditors, '\n', debtors)
    print('full dolg', full_dolg)
    await equalizer(debtors, creditors)
