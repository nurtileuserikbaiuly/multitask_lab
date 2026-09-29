import sqlite3
from datetime import datetime, timedelta, timezone

import pandas as pd

from config import DB_PATH

# Алматы: UTC+5 (так время будет верным и на сервере в интернете)
ALMATY = timezone(timedelta(hours=5))


class Database:
    """Работа с базой данных: сохраняем и читаем ответы."""

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
                source TEXT NOT NULL,
                tabs REAL NOT NULL,
                words_correct INTEGER NOT NULL,
                sleep_hours REAL,
                caffeine INTEGER,
                fatigue INTEGER,
                hour_of_day INTEGER,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
        conn.close()

    def add_response(
        self,
        tabs,
        words_correct,
        source="site",
        sleep_hours=None,
        caffeine=None,
        fatigue=None,
    ):
        """Сохраняет один ответ.

        source: "site" (тест на сайте) или "survey" (опрос из отчёта).
        caffeine: 1 (да) или 0 (нет). Пустые поля хранятся как NULL.
        Время суток записывается само, только для ответов с сайта.
        """
        now = datetime.now(ALMATY)
        hour = now.hour if source == "site" else None

        conn = self.connect()
        conn.execute(
            """
            INSERT INTO responses
            (source, tabs, words_correct, sleep_hours, caffeine, fatigue,
             hour_of_day, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source,
                tabs,
                words_correct,
                sleep_hours,
                caffeine,
                fatigue,
                hour,
                now.isoformat(timespec="seconds"),
            ),
        )
        conn.commit()
        conn.close()

    def get_all(self, source=None):
        """Возвращает ответы в виде таблицы pandas (можно только один источник)."""
        conn = self.connect()
        if source is None:
            df = pd.read_sql("SELECT * FROM responses", conn)
        else:
            df = pd.read_sql(
                "SELECT * FROM responses WHERE source = ?", conn, params=(source,)
            )
        conn.close()
        return df

    def count(self, source=None):
        """Сколько ответов собрано (всего или по источнику)."""
        conn = self.connect()
        if source is None:
            result = conn.execute("SELECT COUNT(*) FROM responses").fetchone()[0]
        else:
            result = conn.execute(
                "SELECT COUNT(*) FROM responses WHERE source = ?", (source,)
            ).fetchone()[0]
        conn.close()
        return result