import sqlite3
from pathlib import Path

import pandas as pd


# CONFIGURAÇÃO DE CAMINHOS

BASE_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DIR = BASE_DIR / "data" / "processed"
DATABASE_DIR = BASE_DIR / "data" / "database"
DATABASE_PATH = DATABASE_DIR / "ecommerce.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


# CONEXÃO COM O BANCO

def create_connection():
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# CRIAÇÃO DO SCHEMA

def create_schema(connection):
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"Schema não encontrado: {SCHEMA_PATH}"
        )

    with open(SCHEMA_PATH, "r", encoding="utf-8") as file:
        schema = file.read()

    connection.executescript(schema)

    print(f"Schema criado com sucesso: {SCHEMA_PATH}")


# CARGA DE UMA TABELA

def load_table(connection, table_name, df):

    if df.empty:
        print(
            f"{table_name}: DataFrame vazio. "
            "Nada para carregar."
        )
        return

    df.to_sql(
        table_name,
        connection,
        if_exists="append",
        index=False
    )

    print(
        f"{table_name}: "
        f"{len(df):,} registros carregados."
    )


# CARGA COMPLETA DO BANCO

def load_data():

    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()
        print("Banco anterior removido.")

    connection = create_connection()

    try:

        print("\n" + "-" * 70)
        print("INICIANDO CARGA DO BANCO")
        print("-" * 70)

        print(f"Banco: {DATABASE_PATH}")
        print(f"Schema: {SCHEMA_PATH}")

        create_schema(connection)

        processed_files = {
            "customers": PROCESSED_DIR / "customers_clean.csv",
            "products": PROCESSED_DIR / "products_clean.csv",
            "sellers": PROCESSED_DIR / "sellers_clean.csv",
            "orders": PROCESSED_DIR / "orders_clean.csv",
            "order_items": PROCESSED_DIR / "order_items_clean.csv",
            "payments": PROCESSED_DIR / "payments_clean.csv",
        }

        dataframes = {}

        for table_name, file_path in processed_files.items():

            if not file_path.exists():
                raise FileNotFoundError(
                    f"Arquivo processado não encontrado: "
                    f"{file_path}"
                )

            dataframes[table_name] = pd.read_csv(
                file_path,
                encoding="utf-8"
            )

        load_table(
            connection,
            "customers",
            dataframes["customers"]
        )

        load_table(
            connection,
            "products",
            dataframes["products"]
        )

        load_table(
            connection,
            "sellers",
            dataframes["sellers"]
        )

        load_table(
            connection,
            "orders",
            dataframes["orders"]
        )

        load_table(
            connection,
            "order_items",
            dataframes["order_items"]
        )

        load_table(
            connection,
            "payments",
            dataframes["payments"]
        )

        connection.commit()

        print("\nCarga concluída com sucesso.")

    except Exception as error:

        connection.rollback()

        print("\nErro durante a carga.")
        print(f"Erro: {error}")

        raise

    finally:

        connection.close()


# EXECUÇÃO DIRETA

if __name__ == "__main__":

    from extract import extract_data

    from transform import (
        transform_data,
        save_processed_data
    )

    extracted_data = extract_data()

    transformed_data = transform_data(
        extracted_data
    )

    save_processed_data(
        transformed_data
    )

    load_data()