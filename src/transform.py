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
    print(f"Registros: {len(df):,}")
    print(f"Colunas: {len(df.columns)}")
    print(f"Duplicados: {df.duplicated().sum():,}")
    print(f"Nulos: {df.isnull().sum().sum():,}")


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
    print(f"Nulos: {df.isnull().sum().sum()}")


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

def transform_orders(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    print("\n" + "=" * 60)
    print("🔄 TRANSFORM — ORDERS")
    print("=" * 60)

    print("\n📊 Estado inicial:")

    print(f"Registros: {len(df):,}")
    print(f"Colunas: {len(df.columns):,}")
    print(f"Duplicados: {df.duplicated().sum():,}")
    print(f"Nulos: {df.isnull().sum().sum():,}")

    duplicated_count = df.duplicated().sum()
    df = df.drop_duplicates()

    print(
        f"\n🧹 Duplicidades removidas: "
        f"{duplicated_count}"
    )

    invalid_order_ids = (df["order_id"].isna() | (df["order_id"] <= 0)).sum()

    print(
        f"🆔 order_id inválidos: "
        f"{invalid_order_ids}"
    )

    if invalid_order_ids > 0 :
        raise ValueError("Foram encontrados order_id inválidos.")

    invalid_customer_ids = (df["customer_id"].isna() | (df["customer_id"] <= 0)).sum()
    print(
        f"👤 customer_id inválidos: "
        f"{invalid_customer_ids}"
    )

    if invalid_customer_ids > 0 :
        raise ValueError("Foram encontrados customer_id inválidos.")

    invalid_seller_ids = (df["seller_id"].isna() | (df["seller_id"] <= 0)).sum()

    print(
        f"🏪 seller_id inválidos: "
        f"{invalid_seller_ids}"
    )

    if invalid_seller_ids > 0:
        raise ValueError("Foram encontrados seller_id inválidos.")

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    invalid_dates = (df["order_date"].isna()).sum()
    print(
        f"📅 Datas inválidas: "
        f"{invalid_dates}"
    )

    if invalid_dates > 0:
        df = df.loc[df["order_date"].notna()].copy()
    print(
        f"🗑️ Pedidos removidos por "
        f"data inválida: {invalid_dates}"
    )

    df["status"] = (
        df["status"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    print("\n📌 Status encontrados:")

    print(df["status"].value_counts())

    df["payment_method"] = (
        df["payment_method"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    print("\n💳 Métodos de pagamento:")

    print(df["payment_method"].value_counts())


    invalid_amounts = (df["total_amount"].isna() | (df["total_amount"] < 0))
    invalid_amount_count = (invalid_amounts.sum())
    print(
        f"\n💰 Valores inválidos: "
        f"{invalid_amount_count}"
    )
    if invalid_amount_count > 0:
        df = df.loc[~invalid_amounts].copy()
    print(
        f"🗑️ Pedidos removidos por "
        f"valor inválido: "
        f"{invalid_amount_count}"
    )

    df["order_id"] = (df["order_id"].astype("int64"))
    df["customer_id"] = (df["customer_id"].astype("int64"))
    df["seller_id"] = (df["seller_id"].astype("int64"))
    df["total_amount"] = (df["total_amount"].astype("float64"))

    df = (df.sort_values("order_id").reset_index(drop=True))

    print("\n📊 Estado após transformação:")

    print(f"Registros: {len(df):,}")
    print(f"Colunas: {len(df.columns):,}")

    print(
        f"Nulos: "
        f"{df.isnull().sum().sum():,}"
    )

    print(
        f"Duplicados: "
        f"{df.duplicated().sum():,}"
    )

    print("\nTipos finais:")
    print(df.dtypes)
    print("\n✅ Transformação de orders concluída.")
    return df

def transform_order_items(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    print("\n" + "=" * 60)
    print("🔄 TRANSFORM — ORDER_ITEMS")
    print("=" * 60)

    print("\n📊 Estado inicial:")
    print(f"Registros: {len(df):,}")
    print(f"Colunas: {len(df.columns):,}")
    print(f"Duplicados: {df.duplicated().sum():,}")
    print(f"Nulos: {df.isnull().sum().sum():,}")

    duplicated_count = df.duplicated().sum()
    df = df.drop_duplicates()
    print(
        f"\n🧹 Duplicidades removidas: "
        f"{duplicated_count}"
    )
    print("\n🔎 Verificação de order_item_id:")
    print(df["order_item_id"].head(10))
    print("\nTipo:")
    print(df["order_item_id"].dtype)
    print("\nNulos:")
    print(df["order_item_id"].isna().sum())
    print("\nValores mínimos e máximos:")
    print(df["order_item_id"].min())
    print(df["order_item_id"].max())

    invalid_order_item_ids = (df["order_item_id"].isna() | (df["order_item_id"] <= 0))
    invalid_order_item_count = invalid_order_item_ids.sum()
    print(
        f"🆔 order_item_id inválidos: "
        f"{invalid_order_item_count}"
    )
    if invalid_order_item_count > 0:
        raise ValueError("Foram encontrados order_item_id inválidos.")


    invalid_order_ids = (df["order_id"].isna() | (df["order_id"] <= 0)).sum()
    print(
        f"🛒 order_id inválidos: "
        f"{invalid_order_ids}"
    )
    if invalid_order_ids > 0:
        raise ValueError("Foram encontrados order_id inválidos.")

    invalid_product_ids = (df["product_id"].isna() | (df["product_id"] <= 0)).sum()
    print(
        f"📦 product_id inválidos: "
        f"{invalid_product_ids}"
    )
    if invalid_product_ids > 0:
        raise ValueError("Foram encontrados product_id inválidos.")


    invalid_quantity = (df["quantity"].isna() | (df["quantity"] <= 0))
    invalid_quantity_count = (invalid_quantity.sum())
    print(
        f"🔢 Quantidades inválidas: "
        f"{invalid_quantity_count}"
    )

    invalid_unit_price = (df["unit_price"].isna() | (df["unit_price"] <= 0))
    invalid_unit_price_count = (invalid_unit_price.sum())
    print(
        f"💰 Preços unitários inválidos: "
        f"{invalid_unit_price_count}"
    )


    invalid_discount = (
        df["discount"].isna()
        | (df["discount"] < 0)
        | (df["discount"] > 1)
    )

    invalid_discount_count = (invalid_discount.sum())
    print(
        f"🏷️ Descontos inválidos: "
        f"{invalid_discount_count}"
    )

    invalid_records = (invalid_quantity | invalid_unit_price | invalid_discount)
    total_invalid_records = (invalid_records.sum())
    print(
        f"\n❌ Registros inválidos: "
        f"{total_invalid_records}"
    )
    if total_invalid_records > 0:
        df = df.loc[~invalid_records].copy()
        print(
            f"🗑️ Registros removidos: "
            f"{total_invalid_records}"
        )

    df["order_item_id"] = (df["order_item_id"].astype("int64"))
    df["order_id"] = (df["order_id"].astype("int64"))
    df["product_id"] = (df["product_id"].astype("int64"))
    df["quantity"] = (df["quantity"].astype("int64"))
    df["unit_price"] = (df["unit_price"].astype("float64"))
    df["discount"] = (df["discount"].astype("float64"))

    df["gross_amount"] = (df["quantity"] * df["unit_price"])
    df["discount_amount"] = (df["gross_amount"] * df["discount"])
    df["net_amount"] = (df["gross_amount"] - df["discount_amount"])
    print("\n💵 Métricas calculadas:")
    print(
        f"Valor bruto total: "
        f"R$ {df['gross_amount'].sum():,.2f}"
    )

    print(
        f"Desconto total: "
        f"R$ {df['discount_amount'].sum():,.2f}"
    )

    print(
        f"Valor líquido total: "
        f"R$ {df['net_amount'].sum():,.2f}"
    )

    df = (df.sort_values("order_item_id").reset_index(drop=True))

    print("\n📊 Estado após transformação:")

    print(
        f"Registros: {len(df):,}"
    )

    print(
        f"Colunas: {len(df.columns):,}"
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
        "\n✅ Transformação de order_items concluída."
    )

    return df

def transform_payments(df:pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    print("\n" + "=" * 60)
    print("🔄 TRANSFORM — PAYMENTS")
    print("=" * 60)

    print("\n📊 Estado inicial:")
    print(f"Registros: {len(df):,}")
    print(f"Colunas: {len(df.columns):,}")
    print(f"Duplicados: {df.duplicated().sum():,}")
    print(f"Nulos: {df.isnull().sum().sum():,}")

    duplicated_count = df.duplicated().sum()

    df = df.drop_duplicates()

    print(
        f"\n🧹 Duplicidades removidas: "
        f"{duplicated_count}"
    )

    invalid_payment_ids = (df["payment_id"].isna() | (df["payment_id"] <= 0))
    invalid_payment_id_count = (invalid_payment_ids.sum())
    print(
        f"🆔 payment_id inválidos: "
        f"{invalid_payment_id_count}"
    )

    invalid_orders_ids = (df["order_id"].isna() | (df["order_id"] <= 0))
    invalid_order_id_count = (invalid_orders_ids.sum())
    print(
        f"🛒 order_id inválidos: "
        f"{invalid_order_id_count}"
    )

    df["payment_date"] = pd.to_datetime(df["payment_date"], errors="coerce")
    invalid_dates = (df["payment_date"].isna())
    invalid_date_count = (invalid_dates.sum())
    print(
        f"📅 Datas inválidas: "
        f"{invalid_date_count}"
    )

    invalid_amount = (df["amount"].isna() | df["amount"] <= 0)
    invalid_amount_count = (invalid_amount.sum())
    print(
        f"💰 Valores inválidos: "
        f"{invalid_amount_count}"
    )

    df["status"] = (df["status"].astype("string").str.strip().str.lower())

    print("\n💳 Status encontrados:")
    print(df["status"].value_counts())

    invalid_records = (invalid_payment_ids | invalid_orders_ids | invalid_dates | invalid_amount)
    total_invalid_records = (invalid_records.sum())

    print(
        f"\n❌ Registros inválidos: "
        f"{total_invalid_records}"
    )

    if total_invalid_records > 0:
        df = df.loc[~invalid_records].copy()

        print(
            f"🗑️ Registros removidos: "
            f"{total_invalid_records}"
        )


    df["payment_id"] = (df["payment_id"].astype("int64"))
    df["order_id"] = (df["order_id"].astype("int64"))
    df["amount"] = (df["amount"].astype("float64"))

    df = (df.sort_values("payment_id").reset_index(drop=True))

    print("\n📊 Estado após transformação:")
    print(f"Registros: {len(df):,}")
    print(f"Colunas: {len(df.columns):,}")
    print(f"Nulos: {df.isnull().sum().sum():,}")
    print(f"Duplicados: {df.duplicated().sum():,}")
    print("\nTipos finais:")
    print(df.dtypes)
    print("\n✅ Transformação de payments concluída.")

    return df

def transform_sellers(df:pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    print("\n" + "=" * 60)
    print("🔄 TRANSFORM — SELLERS")
    print("=" * 60)

    print("\n📊 Estado inicial:")
    print(f"Registros: {len(df):,}")
    print(f"Colunas: {len(df.columns)}")
    print(f"Duplicados: {df.duplicated().sum():,}")
    print(f"Nulos: {df.isnull().sum().sum():,}")

    duplicated_count = df.duplicated().sum()

    df = df.drop_duplicates()

    print(
        f"\n🧹 Duplicidades removidas: "
        f"{duplicated_count}"
    )

    invalid_seller_ids = (df["seller_id"].isna() | (df["seller_id"] <= 0)).sum()
    print(
        f"🏪 seller_id inválidos: "
        f"{invalid_seller_ids}"
    )

    if invalid_seller_ids > 0:
        raise ValueError("Foram encontrados seller_id inválidos.")

    duplicate_seller_ids = df.duplicated(subset=["seller_id"]).sum()
    df = df.drop_duplicates(subset=["seller_id"],keep="first")

    print(
        f"🆔 seller_id duplicados removidos: "
        f"{duplicate_seller_ids}"
    )

    text_columns = [
        "seller_name",
        "city",
        "state"
    ]

    for column in text_columns:
        df[column] = (df[column].astype("string").str.strip())

    print("\n📍 Estados encontrados:")
    print(df["state"].value_counts())

    df["seller_id"] = df["seller_id"].astype("int64")

    df = (df.sort_values("seller_id").reset_index(drop=True))

    print("\n📊 Estado após transformação:")
    print(f"Registros: {len(df):,}")
    print(f"Colunas: {len(df.columns)}")
    print(f"Nulos: {df.isnull().sum().sum():,}")
    print(f"Duplicados: {df.duplicated().sum():,}")

    print("\nTipos finais:")
    print(df.dtypes)

    print(
        "\n✅ Transformação de sellers concluída."
    )

    return df

def enforce_referential_integrity(
        orders: pd.DataFrame,
        products: pd.DataFrame,
        order_items: pd.DataFrame,
        payments: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    print("\n" + "=" * 60)
    print("🔗 INTEGRIDADE REFERENCIAL — pós-transformação")
    print("=" * 60)

    valid_order_ids = set(orders["order_id"])
    valid_product_ids = set(products["product_id"])

    before = len(order_items)
    order_items = order_items[
        order_items["order_id"].isin(valid_order_ids)
        & order_items["product_id"].isin(valid_product_ids)
    ].reset_index(drop=True)
    removed = before - len(order_items)
    print(
        f"🗑️ order_items removidos "
        f"(order_id/product_id órfãos): {removed}"
    )

    before = len(payments)
    payments = payments[
        payments["order_id"].isin(valid_order_ids)
    ].reset_index(drop=True)
    removed = before - len(payments)
    print(
        f"🗑️ payments removidos "
        f"(order_id órfão): {removed}"
    )
 
    print("\n✅ Integridade referencial garantida.")
 
    return order_items, payments

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
        # --- Tabelas "pai" primeiro ---
        customers_path = (RAW_DIR / "customers.csv")
        customers = pd.read_csv(customers_path, encoding="utf-8")
        customers_clean = transform_customers(customers)
        save_processed_data(customers_clean, "customers_clean.csv")

        products_path = (RAW_DIR / "products.csv")
        products = pd.read_csv(products_path, encoding="utf-8")
        products_clean = transform_products(products)
        save_processed_data(products_clean, "products_clean.csv")

        sellers_path = (RAW_DIR / "sellers.csv")
        sellers = pd.read_csv(sellers_path, encoding="utf-8")
        sellers_clean = transform_sellers(sellers)
        save_processed_data(sellers_clean, "sellers_clean.csv")

        orders_path = (RAW_DIR / "orders.csv")
        orders = pd.read_csv(orders_path, encoding="utf-8")
        orders_clean = transform_orders(orders)
        save_processed_data(orders_clean, "orders_clean.csv")

        # --- Tabelas "filhas" ---
        order_items_path = (RAW_DIR / "order_items.csv")
        order_items = pd.read_csv(order_items_path, encoding="utf-8")
        order_items_clean = transform_order_items(order_items)

        payments_path = (RAW_DIR / "payments.csv")
        payments = pd.read_csv(payments_path, encoding="utf-8")
        payments_clean = transform_payments(payments)

        # --- Garante que nenhuma linha órfã sobreviva ---
        order_items_clean, payments_clean = enforce_referential_integrity(
            orders_clean, products_clean, order_items_clean, payments_clean
        )

        save_processed_data(order_items_clean, "order_items_clean.csv")
        save_processed_data(payments_clean, "payments_clean.csv")

        print("\n🎉 TRANSFORMAÇÕES CONCLUÍDAS!")

    except FileNotFoundError as error:
        print(f"❌ Arquivo não encontrado: {error}")

    except Exception as error:
        print(f"❌ Erro durante a transformação: {error}")