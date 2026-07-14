"""
Data pipeline — creates the MySQL schema and bulk-inserts CSV data.

Reads database credentials from environment variables with sensible defaults
so the same script works locally and in CI.
"""

import csv
import logging
import os

import mysql.connector
from mysql.connector import Error

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger(__name__)

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "root"),
    "database": os.environ.get("DB_NAME", "goalmetric_db"),
}

BATCH_SIZE = 5000


# ---------------------------------------------------------------------------
# Schema setup
# ---------------------------------------------------------------------------

def setup_database():
    """Connect to MySQL, create the database and the *matches* table."""
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
        )
        cursor = connection.cursor()

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id           INT AUTO_INCREMENT PRIMARY KEY,
                match_date   DATE         NOT NULL,
                home_team    VARCHAR(100) NOT NULL,
                away_team    VARCHAR(100) NOT NULL,
                home_score   INT          NOT NULL,
                away_score   INT          NOT NULL,
                tournament   VARCHAR(150),
                city         VARCHAR(100),
                country      VARCHAR(100),
                neutral_venue BOOLEAN,
                INDEX idx_home_team (home_team),
                INDEX idx_away_team (away_team),
                UNIQUE KEY unique_match (match_date, home_team, away_team)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        logger.info("Database '%s' and 'matches' table verified.", DB_CONFIG["database"])
        return connection, cursor

    except Error as exc:
        logger.critical("Database setup failed: %s", exc)
        return None, None


def setup_goalscorers_table(connection, cursor):
    """Create the *goalscorers* table with composite unique constraints."""
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goalscorers (
                id           INT AUTO_INCREMENT PRIMARY KEY,
                match_date   DATE         NOT NULL,
                home_team    VARCHAR(100) NOT NULL,
                away_team    VARCHAR(100) NOT NULL,
                scoring_team VARCHAR(100) NOT NULL,
                scorer       VARCHAR(100) NOT NULL,
                minute       INT,
                own_goal     BOOLEAN,
                penalty      BOOLEAN,
                INDEX idx_scorer       (scorer),
                INDEX idx_scoring_team (scoring_team),
                UNIQUE KEY unique_goal (match_date, home_team, away_team, scorer, minute)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        logger.info("'goalscorers' table verified/created.")
    except Error as exc:
        logger.critical("Goalscorers table setup failed: %s", exc)


# ---------------------------------------------------------------------------
# CSV ingestion
# ---------------------------------------------------------------------------

def _resolve_path(filename: str) -> str:
    """Return the absolute path to *filename* relative to this script."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)


def ingest_csv_data(connection, cursor, csv_filename: str):
    """Bulk-insert *results.csv* into the *matches* table."""
    filepath = _resolve_path(csv_filename)
    if not os.path.exists(filepath):
        logger.error("Dataset missing: %s", filepath)
        return

    insert_query = """
        INSERT IGNORE INTO matches
            (match_date, home_team, away_team, home_score, away_score,
             tournament, city, country, neutral_venue)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    batch, total = [], 0
    logger.info("Ingesting match data from %s …", csv_filename)

    try:
        with open(filepath, mode="r", encoding="utf-8", errors="replace") as fh:
            for row in csv.DictReader(fh):
                if not row["home_score"] or not row["away_score"]:
                    continue

                neutral = 1 if row.get("neutral", "False").strip().lower() == "true" else 0
                batch.append((
                    row["date"],
                    row["home_team"].strip(),
                    row["away_team"].strip(),
                    int(row["home_score"]),
                    int(row["away_score"]),
                    row["tournament"].strip(),
                    row["city"].strip(),
                    row["country"].strip(),
                    neutral,
                ))

                if len(batch) == BATCH_SIZE:
                    cursor.executemany(insert_query, batch)
                    connection.commit()
                    total += len(batch)
                    logger.info("  … %d matches imported", total)
                    batch.clear()

            if batch:
                cursor.executemany(insert_query, batch)
                connection.commit()
                total += len(batch)

        logger.info("Match ingestion complete — %d rows.", total)

    except Error as exc:
        logger.error("Match ingestion aborted (SQL): %s", exc)
        connection.rollback()
    except Exception as exc:
        logger.error("Match ingestion aborted: %s", exc)


def ingest_goalscorers_data(connection, cursor, csv_filename: str):
    """Bulk-insert *goalscorers.csv* into the *goalscorers* table."""
    filepath = _resolve_path(csv_filename)
    if not os.path.exists(filepath):
        logger.error("Dataset missing: %s", filepath)
        return

    insert_query = """
        INSERT IGNORE INTO goalscorers
            (match_date, home_team, away_team, scoring_team, scorer,
             minute, own_goal, penalty)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    batch, total = [], 0
    logger.info("Ingesting goalscorer data from %s …", csv_filename)

    try:
        with open(filepath, mode="r", encoding="utf-8", errors="replace") as fh:
            for row in csv.DictReader(fh):
                minute_val = int(row["minute"]) if row.get("minute", "").isdigit() else None
                own = 1 if row.get("own_goal", "").strip().lower() == "true" else 0
                pen = 1 if row.get("penalty", "").strip().lower() == "true" else 0

                batch.append((
                    row["date"],
                    row["home_team"].strip(),
                    row["away_team"].strip(),
                    row["team"].strip(),
                    row["scorer"].strip(),
                    minute_val,
                    own,
                    pen,
                ))

                if len(batch) == BATCH_SIZE:
                    cursor.executemany(insert_query, batch)
                    connection.commit()
                    total += len(batch)
                    batch.clear()

            if batch:
                cursor.executemany(insert_query, batch)
                connection.commit()
                total += len(batch)

        logger.info("Goalscorer ingestion complete — %d rows.", total)

    except Error as exc:
        logger.error("Goalscorer ingestion aborted (SQL): %s", exc)
        connection.rollback()


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    conn, curs = setup_database()

    if conn and curs:
        ingest_csv_data(conn, curs, "results.csv")
        setup_goalscorers_table(conn, curs)
        ingest_goalscorers_data(conn, curs, "goalscorers.csv")

        curs.close()
        conn.close()
        logger.info("Pipeline finished — connections closed.")
