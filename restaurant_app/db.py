"""PostgreSQL connection pool and small database helpers."""

from contextlib import contextmanager

from psycopg2.pool import SimpleConnectionPool

from restaurant_app.config import get_database_settings

_pool = None


def get_pool():
    """Create the pool once, then reuse it."""
    global _pool
    if _pool is None:
        _pool = SimpleConnectionPool(
            minconn=1,
            maxconn=5,
            **get_database_settings(),
        )
    return _pool


@contextmanager
def get_connection():
    """Return a connection to the pool even if a query fails."""
    pool = get_pool()
    connection = pool.getconn()
    try:
        yield connection
    finally:
        pool.putconn(connection)


def close_pool():
    """Close all pooled connections when the application exits."""
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None
