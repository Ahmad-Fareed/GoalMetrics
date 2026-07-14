"""Database connection pool management with context-manager support."""

import logging
from contextlib import contextmanager

import mysql.connector
from mysql.connector import pooling, Error

logger = logging.getLogger(__name__)

# Module-level pool reference, initialised once at app startup
_pool: pooling.MySQLConnectionPool | None = None


def init_db_pool(app):
    """Create a MySQL connection pool using Flask app config values."""
    global _pool
    try:
        _pool = pooling.MySQLConnectionPool(
            pool_name="goal_metrics_pool",
            pool_size=5,
            pool_reset_session=True,
            host=app.config["DB_HOST"],
            user=app.config["DB_USER"],
            password=app.config["DB_PASSWORD"],
            database=app.config["DB_NAME"],
        )
        logger.info("MySQL connection pool initialised successfully.")
    except Error as exc:
        logger.critical("Failed to initialise MySQL pool: %s", exc)


def get_db_connection():
    """Return a raw connection from the pool (caller must close it)."""
    if _pool is None:
        raise RuntimeError("Database pool has not been initialised.")
    try:
        return _pool.get_connection()
    except Error as exc:
        logger.error("Could not obtain database connection: %s", exc)
        return None


@contextmanager
def get_db():
    """Context manager that yields *(connection, cursor)* and guarantees cleanup.

    Usage::

        with get_db() as (conn, cursor):
            cursor.execute("SELECT ...")
            rows = cursor.fetchall()
    """
    conn = get_db_connection()
    if conn is None:
        raise RuntimeError("Database connection could not be established.")
    cursor = conn.cursor(dictionary=True)
    try:
        yield conn, cursor
    finally:
        cursor.close()
        conn.close()