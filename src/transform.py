import pandas as pd
from pathlib import Path
print("🚀 TRANSFORM.PY FOI EXECUTADO")


BASE_DIR = Path(__file__).resolve().parents[1] 
RAW_DIR = BASE_DIR / "data" / "raw" 
PROCESSED_DIR = BASE_DIR / "data" / "processed"

def transform_customers(df: pd.DataFrame) -> pd.DataFrame:    
    df = df.copy()
    print("\n" + "=" * 60)
    print("🔄 TRANSFORM — CUSTOMERS")
    print("=" * 60)


    print("\n📊 Estado inicial:")

    print(
        f"Registros: {len(df):,}"
    )

    print(
        f"Colunas: {len(df.columns)}"
    )

    print(
        f"Duplicados: {df.duplicated().sum():,}"
    )

    print(
        f"Nulos: {df.isnull().sum().sum():,}"
    )


    duplicated_before = df.duplicated().sum()

    df = df.drop_duplicates()

    duplicated_after = df.duplicated().sum()

    print(
        "\n🧹 Duplicidades completas removidas: "
        f"{duplicated_before - duplicated_after}"
    )


    text_columns = [
        "name",
        "city",
        "state",
    ]

    for column in text_columns:

        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )


    df["email"] = (
        df["email"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    null_email_count = df["email"].isna().sum()

    print(
        f"📧 E-mails nulos encontrados: "
        f"{null_email_count}"
    )


    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce"
    )

    invalid_dates = df["created_at"].isna().sum()

    print(
        f"📅 Datas inválidas: "
        f"{invalid_dates}"
    )


    invalid_customer_ids = (
        df["customer_id"].isna()
        | (df["customer_id"] <= 0)
    ).sum()

    if invalid_customer_ids > 0:

        raise ValueError(
            "Foram encontrados customer_id inválidos."
        )

    df = (
        df
        .sort_values(
            by="customer_id"
        )
        .reset_index(drop=True)
    )


    print("\n📊 Estado após transformação:")

    print(
        f"Registros: {len(df):,}"
    )

    print(
        f"Colunas: {len(df.columns)}"
    )

    print(
        f"Nulos: {df.isnull().sum().sum():,}"
    )

    print(
        f"Duplicados: {df.duplicated().sum():,}"
    )

    print("\nTipos finais:")

    print(df.dtypes)

    print(
        "\n✅ Transformação de customers concluída."
    )

    return df


def transform_products(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()


    print("\n" + "=" * 60)
    print("🔄 TRANSFORM — PRODUCTS")
    print("=" * 60)

    print("\n📊 Estado inicial:")
    print(f"Registros: {len(df):,}")
    print(f"Colunas: {len(df.columns)}")
    print(f"Duplicados: {df.duplicated().sum():,}")
    print(f"Nulos: {df.isnull().sum().sum(),}")


    duplicated_count = df.duplicated().sum()

    df =  df.drop_duplicates()

    print(
        f"\n🧹 Duplicidades removidas: "
        f"{duplicated_count}"
    )

    df["product_name"] = (
        df["product_name"]
        .astype("string")
        .str.strip()
    )

    df["category"] = (
        df["category"]
        .astype("string")
        .str.strip()
    )

    category_mapping = {
        "eletronicos": "Eletrônicos",
        "Eletronicos": "Eletrônicos",
        "ELETRONICOS": "Eletrônicos",
    }

    df["category"] = (df["category"].replace(category_mapping))

    print("\n🏷️ Categorias encontradas:")

    print(df["category"].value_counts())

    invalid_prices = (df["price"].isna() | (df["price"] <= 0))

    invalid_price_count = invalid_prices.sum()

    print(
        f"\n💰 Preços inválidos: "
        f"{invalid_price_count}"
    )

    invalid_cost = (df["cost"].isna() | (df["cost"] <= 0))

    invalid_cost_count = invalid_cost.sum()

    print(
        f"💵 Custos inválidos: "
        f"{invalid_cost_count}"
    )

    invalid_stock = (df["stock"].isna() | (df["stock"] < 0))

    invalid_stock_count = invalid_stock.sum()

    print(
        f"📦 Estoques inválidos: "
        f"{invalid_stock_count}"
    )

    invalid_records = (invalid_prices | invalid_cost | invalid_stock)

    total_invalid_records = invalid_records.sum()

    print(
        f"\n❌ Registros inválidos removidos: "
        f"{total_invalid_records}"
    )

    df = df.loc[~invalid_records].copy()


    invalid_product_ids = (df["product_id"].isna() | (df["product_id"] <= 0)).sum()

    if invalid_product_ids > 0:
        raise ValueError("Foram encontrados product_id inválidos")


    df["product_id"] = df["product_id"].astype("int64")
    df["price"] = df["price"].astype("float64")
    df["cost"] = df["cost"].astype("float64")
    df["stock"] = df["stock"].astype("int64")

    df = (
        df
        .sort_values("product_id")
        .reset_index(drop=True)
    )

    print("\n📊 Estado após transformação:")

    print(
        f"Registros: {len(df):,}"
    )

    print(
        f"Colunas: {len(df.columns)}"
    )

    print(
        f"Nulos: {df.isnull().sum().sum():,}"
    )

    print(
        f"Duplicados: {df.duplicated().sum():,}"
    )

    print("\nTipos finais:")

    print(df.dtypes)

    print(
        "\n✅ Transformação de products concluída."
    )

    return df



def save_processed_data(
    df: pd.DataFrame,
    filename: str,
) -> None:

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        PROCESSED_DIR / filename
    )

    df.to_csv(
        output_path,
        index=False,
        encoding="utf-8",
    )

    print(
        f"\n💾 Arquivo salvo: "
        f"{output_path}"
    )




if __name__ == "__main__":

    try:

        customers_path = (RAW_DIR / "customers.csv")

        customers = pd.read_csv(customers_path, encoding="utf-8")
        customers_clean = transform_customers(customers)
        save_processed_data(customers_clean, "customers_clean.csv")


        products_path = (RAW_DIR / "products.csv")

        products = pd.read_csv(products_path, encoding="utf-8")
        products_clean = transform_products(products)        
        save_processed_data(products_clean, "products_clean.csv")

        print("\n🎉 TRANSFORMAÇÕES CONCLUÍDAS!")

    except FileNotFoundError as error:
        print(
            f"❌ Arquivo não encontrado: "
            f"{error}"
        )

    except Exception as error:
        print(
            f"❌ Erro durante a transformação: "
            f"{error}"
        )