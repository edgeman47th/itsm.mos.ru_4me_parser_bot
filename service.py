import sqlite3
import os

class Database:
    def __init__(self, db_path='./db/items.db'):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                user_id INTEGER PRIMARY KEY
            )
        ''')
        self.conn.commit()

    def add_subscriber(self, user_id):
        self.conn.execute('INSERT OR IGNORE INTO subscribers (user_id) VALUES (?)', (user_id,))
        self.conn.commit()

    def remove_subscriber(self, user_id):
        self.conn.execute('DELETE FROM subscribers WHERE user_id = ?', (user_id,))
        self.conn.commit()

    def get_subscribers(self):
        cursor = self.conn.execute('SELECT user_id FROM subscribers')
        return [row[0] for row in cursor.fetchall()]