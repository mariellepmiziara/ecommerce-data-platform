import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)



BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"


# FUNÇÕES AUXILIARES

def remove_full_duplicates(
    df: pd.DataFrame,
    dataset_name: str,
) -> pd.DataFrame:
    
    before = len(df)

    df = df.drop_duplicates().copy()

    removed = before - len(df)

    logger.info(
        "🧹 %s: %s duplicados removidos.",
        dataset_name,
        f"{removed:,}",
    )

    return df


def normalize_text(
    df: pd.DataFrame,
    columns: list[str],
    lowercase: bool = False,
) -> pd.DataFrame:
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
    final_rows = len(df)
    removed = initial_rows - final_rows

    logger.info(
        "📊 %s: %s → %s registros (%s removidos)",
        dataset_name,
        f"{initial_rows:,}",
        f"{final_rows:,}",
        f"{removed:,}",
    )


# CUSTOMERS

def transform_customers(
    df: pd.DataFrame,
) -> pd.DataFrame:

    dataset_name = "customers"
    initial_rows = len(df)

    logger.info("🔄 Transformando %s...", dataset_name)

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
        logger.info(
            "ℹ️ %s clientes sem e-mail. Mantidos.",
            f"{null_emails:,}",
        )

    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce",
    )

    invalid_dates = int(df["created_at"].isna().sum())

    if invalid_dates:
        logger.warning(
            "⚠️ %s datas inválidas em customers.",
            f"{invalid_dates:,}",
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


# PRODUCTS

def transform_products(
    df: pd.DataFrame,
) -> pd.DataFrame:

    dataset_name = "products"
    initial_rows = len(df)

    logger.info("🔄 Transformando %s...", dataset_name)

    df = remove_full_duplicates(
        df,
        dataset_name,
    )

    df = normalize_text(
        df,
        ["product_name", "category"],
    )

    category_map = {
        "eletronicos": "Eletrônicos",
        "Eletronicos": "Eletrônicos",
        "ELETRONICOS": "Eletrônicos",
    }

    df["category"] = df["category"].replace(
        category_map
    )

    invalid_price = (
        df["price"].isna()
        | (df["price"] <= 0)
    )

    if invalid_price.any():
        logger.warning(
            "⚠️ %s preços inválidos removidos.",
            f"{int(invalid_price.sum()):,}",
        )

        df = df.loc[~invalid_price].copy()

    invalid_cost = (
        df["cost"].isna()
        | (df["cost"] <= 0)
    )

    if invalid_cost.any():
        logger.warning(
            "⚠️ %s custos inválidos removidos.",
            f"{int(invalid_cost.sum()):,}",
        )

        df = df.loc[~invalid_cost].copy()

    invalid_stock = (
        df["stock"].isna()
        | (df["stock"] < 0)
    )

    if invalid_stock.any():
        logger.warning(
            "⚠️ %s estoques inválidos removidos.",
            f"{int(invalid_stock.sum()):,}",
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


# SELLERS

def transform_sellers(
    df: pd.DataFrame,
) -> pd.DataFrame:

    dataset_name = "sellers"
    initial_rows = len(df)

    logger.info("🔄 Transformando %s...", dataset_name)

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

    logger.info(
        "🧹 seller_id duplicados removidos: %s",
        f"{before - len(df):,}",
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


# ORDERS

def transform_orders(
    df: pd.DataFrame,
) -> pd.DataFrame:

    dataset_name = "orders"
    initial_rows = len(df)

    logger.info("🔄 Transformando %s...", dataset_name)

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

    df["order_date"] = pd.to_datetime(
        df["order_date"],
        errors="coerce",
    )

    invalid_dates = df["order_date"].isna()

    if invalid_dates.any():
        logger.warning(
            "⚠️ %s pedidos com data inválida removidos.",
            f"{int(invalid_dates.sum()):,}",
        )

        df = df.loc[~invalid_dates].copy()

    df = normalize_text(
        df,
        ["status", "payment_method"],
        lowercase=True,
    )

    invalid_amount = (
        df["total_amount"].isna()
        | (df["total_amount"] < 0)
    )

    if invalid_amount.any():
        logger.warning(
            "⚠️ %s totais inválidos removidos.",
            f"{int(invalid_amount.sum()):,}",
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


# ORDER ITEMS

def transform_order_items(
    df: pd.DataFrame,
) -> pd.DataFrame:

    dataset_name = "order_items"
    initial_rows = len(df)

    logger.info("🔄 Transformando %s...", dataset_name)

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

    invalid_quantity = (
        df["quantity"].isna()
        | (df["quantity"] <= 0)
    )

    invalid_price = (
        df["unit_price"].isna()
        | (df["unit_price"] <= 0)
    )

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
        logger.warning(
            "⚠️ %s order_items inválidos removidos.",
            f"{int(invalid.sum()):,}",
        )

        df = df.loc[~invalid].copy()

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

    # MÉTRICAS DERIVADAS

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

    logger.info(
        "💰 Gross amount: %.2f | 💸 Discount amount: %.2f | 💵 Net amount: %.2f",
        df["gross_amount"].sum(),
        df["discount_amount"].sum(),
        df["net_amount"].sum(),
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


# PAYMENTS

def transform_payments(
    df: pd.DataFrame,
) -> pd.DataFrame:

    dataset_name = "payments"
    initial_rows = len(df)

    logger.info("🔄 Transformando %s...", dataset_name)

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
        logger.warning(
            "⚠️ %s payments inválidos removidos.",
            f"{int(invalid.sum()):,}",
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


# REFERENTIAL INTEGRITY

def enforce_referential_integrity(
    orders: pd.DataFrame,
    products: pd.DataFrame,
    order_items: pd.DataFrame,
    payments: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:

    logger.info("🔗 Verificando integridade referencial...")

    valid_order_ids = set(
        orders["order_id"]
    )

    valid_product_ids = set(
        products["product_id"]
    )

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

    log_level = logging.WARNING if removed_items else logging.INFO

    logger.log(
        log_level,
        "🧹 order_items removidos por FK inválida: %s",
        f"{removed_items:,}",
    )

    before_payments = len(payments)

    payments = payments[
        payments["order_id"].isin(
            valid_order_ids
        )
    ].copy()

    removed_payments = (
        before_payments - len(payments)
    )

    log_level = logging.WARNING if removed_payments else logging.INFO

    logger.log(
        log_level,
        "🧹 payments removidos por FK inválida: %s",
        f"{removed_payments:,}",
    )

    return order_items, payments


def transform_data(
    data: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:

    logger.info("🔄 ETAPA TRANSFORM — iniciando")

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

    logger.info("✅ TRANSFORMAÇÃO CONCLUÍDA")

    return transformed_data


def save_processed_data(
    data: dict[str, pd.DataFrame],
) -> None:

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger.info("💾 Salvando dados processados...")

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

        logger.info(
            "✅ %s: %s registros",
            output_path.name,
            f"{len(df):,}",
        )


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    from extract import extract_data

    data = extract_data()

    transformed_data = transform_data(data)

    save_processed_data(transformed_data)