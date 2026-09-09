import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = BASE_DIR / "data" / "database" / "ecommerce.db"


class DataValidationError(Exception):
    """Levantada quando a validação pós-carga encontra problemas de qualidade de dados."""


def validate_database():
    print("🔎 VALIDAÇÃO DO BANCO DE DADOS")
    print("=" * 60)

    connection = sqlite3.connect(DATABASE_PATH)

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

        print("\n📋 Tabelas encontradas:")

        for table in tables:
            print(f"   ✅ {table[0]}")

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

        print("\n📊 CONTAGEM DE REGISTROS")
        print("-" * 60)

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
                continue

            cursor.execute(
                f"SELECT COUNT(*) FROM {table}"
            )

            count = cursor.fetchone()[0]

            print(f"{table:<15} {count:>10,}")

            if count == 0:
                errors.append(f"{table}: tabela carregada com 0 registros")


        if missing_tables:

            print("\n⏭️  Demais checagens puladas: tabelas ausentes.")

        else:

            print("\n🔍 DUPLICIDADES")
            print("-" * 60)

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
                    print(f"✅ {name}: sem duplicidades")
                else:
                    print(f"❌ {name}: {duplicates} duplicidades")
                    errors.append(
                        f"{name}: {duplicates} registros com PK duplicada"
                    )

            print("\n🔗 INTEGRIDADE REFERENCIAL")
            print("-" * 60)

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
                    print(f"✅ {name}")
                else:
                    print(f"❌ {name}: {invalid} registros inválidos")
                    errors.append(
                        f"{name}: {invalid} registros órfãos (FK inválida)"
                    )

            print("\n🕳️ VALORES NULOS")
            print("-" * 60)

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
                    print(f"✅ {name}: sem nulos")
                else:
                    print(f"⚠️ {name}: {nulls} nulos")

                    if name not in allowed_nulls:
                        errors.append(
                            f"{name}: {nulls} nulos em coluna crítica "
                            "(não documentado como aceitável)"
                        )

        print("\n" + "=" * 60)

        if errors:
            print("❌ VALIDAÇÃO FALHOU")
            print("=" * 60)

            for error in errors:
                print(f"   - {error}")

            raise DataValidationError(
                f"{len(errors)} problema(s) de qualidade de dados "
                f"encontrado(s):\n" + "\n".join(f"- {e}" for e in errors)
            )

        print("🎉 VALIDAÇÃO CONCLUÍDA!")
        print("=" * 60)

    finally:
        connection.close()


if __name__ == "__main__":
    validate_database()
