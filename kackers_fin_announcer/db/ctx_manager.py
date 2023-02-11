from contextlib import ContextDecorator

from botils.utils import CFG

import mariadb


class KFADBConnection(ContextDecorator):
    """Database Context Manager"""

    def __init__(self):
        self.connection = None
        self.cursor = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb is None:
            self.connection.commit()
        else:
            self.connection.rollback()
        self.cursor.close()
        self.connection.close()

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

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            with self as ctx:
                func(*args, ctx)

        return wrapper
