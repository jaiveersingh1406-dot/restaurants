import os

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

_DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()


class _Connection:
    """Thin wrapper so existing code can keep using
    connection.cursor(dictionary=True) the same way it did with MySQL."""

    def __init__(self, conn):
        self._conn = conn

    def cursor(self, dictionary=False):
        if dictionary:
            return self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return self._conn.cursor()

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()


def get_connection():
    if not _DATABASE_URL or _DATABASE_URL == "your_supabase_database_url":
        raise RuntimeError(
            "DATABASE_URL must contain a real Supabase PostgreSQL connection string. "
            "Set it in .env locally or in Render environment variables."
        )
    return _Connection(psycopg2.connect(_DATABASE_URL))


def connection():
    return get_connection()