import pandas as pd
import pytest

from src.transform import (
    transform_order_items,
    transform_products,
    enforce_referential_integrity,
)


# ============================================================
# TESTES DE TRANSFORMAÇÃO DE PRODUTOS
# ============================================================

def test_product_invalid_price_is_removed():

    df = pd.DataFrame({
        "product_id": [1, 2, 3],
        "product_name": ["Produto A", "Produto B", "Produto C"],
        "category": ["Books", "Beauty", "Sports"],
        "price": [100.0, 0.0, -10.0],
        "cost": [50.0, 30.0, 5.0],
        "stock": [10, 20, 5],
    })

    result = transform_products(df)

    assert len(result) == 1
    assert result["product_id"].tolist() == [1]


def test_product_negative_stock_is_removed():

    df = pd.DataFrame({
        "product_id": [1, 2],
        "product_name": ["Produto A", "Produto B"],
        "category": ["Books", "Beauty"],
        "price": [100.0, 200.0],
        "cost": [50.0, 100.0],
        "stock": [10, -5],
    })

    result = transform_products(df)

    assert len(result) == 1
    assert result["product_id"].tolist() == [1]


# ============================================================
# TESTES DE CÁLCULO DE ORDER ITEMS
# ============================================================

def test_order_item_calculations():

    df = pd.DataFrame({
        "order_item_id": [1],
        "order_id": [100],
        "product_id": [10],
        "quantity": [2],
        "unit_price": [100.0],
        "discount": [0.10],
    })

    result = transform_order_items(df)

    assert result.iloc[0]["gross_amount"] == pytest.approx(200.0)
    assert result.iloc[0]["discount_amount"] == pytest.approx(20.0)
    assert result.iloc[0]["net_amount"] == pytest.approx(180.0)


def test_order_item_invalid_quantity_is_removed():

    df = pd.DataFrame({
        "order_item_id": [1, 2],
        "order_id": [100, 100],
        "product_id": [10, 10],
        "quantity": [2, 0],
        "unit_price": [100.0, 100.0],
        "discount": [0.10, 0.10],
    })

    result = transform_order_items(df)

    assert len(result) == 1
    assert result["order_item_id"].tolist() == [1]


def test_order_item_invalid_discount_is_removed():

    df = pd.DataFrame({
        "order_item_id": [1, 2, 3],
        "order_id": [100, 100, 100],
        "product_id": [10, 10, 10],
        "quantity": [1, 1, 1],
        "unit_price": [100.0, 100.0, 100.0],
        "discount": [0.10, -0.10, 1.10],
    })

    result = transform_order_items(df)

    assert len(result) == 1
    assert result["order_item_id"].tolist() == [1]


# ============================================================
# TESTES DE INTEGRIDADE REFERENCIAL
# ============================================================

def test_referential_integrity_removes_orphan_order_items():

    orders = pd.DataFrame({
        "order_id": [100, 101]
    })

    products = pd.DataFrame({
        "product_id": [10, 20]
    })

    order_items = pd.DataFrame({
        "order_item_id": [1, 2, 3],
        "order_id": [100, 999, 101],
        "product_id": [10, 20, 999],
        "quantity": [1, 1, 1],
        "unit_price": [100.0, 200.0, 300.0],
        "discount": [0.10, 0.10, 0.10]
    })

    payments = pd.DataFrame({
        "payment_id": [1],
        "order_id": [100]
    })

    result = enforce_referential_integrity(
        orders,
        products,
        order_items,
        payments
    )

    clean_order_items = result[0]

    assert len(clean_order_items) == 1
    assert clean_order_items["order_item_id"].tolist() == [1]


def test_referential_integrity_removes_orphan_payments():

    orders = pd.DataFrame({
        "order_id": [100, 101]
    })

    products = pd.DataFrame({
        "product_id": [10]
    })

    order_items = pd.DataFrame({
        "order_item_id": [1],
        "order_id": [100],
        "product_id": [10]
    })

    payments = pd.DataFrame({
        "payment_id": [1, 2],
        "order_id": [100, 999]
    })

    result = enforce_referential_integrity(
        orders,
        products,
        order_items,
        payments
    )

    clean_payments = result[1]

    assert len(clean_payments) == 1
    assert clean_payments["payment_id"].tolist() == [1]