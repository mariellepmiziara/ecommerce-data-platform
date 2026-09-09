import sqlite3

import pytest

from src import validate
from src.validate import validate_database, DataValidationError



VALID_SCHEMA_SQL = """
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    city TEXT,
    state TEXT,
    created_at TEXT
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL CHECK (price > 0),
    cost REAL NOT NULL CHECK (cost > 0),
    stock INTEGER NOT NULL CHECK (stock >= 0)
);

CREATE TABLE sellers (
    seller_id INTEGER PRIMARY KEY,
    seller_name TEXT NOT NULL,
    city TEXT,
    state TEXT
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    seller_id INTEGER NOT NULL,
    order_date TEXT NOT NULL,
    status TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    total_amount REAL NOT NULL CHECK (total_amount >= 0),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
);

CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price > 0),
    discount REAL NOT NULL CHECK (discount >= 0 AND discount <= 1),
    gross_amount REAL NOT NULL,
    discount_amount REAL NOT NULL,
    net_amount REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE payments (
    payment_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    payment_date TEXT NOT NULL,
    amount REAL NOT NULL CHECK (amount > 0),
    status TEXT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
"""


def _build_valid_database(db_path):

    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(VALID_SCHEMA_SQL)

    connection.execute(
        "INSERT INTO customers VALUES (1, 'Cliente A', 'a@teste.com', "
        "'Uberaba', 'MG', '2024-01-01')"
    )
    connection.execute(
        "INSERT INTO products VALUES (1, 'Produto A', 'Books', 10.0, 5.0, 100)"
    )
    connection.execute(
        "INSERT INTO sellers VALUES (1, 'Vendedor A', 'Uberaba', 'MG')"
    )
    connection.execute(
        "INSERT INTO orders VALUES (1, 1, 1, '2024-01-01', 'completed', 'pix', 100.0)"
    )
    connection.execute(
        "INSERT INTO order_items VALUES (1, 1, 1, 2, 10.0, 0.0, 20.0, 0.0, 20.0)"
    )
    connection.execute(
        "INSERT INTO payments VALUES (1, 1, '2024-01-01', 100.0, 'paid')"
    )

    connection.commit()
    connection.close()


@pytest.fixture
def valid_db(tmp_path, monkeypatch):

    db_path = tmp_path / "ecommerce.db"
    _build_valid_database(db_path)

    monkeypatch.setattr(validate, "DATABASE_PATH", db_path)

    return db_path


# CASOS DE SUCESSO

def test_validate_database_passes_with_clean_data(valid_db):

    validate_database()


def test_validate_database_allows_null_customer_email(valid_db):

    connection = sqlite3.connect(valid_db)
    connection.execute(
        "INSERT INTO customers VALUES (2, 'Cliente B', NULL, 'Uberaba', 'MG', '2024-01-02')"
    )
    connection.commit()
    connection.close()

    validate_database()


# CASOS DE FALHA

def test_sqlite_primary_key_prevents_duplicate_ids(valid_db):
    """
    O check de duplicidade em validate.py (COUNT(*) - COUNT(DISTINCT id))
    é uma rede de segurança defensiva: como as colunas são declaradas
    INTEGER PRIMARY KEY, o próprio SQLite já impede duplicidade no INSERT.
    Este teste documenta essa garantia da camada de banco.
    """

    connection = sqlite3.connect(valid_db)
    connection.execute("PRAGMA foreign_keys = OFF")

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            "INSERT INTO products VALUES (1, 'Produto Duplicado', "
            "'Books', 20.0, 10.0, 50)"
        )

    connection.close()


def test_validate_database_raises_on_orphan_order_items(valid_db):

    connection = sqlite3.connect(valid_db)
    connection.execute("PRAGMA foreign_keys = OFF")

    connection.execute(
        "INSERT INTO order_items VALUES "
        "(2, 999999, 1, 1, 10.0, 0.0, 10.0, 0.0, 10.0)"
    )

    connection.commit()
    connection.close()

    with pytest.raises(DataValidationError, match="order_items → orders"):
        validate_database()


def test_validate_database_raises_on_orphan_payments(valid_db):

    connection = sqlite3.connect(valid_db)
    connection.execute("PRAGMA foreign_keys = OFF")

    connection.execute(
        "INSERT INTO payments VALUES (2, 999999, '2024-01-01', 50.0, 'paid')"
    )

    connection.commit()
    connection.close()

    with pytest.raises(DataValidationError, match="payments → orders"):
        validate_database()


def test_schema_prevents_null_in_orders_customer_id(valid_db):
    """
    A checagem de nulos em validate.py para orders.customer_id é uma rede
    de segurança defensiva: a coluna já é NOT NULL no schema.sql, então o
    SQLite recusa o INSERT antes mesmo de a validação rodar. Este teste
    documenta essa garantia da camada de banco.
    """

    connection = sqlite3.connect(valid_db)
    connection.execute("PRAGMA foreign_keys = OFF")

    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            "INSERT INTO orders VALUES "
            "(2, NULL, 1, '2024-01-02', 'completed', 'pix', 50.0)"
        )

    connection.close()


def test_validate_database_raises_on_missing_table(tmp_path, monkeypatch):

    db_path = tmp_path / "ecommerce.db"

    connection = sqlite3.connect(db_path)
    connection.execute(
        "CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL)"
    )
    connection.commit()
    connection.close()

    monkeypatch.setattr(validate, "DATABASE_PATH", db_path)

    with pytest.raises(DataValidationError, match="Tabelas ausentes"):
        validate_database()


def test_validate_database_error_message_lists_all_problems(valid_db):

    connection = sqlite3.connect(valid_db)
    connection.execute("PRAGMA foreign_keys = OFF")

    # Dois problemas simultâneos: order_item órfão + payment órfão.
    connection.execute(
        "INSERT INTO order_items VALUES (2, 999999, 1, 1, 10.0, 0.0, 10.0, 0.0, 10.0)"
    )
    connection.execute(
        "INSERT INTO payments VALUES (2, 888888, '2024-01-01', 50.0, 'paid')"
    )

    connection.commit()
    connection.close()

    with pytest.raises(DataValidationError) as error:
        validate_database()

    message = str(error.value)

    assert "order_items → orders" in message
    assert "payments → orders" in message