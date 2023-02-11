import sys

from botils.utils import CFG, _get_module_logger
from db.ctx_manager import KFADBConnection

import mariadb

logger = _get_module_logger(__name__)


@KFADBConnection()
def update_or_create_fin(player, fin, ctx=None):
    try:
        query = "UPDATE user_fields SET alarms = ? WHERE id = ?"
        cur = ctx.connection.cursor()
        ctx.cursor.execute(query, (";".join(fin), player))
        ctx.connection.commit()
    except mariadb.Error as e:
        logger.error(f"Error querying database: {e}")
