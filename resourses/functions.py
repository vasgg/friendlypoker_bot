from db.database import session
from db.models import Game, Player


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


