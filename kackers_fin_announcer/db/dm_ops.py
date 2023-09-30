from botils.utils import CFG, _fins2tuple, _get_module_logger
from db.ctx_manager import DBConnection

logger = _get_module_logger(__name__)


@DBConnection
def add_player(player: str, fins: dict, ctx=None):
    """Add player and their fetched finishes to database."""
    fins = _fins2tuple(fins)
    pquery = "INSERT IGNORE INTO players (username, fincount) VALUES (?, ?)"
    ctx.cursor.execute(pquery, (player, len(fins)))
    fquery = f"INSERT INTO mapfins (mapname, date, rank, score, player_id) VALUES (?, FROM_UNIXTIME(?), ?, ?, {ctx.cursor.lastrowid})"
    ctx.cursor.executemany(fquery, fins)


@DBConnection
def remove_player(player: str, ctx=None):
    """Remove player & their finishes from database."""
    query = "DELETE FROM players WHERE username=?"
    ctx.cursor.execute(query, (player,))


@DBConnection
def get_all_players(ctx=None) -> list:
    """Gets all (username, fincount) from database"""
    query = "SELECT username, fincount FROM players"
    ctx.cursor.execute(query)
    players = ctx.cursor.fetchall()
    return players
