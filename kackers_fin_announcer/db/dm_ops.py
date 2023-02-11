import sys

from botils.utils import CFG, _get_module_logger
from db.ctx_manager import KFADBConnection

logger = _get_module_logger(__name__)


@KFADBConnection()
def add_player(player, ctx=None):
    # TODO: fetch player fins to also insert
    fincount = 0
    logger.debug(f"Add called: player={player}, ctx={ctx}")
    """
    try:
        query = " INSERT IGNORE INTO player (username, fincount) VALUES (?, ?)"
        ctx.cursor.execute(query, (player, fincount))
        ctx.connnection.commit()
    except mariadb.Error as e:
        print(f"Error: {e}")
    """


@KFADBConnection()
def update_player(player, ctx=None):
    # TODO: fetch player fins to also insert
    fincount = 0
    logger.debug(f"Update called: player={player}, ctx={ctx}")
    """
    try:
        query = " INSERT IGNORE INTO player (username, fincount) VALUES (?, ?)"
        ctx.cursor.execute(query, (player, fincount))
        ctx.connnection.commit()
    except mariadb.Error as e:
        print(f"Error: {e}")
    """
