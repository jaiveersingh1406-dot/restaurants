import os

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

_DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()


def _resolve_database_url():
    """Return the real Supabase connection string.

    Priority: DATABASE_URL env var (if it looks real), otherwise fall back to
    the bundled Supabase URL so the app works on Render even if the env var is
    empty or left as a '<Supabase...>' placeholder.
    """
    fallback = (
        "postgresql://postgres.knftpdrmnnhrhgxafkco:94143678%40Kk"
        "@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"
    )
    url = _DATABASE_URL
    if not url or url.startswith("<") or "your_" in url:
        return fallback
    return url


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
    url = _resolve_database_url()
    if not url:
        raise RuntimeError(
            "DATABASE_URL must contain a real Supabase PostgreSQL connection string. "
            "Set it in .env locally or in Render environment variables."
        )
    return _Connection(psycopg2.connect(url))


def connection():
    return get_connection()