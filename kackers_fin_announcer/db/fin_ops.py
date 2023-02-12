from botils.utils import _get_module_logger
from db.ctx_manager import DBConnection

logger = _get_module_logger(__name__)


@DBConnection
def get_all_players(ctx=None) -> dict:
    """Gets all (username, id) from database"""
    query = "SELECT username, id FROM players"
    ctx.cursor.execute(query)
    players = dict()
    for username, id in ctx.cursor:
        players[username] = id
    return players


@DBConnection
def get_player_fins(player: str, ctx=None):
    """Get all players' fins in database"""
    query = "SELECT mapfins.mapname, mapfins.score, mapfins.rank, UNIX_TIMESTAMP(mapfins.date), mapfins.delta FROM mapfins INNER JOIN players ON mapfins.player_id=players.id WHERE players.username=?"
    ctx.cursor.execute(query, (player,))
    fins = {}
    for mapname, score, rank, date, delta in ctx.cursor:
        fins[mapname] = {
            "score": score,
            "kacky_rank": rank,
            "date": date,
            "delta": delta,
        }
    return fins


@DBConnection
def update_fins(player_id: int, fins: list, ctx=None):
    """Bulk update finishes in database (PB)"""
    if fins:
        query = f"UPDATE mapfins SET delta = ?, date = FROM_UNIXTIME(?), rank = ?, score = ? WHERE mapname=? AND player_id= {player_id}"
        ctx.cursor.executemany(query, fins)


@DBConnection
def create_fins(player_id: str, fins: list, ctx=None):
    """Bulk create finishes in database (new)"""
    # create new fins
    if fins:
        fquery = f"INSERT INTO mapfins (mapname, score, rank, date, player_id)  VALUES (?, ?, ?, FROM_UNIXTIME(?), {player_id})"
        ctx.cursor.executemany(fquery, fins)
        # update fincount
        pquery = f"UPDATE players SET fincount=fincount + ? WHERE id = ?"
        ctx.cursor.execute(pquery, (len(fins), player_id))
