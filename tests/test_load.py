import sqlite3

import pandas as pd
import pandas.errors
import pytest

from src import load
from src.load import (
    create_connection,
    create_schema,
    load_table,
    load_data,
)


SCHEMA_SQL = """
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    price REAL NOT NULL CHECK (price > 0)
);
"""


@pytest.fixture
def load_paths(tmp_path, monkeypatch):
    """Redireciona todos os caminhos do módulo load para um diretório temporário."""

    database_dir = tmp_path / "data" / "database"
    processed_dir = tmp_path / "data" / "processed"
    processed_dir.mkdir(parents=True)

    schema_path = tmp_path / "schema.sql"
    database_path = database_dir / "ecommerce.db"

    monkeypatch.setattr(load, "DATABASE_DIR", database_dir)
    monkeypatch.setattr(load, "DATABASE_PATH", database_path)
    monkeypatch.setattr(load, "SCHEMA_PATH", schema_path)
    monkeypatch.setattr(load, "PROCESSED_DIR", processed_dir)

    return {
        "database_dir": database_dir,
        "database_path": database_path,
        "schema_path": schema_path,
        "processed_dir": processed_dir,
    }



def test_create_connection_creates_database_directory(load_paths):

    assert not load_paths["database_dir"].exists()

    connection = create_connection()
    connection.close()

    assert load_paths["database_dir"].exists()


def test_create_connection_enables_foreign_keys(load_paths):

    connection = create_connection()

    result = connection.execute("PRAGMA foreign_keys").fetchone()[0]

    connection.close()

    assert result == 1



def test_create_schema_raises_when_schema_file_missing(load_paths):

    connection = sqlite3.connect(":memory:")

    with pytest.raises(FileNotFoundError):
        create_schema(connection)

    connection.close()


def test_create_schema_creates_expected_tables(load_paths):

    load_paths["schema_path"].write_text(SCHEMA_SQL, encoding="utf-8")

    connection = sqlite3.connect(":memory:")

    create_schema(connection)

    cursor = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
    )

    tables = {row[0] for row in cursor.fetchall()}

    connection.close()

    assert tables == {"customers", "products"}



def test_load_table_skips_empty_dataframe(load_paths):

    load_paths["schema_path"].write_text(SCHEMA_SQL, encoding="utf-8")

    connection = sqlite3.connect(":memory:")
    create_schema(connection)

    empty_df = pd.DataFrame(columns=["customer_id", "name"])

    load_table(connection, "customers", empty_df)

    count = connection.execute(
        "SELECT COUNT(*) FROM customers"
    ).fetchone()[0]

    connection.close()

    assert count == 0


def test_load_table_inserts_rows(load_paths):

    load_paths["schema_path"].write_text(SCHEMA_SQL, encoding="utf-8")

    connection = sqlite3.connect(":memory:")
    create_schema(connection)

    df = pd.DataFrame({
        "customer_id": [1, 2],
        "name": ["Cliente A", "Cliente B"],
    })

    load_table(connection, "customers", df)

    count = connection.execute(
        "SELECT COUNT(*) FROM customers"
    ).fetchone()[0]

    connection.close()

    assert count == 2



REAL_SCHEMA_SQL = (
    "CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL);\n"
    "CREATE TABLE products (product_id INTEGER PRIMARY KEY, price REAL NOT NULL CHECK (price > 0));\n"
    "CREATE TABLE sellers (seller_id INTEGER PRIMARY KEY, seller_name TEXT NOT NULL);\n"
    "CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL, "
    "seller_id INTEGER NOT NULL, total_amount REAL NOT NULL);\n"
    "CREATE TABLE order_items (order_item_id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL, "
    "product_id INTEGER NOT NULL, quantity INTEGER NOT NULL);\n"
    "CREATE TABLE payments (payment_id INTEGER PRIMARY KEY, order_id INTEGER NOT NULL, "
    "amount REAL NOT NULL CHECK (amount > 0));\n"
)


def _write_minimal_processed_csvs(processed_dir):

    pd.DataFrame({"customer_id": [1], "name": ["Cliente A"]}).to_csv(
        processed_dir / "customers_clean.csv", index=False
    )

    pd.DataFrame({"product_id": [1], "price": [10.0]}).to_csv(
        processed_dir / "products_clean.csv", index=False
    )

    pd.DataFrame({"seller_id": [1], "seller_name": ["Vendedor A"]}).to_csv(
        processed_dir / "sellers_clean.csv", index=False
    )

    pd.DataFrame({
        "order_id": [1],
        "customer_id": [1],
        "seller_id": [1],
        "total_amount": [100.0],
    }).to_csv(processed_dir / "orders_clean.csv", index=False)

    pd.DataFrame({
        "order_item_id": [1],
        "order_id": [1],
        "product_id": [1],
        "quantity": [2],
    }).to_csv(processed_dir / "order_items_clean.csv", index=False)

    pd.DataFrame({
        "payment_id": [1],
        "order_id": [1],
        "amount": [100.0],
    }).to_csv(processed_dir / "payments_clean.csv", index=False)


def test_load_data_loads_all_tables_successfully(load_paths):

    load_paths["schema_path"].write_text(REAL_SCHEMA_SQL, encoding="utf-8")
    _write_minimal_processed_csvs(load_paths["processed_dir"])

    load_data()

    connection = sqlite3.connect(load_paths["database_path"])

    for table in ["customers", "products", "sellers", "orders", "order_items", "payments"]:
        count = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        assert count == 1, f"{table} deveria ter 1 registro"

    connection.close()


def test_load_data_raises_when_processed_file_is_missing(load_paths):

    load_paths["schema_path"].write_text(REAL_SCHEMA_SQL, encoding="utf-8")
    _write_minimal_processed_csvs(load_paths["processed_dir"])

    (load_paths["processed_dir"] / "payments_clean.csv").unlink()

    with pytest.raises(FileNotFoundError):
        load_data()


def test_load_data_removes_previous_database_before_loading(load_paths):

    load_paths["schema_path"].write_text(REAL_SCHEMA_SQL, encoding="utf-8")
    _write_minimal_processed_csvs(load_paths["processed_dir"])

    load_data()
    first_mtime = load_paths["database_path"].stat().st_mtime_ns

    # Segunda carga deve recriar o banco do zero (sem erro de tabela já existente).
    load_data()
    second_mtime = load_paths["database_path"].stat().st_mtime_ns

    assert load_paths["database_path"].exists()
    assert second_mtime >= first_mtime


def test_load_data_rolls_back_on_constraint_violation(load_paths):

    load_paths["schema_path"].write_text(REAL_SCHEMA_SQL, encoding="utf-8")
    _write_minimal_processed_csvs(load_paths["processed_dir"])

    # Viola o CHECK (price > 0) de products, forçando falha durante a carga.
    pd.DataFrame({"product_id": [1], "price": [-10.0]}).to_csv(
        load_paths["processed_dir"] / "products_clean.csv", index=False
    )

    with pytest.raises(pandas.errors.DatabaseError):
        load_data()

    connection = sqlite3.connect(load_paths["database_path"])

    products_count = connection.execute(
        "SELECT COUNT(*) FROM products"
    ).fetchone()[0]

    connection.close()

    assert products_count == 0