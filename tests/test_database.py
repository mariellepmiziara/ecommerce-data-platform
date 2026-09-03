import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DATABASE_PATH = BASE_DIR / "data" / "database" / "ecommerce.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


# ============================================================
# TESTES BÁSICOS DO BANCO
# ============================================================

def test_database_exists():

    assert DATABASE_PATH.exists(), (
        f"Banco de dados não encontrado: {DATABASE_PATH}"
    )


def test_expected_tables_exist():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
    """)

    tables = {row[0] for row in cursor.fetchall()}

    connection.close()

    expected_tables = {
        "customers",
        "products",
        "sellers",
        "orders",
        "order_items",
        "payments",
    }

    assert expected_tables.issubset(tables)


def test_expected_record_counts():

    connection = get_connection()

    expected_counts = {
        "customers": 1000,
        "products": 198,
        "orders": 9997,
        "order_items": 24734,
        "payments": 9996,
    }

    for table, expected_count in expected_counts.items():

        cursor = connection.execute(
            f"SELECT COUNT(*) FROM {table}"
        )

        actual_count = cursor.fetchone()[0]

        assert actual_count == expected_count, (
            f"{table}: esperado {expected_count}, "
            f"encontrado {actual_count}"
        )

    connection.close()


# ============================================================
# TESTE DE PRIMARY KEYS
# ============================================================

def test_primary_keys_exist():

    connection = get_connection()

    tables_and_columns = {
        "customers": "customer_id",
        "products": "product_id",
        "sellers": "seller_id",
        "orders": "order_id",
        "order_items": "order_item_id",
        "payments": "payment_id",
    }

    for table, column in tables_and_columns.items():

        cursor = connection.execute(
            f"PRAGMA table_info({table})"
        )

        columns = cursor.fetchall()

        primary_key_columns = {
            row[1]
            for row in columns
            if row[5] == 1
        }

        assert column in primary_key_columns, (
            f"{table}.{column} não está definido como PRIMARY KEY"
        )

    connection.close()


# ============================================================
# TESTE DE FOREIGN KEYS
# ============================================================

def test_foreign_keys_enabled():

    connection = get_connection()

    result = connection.execute(
        "PRAGMA foreign_keys"
    ).fetchone()[0]

    connection.close()

    assert result == 1


def test_orders_foreign_keys():

    connection = get_connection()

    foreign_keys = connection.execute(
        "PRAGMA foreign_key_list(orders)"
    ).fetchall()

    connection.close()

    references = {
        (row[3], row[2], row[4])
        for row in foreign_keys
    }

    assert (
        "customer_id",
        "customers",
        "customer_id"
    ) in references

    assert (
        "seller_id",
        "sellers",
        "seller_id"
    ) in references


def test_order_items_foreign_keys():

    connection = get_connection()

    foreign_keys = connection.execute(
        "PRAGMA foreign_key_list(order_items)"
    ).fetchall()

    connection.close()

    references = {
        (row[3], row[2], row[4])
        for row in foreign_keys
    }

    assert (
        "order_id",
        "orders",
        "order_id"
    ) in references

    assert (
        "product_id",
        "products",
        "product_id"
    ) in references


def test_payments_foreign_key():

    connection = get_connection()

    foreign_keys = connection.execute(
        "PRAGMA foreign_key_list(payments)"
    ).fetchall()

    connection.close()

    references = {
        (row[3], row[2], row[4])
        for row in foreign_keys
    }

    assert (
        "order_id",
        "orders",
        "order_id"
    ) in references