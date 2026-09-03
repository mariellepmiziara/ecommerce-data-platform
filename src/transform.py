from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURAÇÃO
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def remove_full_duplicates(
    df: pd.DataFrame,
    dataset_name: str,
) -> pd.DataFrame:
    """Remove registros completamente duplicados."""

    before = len(df)

    df = df.drop_duplicates().copy()

    removed = before - len(df)

    print(
        f"🧹 {dataset_name}: "
        f"{removed:,} duplicados removidos."
    )

    return df


def normalize_text(
    df: pd.DataFrame,
    columns: list[str],
    lowercase: bool = False,
) -> pd.DataFrame:
    """Normaliza colunas textuais."""

    for column in columns:

        if column not in df.columns:
            continue

        df[column] = df[column].astype("string").str.strip()

        if lowercase:
            df[column] = df[column].str.lower()

    return df


def validate_positive_id(
    df: pd.DataFrame,
    column: str,
    dataset_name: str,
) -> None:
    """Valida IDs obrigatórios."""

    invalid = (
        df[column].isna()
        | (df[column] <= 0)
    )

    if invalid.any():
        count = int(invalid.sum())

        raise ValueError(
            f"❌ {dataset_name}: "
            f"{count} registros possuem "
            f"{column} inválido."
        )


def print_transformation_summary(
    df: pd.DataFrame,
    dataset_name: str,
    initial_rows: int,
) -> None:
    """Exibe resumo da transformação."""

    final_rows = len(df)
    removed = initial_rows - final_rows

    print(
        f"📊 {dataset_name}: "
        f"{initial_rows:,} → "
        f"{final_rows:,} registros "
        f"({removed:,} removidos)"
    )


# ============================================================
# CUSTOMERS
# ============================================================

def transform_customers(
    df: pd.DataFrame,
) -> pd.DataFrame:

    dataset_name = "customers"
    initial_rows = len(df)

    print(f"\n🔄 Transformando {dataset_name}...")

    df = remove_full_duplicates(
        df,
        dataset_name,
    )

    df = normalize_text(
        df,
        ["name", "city", "state"],
    )

    df = normalize_text(
        df,
        ["email"],
        lowercase=True,
    )

    null_emails = int(df["email"].isna().sum())

    if null_emails:
        print(
            f"ℹ️ {null_emails:,} clientes "
            f"sem e-mail. Mantidos."
        )

    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce",
    )

    invalid_dates = int(df["created_at"].isna().sum())

    if invalid_dates:
        print(
            f"⚠️ {invalid_dates:,} datas inválidas "
            f"em customers."
        )

    validate_positive_id(
        df,
        "customer_id",
        dataset_name,
    )

    df["customer_id"] = df["customer_id"].astype(int)

    df = df.sort_values("customer_id").reset_index(drop=True)

    print_transformation_summary(
        df,
        dataset_name,
        initial_rows,
    )

    return df


# ============================================================
# PRODUCTS
# ============================================================

def transform_products(
    df: pd.DataFrame,
) -> pd.DataFrame:

    dataset_name = "products"
    initial_rows = len(df)

    print(f"\n🔄 Transformando {dataset_name}...")

    df = remove_full_duplicates(
        df,
        dataset_name,
    )

    df = normalize_text(
        df,
        ["product_name", "category"],
    )

    # Padronização de categorias
    category_map = {
        "eletronicos": "Eletrônicos",
        "Eletronicos": "Eletrônicos",
        "ELETRONICOS": "Eletrônicos",
    }

    df["category"] = df["category"].replace(
        category_map
    )

    # Price
    invalid_price = (
        df["price"].isna()
        | (df["price"] <= 0)
    )

    if invalid_price.any():
        print(
            f"⚠️ {int(invalid_price.sum()):,} "
            f"preços inválidos removidos."
        )

        df = df.loc[~invalid_price].copy()

    # Cost
    invalid_cost = (
        df["cost"].isna()
        | (df["cost"] <= 0)
    )

    if invalid_cost.any():
        print(
            f"⚠️ {int(invalid_cost.sum()):,} "
            f"custos inválidos removidos."
        )

        df = df.loc[~invalid_cost].copy()

    # Stock
    invalid_stock = (
        df["stock"].isna()
        | (df["stock"] < 0)
    )

    if invalid_stock.any():
        print(
            f"⚠️ {int(invalid_stock.sum()):,} "
            f"estoques inválidos removidos."
        )

        df = df.loc[~invalid_stock].copy()

    validate_positive_id(
        df,
        "product_id",
        dataset_name,
    )

    df["product_id"] = df["product_id"].astype(int)
    df["price"] = df["price"].astype(float)
    df["cost"] = df["cost"].astype(float)
    df["stock"] = df["stock"].astype(int)

    df = df.sort_values("product_id").reset_index(drop=True)

    print_transformation_summary(
        df,
        dataset_name,
        initial_rows,
    )

    return df


# ============================================================
# SELLERS
# ============================================================

def transform_sellers(
    df: pd.DataFrame,
) -> pd.DataFrame:

    dataset_name = "sellers"
    initial_rows = len(df)

    print(f"\n🔄 Transformando {dataset_name}...")

    df = remove_full_duplicates(
        df,
        dataset_name,
    )

    validate_positive_id(
        df,
        "seller_id",
        dataset_name,
    )

    # Remove IDs duplicados mantendo o primeiro
    before = len(df)

    df = df.drop_duplicates(
        subset=["seller_id"],
        keep="first",
    ).copy()

    print(
        f"🧹 seller_id duplicados removidos: "
        f"{before - len(df):,}"
    )

    df = normalize_text(
        df,
        ["seller_name", "city", "state"],
    )

    df["seller_id"] = df["seller_id"].astype(int)

    df = df.sort_values("seller_id").reset_index(drop=True)

    print_transformation_summary(
        df,
        dataset_name,
        initial_rows,
    )

    return df


# ============================================================
# ORDERS
# ============================================================

def transform_orders(
    df: pd.DataFrame,
) -> pd.DataFrame:

    dataset_name = "orders"
    initial_rows = len(df)

    print(f"\n🔄 Transformando {dataset_name}...")

    df = remove_full_duplicates(
        df,
        dataset_name,
    )

    for column in [
        "order_id",
        "customer_id",
        "seller_id",
    ]:
        validate_positive_id(
            df,
            column,
            dataset_name,
        )

    # Datas
    df["order_date"] = pd.to_datetime(
        df["order_date"],
        errors="coerce",
    )

    invalid_dates = df["order_date"].isna()

    if invalid_dates.any():
        print(
            f"⚠️ {int(invalid_dates.sum()):,} "
            f"pedidos com data inválida removidos."
        )

        df = df.loc[~invalid_dates].copy()

    # Textos
    df = normalize_text(
        df,
        ["status", "payment_method"],
        lowercase=True,
    )

    # Total
    invalid_amount = (
        df["total_amount"].isna()
        | (df["total_amount"] < 0)
    )

    if invalid_amount.any():
        print(
            f"⚠️ {int(invalid_amount.sum()):,} "
            f"totais inválidos removidos."
        )

        df = df.loc[~invalid_amount].copy()

    df["order_id"] = df["order_id"].astype(int)
    df["customer_id"] = df["customer_id"].astype(int)
    df["seller_id"] = df["seller_id"].astype(int)
    df["total_amount"] = df["total_amount"].astype(float)

    df = df.sort_values("order_id").reset_index(drop=True)

    print_transformation_summary(
        df,
        dataset_name,
        initial_rows,
    )

    return df


# ============================================================
# ORDER ITEMS
# ============================================================

def transform_order_items(
    df: pd.DataFrame,
) -> pd.DataFrame:

    dataset_name = "order_items"
    initial_rows = len(df)

    print(f"\n🔄 Transformando {dataset_name}...")

    df = remove_full_duplicates(
        df,
        dataset_name,
    )

    for column in [
        "order_item_id",
        "order_id",
        "product_id",
    ]:
        validate_positive_id(
            df,
            column,
            dataset_name,
        )

    # Quantity
    invalid_quantity = (
        df["quantity"].isna()
        | (df["quantity"] <= 0)
    )

    # Unit price
    invalid_price = (
        df["unit_price"].isna()
        | (df["unit_price"] <= 0)
    )

    # Discount
    invalid_discount = (
        df["discount"].isna()
        | (df["discount"] < 0)
        | (df["discount"] > 1)
    )

    invalid = (
        invalid_quantity
        | invalid_price
        | invalid_discount
    )

    if invalid.any():
        print(
            f"⚠️ {int(invalid.sum()):,} "
            f"order_items inválidos removidos."
        )

        df = df.loc[~invalid].copy()

    # Tipos
    df["order_item_id"] = df[
        "order_item_id"
    ].astype(int)

    df["order_id"] = df[
        "order_id"
    ].astype(int)

    df["product_id"] = df[
        "product_id"
    ].astype(int)

    df["quantity"] = df[
        "quantity"
    ].astype(int)

    df["unit_price"] = df[
        "unit_price"
    ].astype(float)

    df["discount"] = df[
        "discount"
    ].astype(float)

    # ========================================================
    # MÉTRICAS DERIVADAS
    # ========================================================

    df["gross_amount"] = (
        df["quantity"]
        * df["unit_price"]
    )

    df["discount_amount"] = (
        df["gross_amount"]
        * df["discount"]
    )

    df["net_amount"] = (
        df["gross_amount"]
        - df["discount_amount"]
    )

    print(
        f"💰 Gross amount: "
        f"{df['gross_amount'].sum():,.2f}"
    )

    print(
        f"💸 Discount amount: "
        f"{df['discount_amount'].sum():,.2f}"
    )

    print(
        f"💵 Net amount: "
        f"{df['net_amount'].sum():,.2f}"
    )

    df = df.sort_values(
        "order_item_id"
    ).reset_index(drop=True)

    print_transformation_summary(
        df,
        dataset_name,
        initial_rows,
    )

    return df


# ============================================================
# PAYMENTS
# ============================================================

def transform_payments(
    df: pd.DataFrame,
) -> pd.DataFrame:

    dataset_name = "payments"
    initial_rows = len(df)

    print(f"\n🔄 Transformando {dataset_name}...")

    df = remove_full_duplicates(
        df,
        dataset_name,
    )

    invalid_payment_id = (
        df["payment_id"].isna()
        | (df["payment_id"] <= 0)
    )

    invalid_order_id = (
        df["order_id"].isna()
        | (df["order_id"] <= 0)
    )

    invalid_date = pd.to_datetime(
        df["payment_date"],
        errors="coerce",
    ).isna()

    invalid_amount = (
        df["amount"].isna()
        | (df["amount"] <= 0)
    )

    invalid = (
        invalid_payment_id
        | invalid_order_id
        | invalid_date
        | invalid_amount
    )

    if invalid.any():
        print(
            f"⚠️ {int(invalid.sum()):,} "
            f"payments inválidos removidos."
        )

        df = df.loc[~invalid].copy()

    df["payment_date"] = pd.to_datetime(
        df["payment_date"],
        errors="coerce",
    )

    df = normalize_text(
        df,
        ["status"],
        lowercase=True,
    )

    df["payment_id"] = df[
        "payment_id"
    ].astype(int)

    df["order_id"] = df[
        "order_id"
    ].astype(int)

    df["amount"] = df[
        "amount"
    ].astype(float)

    df = df.sort_values(
        "payment_id"
    ).reset_index(drop=True)

    print_transformation_summary(
        df,
        dataset_name,
        initial_rows,
    )

    return df


# ============================================================
# REFERENTIAL INTEGRITY
# ============================================================

def enforce_referential_integrity(
    orders: pd.DataFrame,
    products: pd.DataFrame,
    order_items: pd.DataFrame,
    payments: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:

    print("\n🔗 Verificando integridade referencial...")

    valid_order_ids = set(
        orders["order_id"]
    )

    valid_product_ids = set(
        products["product_id"]
    )

    # --------------------------------------------------------
    # ORDER ITEMS
    # --------------------------------------------------------

    before_items = len(order_items)

    order_items = order_items[
        order_items["order_id"].isin(
            valid_order_ids
        )
        &
        order_items["product_id"].isin(
            valid_product_ids
        )
    ].copy()

    removed_items = (
        before_items - len(order_items)
    )

    print(
        f"🧹 order_items removidos por "
        f"FK inválida: {removed_items:,}"
    )

    # --------------------------------------------------------
    # PAYMENTS
    # --------------------------------------------------------

    before_payments = len(payments)

    payments = payments[
        payments["order_id"].isin(
            valid_order_ids
        )
    ].copy()

    removed_payments = (
        before_payments - len(payments)
    )

    print(
        f"🧹 payments removidos por "
        f"FK inválida: {removed_payments:,}"
    )

    return order_items, payments


# ============================================================
# TRANSFORMAÇÃO COMPLETA
# ============================================================

def transform_data(
    data: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:

    print("\n" + "=" * 60)
    print("🔄 ETAPA TRANSFORM")
    print("=" * 60)

    customers = transform_customers(
        data["customers"]
    )

    products = transform_products(
        data["products"]
    )

    sellers = transform_sellers(
        data["sellers"]
    )

    orders = transform_orders(
        data["orders"]
    )

    order_items = transform_order_items(
        data["order_items"]
    )

    payments = transform_payments(
        data["payments"]
    )

    order_items, payments = (
        enforce_referential_integrity(
            orders,
            products,
            order_items,
            payments,
        )
    )

    transformed_data = {
        "customers": customers,
        "products": products,
        "sellers": sellers,
        "orders": orders,
        "order_items": order_items,
        "payments": payments,
    }

    print("\n" + "=" * 60)
    print("✅ TRANSFORMAÇÃO CONCLUÍDA")
    print("=" * 60)

    return transformed_data


# ============================================================
# SALVAR PROCESSADOS
# ============================================================

def save_processed_data(
    data: dict[str, pd.DataFrame],
) -> None:

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("\n💾 Salvando dados processados...")

    for dataset_name, df in data.items():

        output_path = (
            PROCESSED_DIR
            / f"{dataset_name}_clean.csv"
        )

        df.to_csv(
            output_path,
            index=False,
            encoding="utf-8",
        )

        print(
            f"✅ {output_path.name}: "
            f"{len(df):,} registros"
        )

if __name__ == "__main__":

    from extract import extract_data

    data = extract_data()

    transformed_data = transform_data(data)

    save_processed_data(transformed_data)