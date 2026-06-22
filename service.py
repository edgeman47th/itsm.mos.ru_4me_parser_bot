import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name='/app/db/items.db'):  # Указываем путь к директории с базой данных
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()


    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS subscribers (
                                user_id INTEGER PRIMARY KEY
                              )''')
        self.conn.commit()

    def add_subscriber(self, user_id):
        self.cursor.execute('INSERT OR IGNORE INTO subscribers (user_id) VALUES (?)', (user_id,))
        self.conn.commit()

    def remove_subscriber(self, user_id):
        self.cursor.execute('DELETE FROM subscribers WHERE user_id=?', (user_id,))
        self.conn.commit()

    def get_subscribers(self):
        self.cursor.execute('SELECT user_id FROM subscribers')
        return [row[0] for row in self.cursor.fetchall()]
