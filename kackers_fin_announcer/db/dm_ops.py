from botils.utils import CFG, _get_module_logger
from db.ctx_manager import DBConnection

logger = _get_module_logger(__name__)


@DBConnection
def add_player(player: str, fins: list, ctx=None):
    """Add player and their fetched finishes to database."""
    fincount = len(fins)
    pquery = "INSERT IGNORE INTO players (username, fincount) VALUES (?, ?)"
    ctx.cursor.execute(pquery, (player, fincount))
    fquery = f"INSERT INTO mapfins (mapname, score, rank, date, player_id) VALUES (?, ?, ?, FROM_UNIXTIME(?), {ctx.cursor.lastrowid})"
    # bulk add all fins
    ctx.cursor.executemany(fquery, fins)


@DBConnection
def remove_player(player: str, ctx=None):
    """Remove player & their finishes from database."""
    query = "DELETE FROM players WHERE username=?"
    ctx.cursor.execute(query, (player,))


@DBConnection
def update_username(old: str, new: str, ctx=None):
    """Update player username in database."""
    query = "UPDATE players SET username=? WHERE username=?"
    ctx.cursor.execute(query, (new, old))
