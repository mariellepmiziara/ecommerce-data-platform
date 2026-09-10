import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]
DATABASE_PATH = BASE_DIR / "data" / "database" / "ecommerce.db"


def list_tables() -> list[str]:
    connection = sqlite3.connect(DATABASE_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
        """)

        return [row[0] for row in cursor.fetchall()]

    finally:
        connection.close()


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    tables = list_tables()

    logger.info("TABELAS ENCONTRADAS: %s", tables)
