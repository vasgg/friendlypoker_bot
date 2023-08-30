from collections import namedtuple
from datetime import datetime

import arrow
import humanize as humanize
from sqlalchemy import func, update

from db.CRUD.player import get_player_from_id
from db.database import session
from db.models import Game, Record
from resourses.replies import answer


async def get_current_game():
    current_game = session.query(Game).filter(Game.finish_time == None).scalar()
    if current_game:
        return current_game


async def get_last_game():
    last_game = session.query(Game).filter(Game.finish_time != None).order_by(Game.id.desc()).first()
    return last_game


async def get_current_game_stats_for_admin() -> str:
    game: Game = await get_current_game()
    start = arrow.get(game.start_time)
    started = start.humanize()
    total_pot_query = session.query(func.sum(Record.buy_in)).filter(Record.game_id == game.id)
    total_pot = total_pot_query.scalar()
    current_game_stats_for_admin = answer['current_game_stats_admin_reply'].format(
        game.id,
        started,
        total_pot,
        game.admin,
    )
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
        game_stats_for_player = answer['exited_game_stats_player_reply'].format(
            game_id,
            humanize.precisedelta(duration, minimum_unit='minutes', format='%0.2d'),
            buy_in,
            buy_out,
            net_profit,
            ROI,
        )
    return game_stats_for_player


async def get_group_game_report() -> str:
    game: Game = await get_last_game()
    duration = arrow.get(game.start_time) - arrow.get(game.finish_time)
    MVP = await get_player_from_id(game.MVP)
    text = answer['global_game_report'].format(
        game.id,
        humanize.precisedelta(duration, minimum_unit='minutes', format='%0.2d'),
        game.total_pot,
        MVP.username,
    )
    return text


async def get_remaining_players_in_game() -> list:
    game: Game = await get_current_game()
    try:
        remaining_players = session.query(Record).filter(
            Record.game_id == game.id, Record.buy_out == None
        )
        remaining_players_ids = []
        if remaining_players:
            for player in remaining_players:
                remaining_players_ids.append(player.id)
        return remaining_players_ids
    except AttributeError:
        pass


async def check_game_balance(game_id: int) -> namedtuple:
    try:
        total_pot = session.query(func.sum(Record.buy_in).filter(Record.game_id == game_id)).scalar()
        total_buy_outs = session.query(func.sum(Record.buy_out).filter(Record.game_id == game_id)).scalar()
        delta = total_pot - total_buy_outs
        Results = namedtuple('Results', ['total_pot', 'delta'])
        results = Results(total_pot, delta)
        return results
    except AttributeError:
        pass


async def exiting_game_by_player(telegram_id: int, buy_out: int):
    game: Game = await get_current_game()
    buy_in_query = session.query(Record.buy_in).filter(
        Record.game_id == game.id, Record.player_telegram_id == telegram_id
    )
    buy_in = buy_in_query.scalar()
    net_profit = buy_out - buy_in
    ROI = round((net_profit / buy_in) * 100)
    record = (
        update(Record)
        .where(Record.game_id == int(game.id), Record.player_telegram_id == telegram_id)
        .values(
            buy_out=buy_out, net_profit=net_profit, ROI=ROI, exited_at=datetime.utcnow()
        )
    )
    session.execute(record)
    session.commit()
    session.close()


async def commit_game_results_to_db(game_id: int, total_pot: int, MVP: int):
    close_game = update(Game).where(Game.id == game_id).values(
        finish_time=datetime.utcnow(),
        total_pot=total_pot,
        MVP=MVP,
    )
    session.execute(close_game)
    session.commit()
    session.close()
