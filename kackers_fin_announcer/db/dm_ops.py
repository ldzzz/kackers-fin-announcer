from botils.utils import CFG, _cleanup_fins, _get_module_logger
from db.ctx_manager import DBConnection, KFADBConnection

import mariadb

logger = _get_module_logger(__name__)


@DBConnection
def add_player(player: str, fins: dict, ctx=None):
    """Add player and their fetched finishes to database."""
    logger.debug(f"Add called: player={player}, ctx={ctx}")
    fincount = len(fins.keys())
    pquery = "INSERT IGNORE INTO player (username, fincount) VALUES (?, ?)"
    ctx.cursor.execute(pquery, (player, fincount))
    fquery = f"INSERT INTO mapfin (mapname, score, rank, date, player_id) VALUES (?, ?, ?, FROM_UNIXTIME(?), {ctx.cursor.lastrowid})"
    # bulk add all fins
    for mapname, mapdata in fins.items():
        to_insert = (mapname,) + tuple(mapdata.values())
        ctx.cursor.execute(fquery, to_insert)
    return True


@DBConnection
def remove_player(player: str, ctx=None):
    logger.debug(f"Remove called: player={player}, ctx={ctx}")
    query = "DELETE FROM player WHERE username=?"
    ctx.cursor.execute(query, (player,))


@DBConnection
def update_username(old: str, new: str, ctx=None):
    logger.debug(f"Update called: {old}->{new}, ctx={ctx}")
    query = "UPDATE player SET username=? WHERE username=?"
    ctx.cursor.execute(query, (new, old))
