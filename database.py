import sqlite3
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests

from config import DB_PATH

# Almaty: UTC+5 (so the time is correct on an internet server too)
ALMATY = timezone(timedelta(hours=5))

COLUMNS = [
    "id",
    "source",
    "tabs",
    "words_correct",
    "sleep_hours",
    "caffeine",
    "fatigue",
    "hour_of_day",
    "created_at",
]


def get_supabase_credentials():
    """Returns (url, key) if Supabase is configured in the Streamlit secrets."""
    try:
        import streamlit as st

        cfg = st.secrets["supabase"]
        return cfg["url"], cfg["key"]
    except Exception:
        return None


class SupabaseStore:
    """Stores the answers in a Supabase table through its web (REST) interface."""

    PAGE_SIZE = 1000

    def __init__(self, url, key):
        self.endpoint = url.rstrip("/") + "/rest/v1/responses"
        self.headers = {
            "apikey": key,
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }

    def insert(self, row):
        response = requests.post(
            self.endpoint, json=row, headers=self.headers, timeout=15
        )
        response.raise_for_status()

    def select(self, source=None):
        rows, offset = [], 0
        while True:
            params = {
                "select": "*",
                "order": "id.asc",
                "limit": self.PAGE_SIZE,
                "offset": offset,
            }
            if source is not None:
                params["source"] = f"eq.{source}"
            response = requests.get(
                self.endpoint, params=params, headers=self.headers, timeout=15
            )
            response.raise_for_status()
            page = response.json()
            rows.extend(page)
            if len(page) < self.PAGE_SIZE:
                return rows
            offset += self.PAGE_SIZE


class Database:
    """Saves and reads the answers.

    If Supabase is configured in the secrets, the answers go to the cloud.
    Otherwise they are saved in a local SQLite file (data.db).
    """

    def __init__(self, path=DB_PATH):
        self.path = path
        credentials = get_supabase_credentials()
        self.remote = SupabaseStore(*credentials) if credentials else None
        if self.remote is None:
            self.create_table()

    # ---------- local SQLite ----------
    def connect(self):
        return sqlite3.connect(self.path)

    def create_table(self):
        """Creates the local table if it does not exist yet."""
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

    # ---------- public methods ----------
    def add_response(
        self,
        tabs,
        words_correct,
        source="site",
        sleep_hours=None,
        caffeine=None,
        fatigue=None,
    ):
        """Saves one response.

        source: "site" (website test) or "survey" (survey from the report).
        caffeine: 1 (yes) or 0 (no). Empty fields are stored as NULL.
        The hour of the day is recorded automatically, only for website responses.
        """
        now = datetime.now(ALMATY)
        row = {
            "source": source,
            "tabs": tabs,
            "words_correct": words_correct,
            "sleep_hours": sleep_hours,
            "caffeine": caffeine,
            "fatigue": fatigue,
            "hour_of_day": now.hour if source == "site" else None,
            "created_at": now.isoformat(timespec="seconds"),
        }

        if self.remote is not None:
            self.remote.insert(row)
            return

        conn = self.connect()
        conn.execute(
            """
            INSERT INTO responses
            (source, tabs, words_correct, sleep_hours, caffeine, fatigue,
             hour_of_day, created_at)
            VALUES (:source, :tabs, :words_correct, :sleep_hours, :caffeine,
                    :fatigue, :hour_of_day, :created_at)
            """,
            row,
        )
        conn.commit()
        conn.close()

    def get_all(self, source=None):
        """Returns the responses as a pandas table (optionally one source only)."""
        if self.remote is not None:
            return pd.DataFrame(self.remote.select(source), columns=COLUMNS)

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
        """How many responses were collected (in total or for one source)."""
        if self.remote is not None:
            return len(self.remote.select(source))

        conn = self.connect()
        if source is None:
            result = conn.execute("SELECT COUNT(*) FROM responses").fetchone()[0]
        else:
            result = conn.execute(
                "SELECT COUNT(*) FROM responses WHERE source = ?", (source,)
            ).fetchone()[0]
        conn.close()
        return result