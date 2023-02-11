# Module Imports
import sys

from botils.utils import CFG

import mariadb


class FinAnnouncerDB:
    def __init__(self):
        try:
            self.conn = mariadb.connect(
                user=CFG.db.user,
                password=CFG.db.password,
                host=CFG.db.host,
                port=CFG.db.get.port,
                database=CFG.db.database,
            )
            self.cursor = self.conn.cursor()
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(-1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def __enter__(self):
        return self

    def update_fins_for_user(self, user, fins):
        try:
            query = "UPDATE user_fields SET alarms = ? WHERE id = ?"
            self.cursor.execute(query, (";".join(fins), user))
            self.connection.commit()
        except mariadb.Error as e:
            print(f"Error: {e}")
