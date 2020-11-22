"""Database singleton"""
# pylint: disable=global-statement
import sqlite3

# PATH = '/run/statx-ajax/.db'
PATH = '.statx-ajax.db'

_DB_CONN: sqlite3.Connection = None


def get_conn() -> sqlite3.Connection:
    """Get Database connection"""
    global _DB_CONN

    if _DB_CONN:
        return _DB_CONN

    try:
        # connect
        connection = sqlite3.connect(PATH)
    except Exception as exc:
        raise ValueError('Database not initialized') from exc

    connection.row_factory = sqlite3.Row

    # set global and return
    _DB_CONN = connection
    return connection
