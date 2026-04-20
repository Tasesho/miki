# Working on It
import sqlite3

class DBManager:
    def __init__(self, db_path="miki_data.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute ("""
                CREATE TABLE IF NOT EXIST users (
                user_id TEXT PRIMARY KEY,
                city TEXT
            )
        """)

    def set_user_city(self, user_id, city):
        with self.conn:
            self.conn.execute("INSERT OR REPLACE INTO users (user_id, city) VALUES (?, ?)", (user_id, city))

## TODOESTO ES PARA QUE CREE UNA TABLA CON INFORMACION DE CADA USUARIO Y GUARDA SU CIUDAD PARA FUTUROS USOS.