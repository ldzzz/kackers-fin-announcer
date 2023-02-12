from botils.utils import CFG, _get_module_logger

import mariadb

logger = _get_module_logger(__name__)


class KFADBConnection(object):
    """Database Context Manager"""

    def __init__(self):
        self.connection = None
        self.cursor = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        err = False
        if exc_tb is None:
            self.connection.commit()
            logger.debug("Commited to database")
        else:
            err = True
            self.connection.rollback()
            logger.error(f"Couldn't commit to database: {exc_val}")
        self.cursor.close()
        self.connection.close()
        if err:
            raise ValueError("Rollback")

    def __enter__(self):
        self.connection = mariadb.connect(
            user=CFG.db.user,
            password=CFG.db.password,
            host=CFG.db.host,
            port=CFG.db.port,
            database=CFG.db.database,
        )
        self.cursor = self.connection.cursor()
        return self


def DBConnection(func):
    """Decorator function that wraps the function in context manager statement"""

    def wrapper(*args):
        try:
            with KFADBConnection() as ctx:
                func(*args, ctx)
        except ValueError:
            return False
        return True

    return wrapper
