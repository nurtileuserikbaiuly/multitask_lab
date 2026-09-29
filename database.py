import sqlite3
from datetime import datetime

import pandas as pd

from config import DB_PATH


class Database:
    """Работа с базой данных: сохраняем и читаем ответы студентов."""

    def __init__(self, path=DB_PATH):
        self.path = path
        self.create_table()

    def connect(self):
        return sqlite3.connect(self.path)

    def create_table(self):
        """Создаёт таблицу, если её ещё нет."""
        conn = self.connect()
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tabs INTEGER NOT NULL,
                words_correct INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
        conn.close()

    def add_response(self, tabs, words_correct):
        """Сохраняет один ответ: число вкладок и число верных слов."""
        conn = self.connect()
        conn.execute(
            "INSERT INTO responses (tabs, words_correct, created_at) VALUES (?, ?, ?)",
            (tabs, words_correct, datetime.now().isoformat(timespec="seconds")),
        )
        conn.commit()
        conn.close()

    def get_all(self):
        """Возвращает все ответы в виде таблицы pandas."""
        conn = self.connect()
        df = pd.read_sql("SELECT * FROM responses", conn)
        conn.close()
        return df

    def count(self):
        """Сколько ответов уже собрано."""
        conn = self.connect()
        result = conn.execute("SELECT COUNT(*) FROM responses").fetchone()[0]
        conn.close()
        return result