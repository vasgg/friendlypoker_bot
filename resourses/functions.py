from sqlalchemy import func

from db.database import session
from db.models import Game, Player, Record
from resourses.replies import answer
import arrow


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


async def get_current_game_stats() -> str:
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
    current_game_stats = answer['current_game_stats_reply'].format(game.id, table_size, started, total_pot, game.admin,
                                                                   total_games_by_admin, game.host, total_games_by_host)
    return current_game_stats
