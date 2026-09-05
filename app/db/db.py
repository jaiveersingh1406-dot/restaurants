import os

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres.knftpdrmnnhrhgxafkco:94143678%40Kk@aws-0-ap-south-1.pooler.supabase.com:6543/postgres",
)


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
    if not _DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is not set. Add your Supabase connection string to .env / Render env vars."
        )
    return _Connection(psycopg2.connect(_DATABASE_URL))


def connection():
    return get_connection()