import sqlite3
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"
DATABASE_DIR = BASE_DIR / "data" / "database"

DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "ecommerce.db"

def create_connection():
    return sqlite3.connect(DATABASE_PATH)


def load_table(df, table_name, connection):
    print("=" * 60)
    print(f"💾 LOAD — {table_name.upper()}")
    print("=" * 60)

    print(f"Registros: {len(df):,}")
    print(f"Colunas: {len(df.columns)}")

    df.to_sql(
        table_name,
        connection,
        if_exists="replace",
        index=False
    )

    print(f"✅ Tabela '{table_name}' carregada com sucesso.")
    print()


def load_data():
    print("🚀 LOAD.PY FOI EXECUTADO")
    print()
    print(f"📁 Banco: {DATABASE_PATH}")
    print()

    connection = create_connection()

    try:
        customers = pd.read_csv(PROCESSED_DIR / "customers_clean.csv")
        load_table(
            customers,
            "customers",
            connection
        )

        products = pd.read_csv(PROCESSED_DIR / "products_clean.csv")
        load_table(
            products,
            "products",
            connection
        )

        sellers = pd.read_csv(PROCESSED_DIR / "sellers_clean.csv")
        load_table(
            sellers,
            "sellers",
            connection
        )

        orders = pd.read_csv(PROCESSED_DIR / "orders_clean.csv")
        load_table(
            orders,
            "orders",
            connection
        )

        order_items = pd.read_csv(PROCESSED_DIR / "order_items_clean.csv")
        load_table(
            order_items,
            "order_items",
            connection
        )

        payments = pd.read_csv(PROCESSED_DIR / "payments_clean.csv")
        load_table(
            payments,
            "payments",
            connection
        )

        connection.commit()

        print("=" * 60)
        print("🎉 LOAD CONCLUÍDO COM SUCESSO!")
        print("=" * 60)

    except Exception as e:
        connection.rollback()
        print("❌ Erro durante o LOAD:")
        print(e)
        raise

    finally:
        connection.close()
        print()
        print("🔒 Conexão com o banco encerrada.")

if __name__ == "__main__":
    load_data()