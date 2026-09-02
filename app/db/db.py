import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv()

_DEFAULT_HOST = os.environ.get("DB_HOST", "localhost")
_DEFAULT_USER = os.environ.get("DB_USER", "root")
_DEFAULT_PASSWORD = os.environ.get("DB_PASSWORD", "root1234")
_DEFAULT_NAME = os.environ.get("DB_NAME", "restaurant")


def get_connection():
    return mysql.connector.connect(
        host=_DEFAULT_HOST,
        user=_DEFAULT_USER,
        password=_DEFAULT_PASSWORD,
        database=_DEFAULT_NAME,
    )


def connection():
    return get_connection()