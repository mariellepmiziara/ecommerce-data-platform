import logging
import sqlite3
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]
DATABASE_PATH = BASE_DIR / "data" / "database" / "ecommerce.db"
EXPORT_DIR = BASE_DIR / "data" / "exports" / "powerbi"


EXPORT_QUERIES = {
    "customers": "SELECT * FROM customers",
    "products": "SELECT * FROM products",
    "sellers": "SELECT * FROM sellers",
    "order_items": "SELECT * FROM order_items",
    "payments": "SELECT * FROM payments",
    "orders": """
        SELECT
            o.order_id,
            o.customer_id,
            o.seller_id,
            o.order_date,
            o.status,
            o.payment_method,
            o.total_amount AS total_amount_raw_not_trusted,
            COALESCE(SUM(oi.net_amount), 0) AS order_total_amount_trusted
        FROM orders o
        LEFT JOIN order_items oi ON oi.order_id = o.order_id
        GROUP BY
            o.order_id, o.customer_id, o.seller_id,
            o.order_date, o.status, o.payment_method, o.total_amount
    """,
}


def export_for_powerbi() -> None:

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Banco não encontrado em {DATABASE_PATH}. "
            "Rode `python main.py` (ou `python src/load.py`) antes de exportar."
        )

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)

    try:
        logger.info("📤 Exportando tabelas para o Power BI em %s", EXPORT_DIR)

        for table_name, query in EXPORT_QUERIES.items():

            df = pd.read_sql_query(query, connection)

            output_path = EXPORT_DIR / f"{table_name}.csv"

            df.to_csv(output_path, index=False, encoding="utf-8")

            logger.info(
                "✅ %s: %s registros → %s",
                table_name,
                f"{len(df):,}",
                output_path.name,
            )

        logger.info("🎉 Exportação concluída.")

    finally:
        connection.close()


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    export_for_powerbi()