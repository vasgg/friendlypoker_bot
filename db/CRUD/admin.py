from sqlalchemy import update

from db.database import session
from db.models import Player


async def promote_to_admin(player_id: int) -> None:
    new_admin = update(Player).where(Player.id == player_id).values(is_admin=True)
    session.execute(new_admin)
    session.commit()
    session.close()


async def demote_from_admin(player_id: int) -> None:
    demote = update(Player).where(Player.id == player_id).values(is_admin=False)
    session.execute(demote)
    session.commit()
    session.close()
