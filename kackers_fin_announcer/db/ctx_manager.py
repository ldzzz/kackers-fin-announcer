from botils.utils import CFG, _get_module_logger

import mariadb

logger = _get_module_logger(__name__)


class KFADBConnection(object):
    """Database Context Manager"""

    def __init__(self):
        self.connection = None
        self.cursor = None

    def __exit__(self, exc_type, exc_val, exc_tb):
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
        ret = True
        try:
            with KFADBConnection() as ctx:
                func(*args, ctx)
                print("Yes function finished")
            print("do i get here????")
        except ValueError:
            print("before fals")
            return False
            # ret = False
        print("but do i get here ???????")
        return True
        # finally:
        #    print("in fiunally")
        #    return ret

    return wrapper
