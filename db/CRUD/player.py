from typing import Literal

from sqlalchemy import update

from db.database import session
from db.models import Player, Record


async def get_players(exluded: list[int] = None) -> list[Player]:
    all_players_query = session.query(Player)
    all_players = session.execute(all_players_query).fetchall()
    filtered_players = []
    for i in all_players:
        player = i[0]
        if not exluded or player.id not in exluded:
            filtered_players.append(player)
    return filtered_players


async def get_list_of_id_and_names(mode: Literal['all', 'admins', 'non-admins']) -> str:
    query = None
    players_reply = ''
    match mode:
        case 'all':
            query = session.query(Player)
        case 'admins':
            query = session.query(Player).filter(Player.is_admin, Player.id != 1)
        case 'non-admins':
            query = session.query(Player).filter(~Player.is_admin)
    players = session.execute(query).all()
    for player in sorted(players):
        players_reply += f'{player[0].id}. {player[0].fullname}\n'
    return players_reply


async def get_list_of_players_and_buy_ins(game_id: int) -> str:
    all_records = session.query(Record).filter(Record.game_id == game_id)
    result = ''
    summ = 0
    for record in sorted(all_records, reverse=True):
        player = await get_player_from_id(record.player_id)
        name = player.fullname
        newname = name.ljust(18)[:18]
        score = record.buy_in

        formatted_string = '{}: {}\n'.format(newname, score)
        summ += record.buy_in
        result += formatted_string
    last_string = 'TOTAL POT '.rjust(18)
    res = '<code>' + result + f'{last_string}: {summ} </code>'
    return res


async def get_player_from_id(player_id: int) -> Player:
    player = session.query(Player).filter(Player.id == player_id).scalar()
    return player


async def get_mvp(game_id: int):
    MVP = session.query(Record.player_id).filter(Record.game_id == game_id).order_by(Record.net_profit.desc()).first()
    return MVP[0]


async def add_thousand(telegram_id: int, game_id: int):
    record = session.query(Record).filter(Record.game_id == game_id, Record.player_telegram_id == telegram_id).scalar()
    add_1000 = (update(Record)
                .where(Record.game_id == game_id, Record.player_telegram_id == telegram_id)
                .values(buy_in=int(record.buy_in) + 1000))
    session.execute(add_1000)
    session.commit()
    session.close()


async def add_players(added_players: list) -> None:
    pass

