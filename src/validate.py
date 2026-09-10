import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = BASE_DIR / "data" / "database" / "ecommerce.db"


class DataValidationError(Exception):
    """Levantada quando a validação pós-carga encontra problemas de qualidade de dados."""


def validate_database():
    logger.info("🔎 VALIDAÇÃO DO BANCO DE DADOS")

    connection = sqlite3.connect(DATABASE_PATH)

    # Acumula mensagens de erro; ao final, se houver alguma, a função falha.
    errors: list[str] = []

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name;
        """)

        tables = cursor.fetchall()
        found_table_names = {table[0] for table in tables}

        logger.info("📋 Tabelas encontradas: %s", sorted(found_table_names))

        expected_tables = {
            "customers",
            "products",
            "sellers",
            "orders",
            "order_items",
            "payments",
        }

        missing_tables = expected_tables - found_table_names

        if missing_tables:
            errors.append(
                f"Tabelas ausentes no banco: {sorted(missing_tables)}"
            )

        logger.info("📊 CONTAGEM DE REGISTROS")

        table_names = [
            "customers",
            "products",
            "sellers",
            "orders",
            "payments",
            "order_items",
        ]

        for table in table_names:

            if table not in found_table_names:
                # Já reportado acima como tabela ausente; evita erro no COUNT(*).
                continue

            cursor.execute(
                f"SELECT COUNT(*) FROM {table}"
            )

            count = cursor.fetchone()[0]

            logger.info("%-15s %10s", table, f"{count:,}")

            if count == 0:
                errors.append(f"{table}: tabela carregada com 0 registros")

        # As checagens abaixo (duplicidades, integridade referencial, nulos)
        # fazem SELECTs diretos nas tabelas esperadas. Se alguma tabela
        # estiver ausente, pular essas seções evita um OperationalError
        # não tratado — o problema já foi registrado em `errors` acima.
        if missing_tables:

            logger.warning("⏭️  Demais checagens puladas: tabelas ausentes.")

        else:

            logger.info("🔍 DUPLICIDADES")

            validations = [

                (
                    "customers.customer_id",
                    """
                    SELECT COUNT(*) - COUNT(DISTINCT customer_id)
                    FROM customers
                    """
                ),

                (
                    "products.product_id",
                    """
                    SELECT COUNT(*) - COUNT(DISTINCT product_id)
                    FROM products
                    """
                ),

                (
                    "sellers.seller_id",
                    """
                    SELECT COUNT(*) - COUNT(DISTINCT seller_id)
                    FROM sellers
                    """
                ),

                (
                    "orders.order_id",
                    """
                    SELECT COUNT(*) - COUNT(DISTINCT order_id)
                    FROM orders
                    """
                ),

                (
                    "orders_items.order_item_id",
                    """
                    SELECT COUNT(*) - COUNT(DISTINCT order_item_id)
                    FROM order_items
                    """
                ),

                (
                    "payments.payment_id",
                    """
                    SELECT COUNT(*) - COUNT(DISTINCT payment_id)
                    FROM payments
                    """
                )
            ]

            for name, query in validations:
                cursor.execute(query)
                duplicates = cursor.fetchone()[0]

                if duplicates == 0:
                    logger.info("✅ %s: sem duplicidades", name)
                else:
                    logger.warning("❌ %s: %s duplicidades", name, duplicates)
                    errors.append(
                        f"{name}: {duplicates} registros com PK duplicada"
                    )

            logger.info("🔗 INTEGRIDADE REFERENCIAL")

            referential_checks = [

                (
                    "orders → customers",
                    """
                    SELECT COUNT(*)
                    FROM orders o
                    LEFT JOIN customers c
                        ON o.customer_id = c.customer_id
                    WHERE c.customer_id IS NULL;
                    """
                ),

                (
                    "orders → sellers",
                    """
                    SELECT COUNT(*)
                    FROM orders o
                    LEFT JOIN sellers s
                        ON o.seller_id = s.seller_id
                    WHERE s.seller_id IS NULL;
                    """
                ),

                (
                    "order_items → orders",
                    """
                    SELECT COUNT(*)
                    FROM order_items oi
                    LEFT JOIN orders o
                        ON oi.order_id = o.order_id
                    WHERE o.order_id IS NULL;
                    """
                ),

                (
                    "order_items → products",
                    """
                    SELECT COUNT(*)
                    FROM order_items oi
                    LEFT JOIN products p
                        ON oi.product_id = p.product_id
                    WHERE p.product_id IS NULL
                    """
                ),

                (
                    "payments → orders",
                    """
                    SELECT COUNT(*)
                    FROM payments p
                    LEFT JOIN orders o
                        ON p.order_id = o.order_id
                    WHERE o.order_id IS NULL;
                    """
                ),
            ]

            for name, query in referential_checks:
                cursor.execute(query)
                invalid = cursor.fetchone()[0]

                if invalid == 0:
                    logger.info("✅ %s", name)
                else:
                    logger.warning(
                        "❌ %s: %s registros inválidos", name, invalid
                    )
                    errors.append(
                        f"{name}: {invalid} registros órfãos (FK inválida)"
                    )

            logger.info("🕳️ VALORES NULOS")

            # Colunas onde nulo é uma condição documentada e aceitável
            # (ver README: "Documented Business Decisions").
            allowed_nulls = {"customers.email"}

            null_checks = {

                "customers.email": """
                    SELECT COUNT(*)
                    FROM customers
                    WHERE email IS NULL
                 """,

                "orders.customer_id": """
                    SELECT COUNT(*)
                    FROM orders
                    WHERE customer_id IS NULL
                """,

                "order.total_amount": """
                    SELECT COUNT(*)
                    FROM orders
                    WHERE total_amount IS NULL
                """,

                "order_items.quantity": """
                    SELECT COUNT(*)
                    FROM order_items
                    WHERE quantity IS NULL
                """
            }

            for name, query in null_checks.items():
                cursor.execute(query)
                nulls = cursor.fetchone()[0]

                if nulls == 0:
                    logger.info("✅ %s: sem nulos", name)
                else:
                    logger.warning("⚠️ %s: %s nulos", name, nulls)

                    if name not in allowed_nulls:
                        errors.append(
                            f"{name}: {nulls} nulos em coluna crítica "
                            "(não documentado como aceitável)"
                        )

        if errors:
            logger.error("❌ VALIDAÇÃO FALHOU")

            for error in errors:
                logger.error("   - %s", error)

            raise DataValidationError(
                f"{len(errors)} problema(s) de qualidade de dados "
                f"encontrado(s):\n" + "\n".join(f"- {e}" for e in errors)
            )

        logger.info("🎉 VALIDAÇÃO CONCLUÍDA!")

    finally:
        connection.close()


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    validate_database()

    # 3 registros de customers sem e-mail — mantidos intencionalmente
    # o email foi normalizado, porém não descartou clientes sem email cadastrado