from botils.utils import CFG, _fins2updatecreate, _get_module_logger
from db.ctx_manager import DBConnection

logger = _get_module_logger(__name__)


@DBConnection
def get_all_players(ctx=None) -> list:
    """Gets all (username, id) from database as a list of dicts."""
    query = "SELECT username, id FROM players"
    ctx.cursor.execute(query)
    players = ctx.cursor.fetchall()
    return players

@DBConnection
def update_or_create_finishes(player_id: int, fins: dict, ctx=None) -> None:
    """Update or create finishes for the player named, also updates players' finish count."""
    # update finishes
    #fins = _fins2updatecreate(fins, player_id)
    fins = [(666,1676404567.0, 74, 10000, 1, 1677404567.0, 6666,1677404567.0, 70, 6666, 20, 1677404567.0)] # TODO: dummy for testing, DELETE
    query = ("INSERT INTO mapfins(mapname, date, rank, score, player_id) VALUES(?, FROM_UNIXTIME(?), ?, ?, ?) "
            "ON DUPLICATE KEY UPDATE score_delta=IF(FROM_UNIXTIME(?) > date, score-?, score_delta),"
            "rank_delta=IF(FROM_UNIXTIME(?) > date,?-CAST(rank AS SIGNED), rank_delta), score=?, rank=?, date=FROM_UNIXTIME(?);")
    ctx.cursor.executemany(query, fins)
    # update fincount
    pquery = "UPDATE players SET fincount=(SELECT COUNT(*) FROM mapfins WHERE player_id=?) WHERE id=?"
    ctx.cursor.execute(pquery, (player_id, player_id))

@DBConnection
def get_latest_finishes(player_id: int, ctx=None) -> list:
    """Return a list of latest players finishes based off of CFG.interval."""
    query = "SELECT * FROM mapfins WHERE player_id=? AND updated_at>=FROM_UNIXTIME(UNIX_TIMESTAMP() - ?);"
    ctx.cursor.execute(query, (player_id, CFG.interval))
    finishes = ctx.cursor.fetchall()
    return finishes

@DBConnection
def get_player_finish_count(player_id: int, ctx=None) -> int:
    """Return current finish count of a given player."""
    query = "SELECT fincount FROM players WHERE id=?"
    ctx.cursor.execute(query, (player_id,))
    fincount = ctx.cursor.fetchone()["fincount"]
    return fincount
