import pandas as pd
import pytest

from src import extract
from src.extract import (
    validate_schema,
    validate_extracted_data,
    read_csv,
    extract_data,
)



def test_validate_schema_passes_when_all_columns_present():

    df = pd.DataFrame({
        "customer_id": [1],
        "name": ["Cliente A"],
        "email": ["a@teste.com"],
        "city": ["Uberaba"],
        "state": ["MG"],
        "created_at": ["2024-01-01"],
    })

    # Não deve levantar exceção.
    validate_schema(df, "customers")


def test_validate_schema_raises_when_column_missing():

    df = pd.DataFrame({
        "customer_id": [1],
        "name": ["Cliente A"],
        # faltam email, city, state, created_at
    })

    with pytest.raises(ValueError, match="Colunas ausentes"):
        validate_schema(df, "customers")


def test_validate_schema_reports_all_missing_columns():

    df = pd.DataFrame({"seller_id": [1]})

    with pytest.raises(ValueError) as error:
        validate_schema(df, "sellers")

    message = str(error.value)

    assert "seller_name" in message
    assert "city" in message
    assert "state" in message



def test_validate_extracted_data_report_counts_rows_and_columns():

    df = pd.DataFrame({
        "product_id": [1, 2, 3],
        "product_name": ["A", "B", "C"],
        "category": ["Books", "Beauty", "Sports"],
        "price": [10.0, 20.0, 30.0],
        "cost": [5.0, 10.0, 15.0],
        "stock": [1, 2, 3],
    })

    report = validate_extracted_data(df, "products")

    assert report["dataset"] == "products"
    assert report["rows"] == 3
    assert report["columns"] == 6
    assert report["nulls"] == 0
    assert report["duplicates"] == 0
    assert report["completeness_pct"] == 100.0


def test_validate_extracted_data_report_counts_nulls_and_duplicates():

    df = pd.DataFrame({
        "product_id": [1, 2, 2],
        "product_name": ["A", "B", "B"],
        "category": ["Books", None, None],
        "price": [10.0, 20.0, 20.0],
        "cost": [5.0, 10.0, 10.0],
        "stock": [1, 2, 2],
    })

    report = validate_extracted_data(df, "products")

    assert report["rows"] == 3
    assert report["nulls"] == 2
    assert report["duplicates"] == 1
    assert report["completeness_pct"] < 100.0


def test_validate_extracted_data_handles_empty_dataframe():

    df = pd.DataFrame(columns=["product_id", "product_name"])

    report = validate_extracted_data(df, "products")

    assert report["rows"] == 0
    assert report["completeness_pct"] == 0.0



def test_read_csv_raises_file_not_found(tmp_path, monkeypatch):

    monkeypatch.setattr(extract, "RAW_DIR", tmp_path)

    with pytest.raises(FileNotFoundError):
        read_csv("nao_existe.csv", "customers")


def test_read_csv_raises_value_error_when_file_is_empty(tmp_path, monkeypatch):

    monkeypatch.setattr(extract, "RAW_DIR", tmp_path)

    empty_file = tmp_path / "customers.csv"
    empty_file.write_text(
        "customer_id,name,email,city,state,created_at\n"
    )

    with pytest.raises(ValueError):
        read_csv("customers.csv", "customers")


def test_read_csv_raises_value_error_when_schema_invalid(tmp_path, monkeypatch):

    monkeypatch.setattr(extract, "RAW_DIR", tmp_path)

    invalid_file = tmp_path / "customers.csv"
    invalid_file.write_text(
        "customer_id,name\n1,Cliente A\n"
    )

    with pytest.raises(ValueError, match="Schema inválido"):
        read_csv("customers.csv", "customers")


def test_read_csv_returns_dataframe_on_success(tmp_path, monkeypatch):

    monkeypatch.setattr(extract, "RAW_DIR", tmp_path)

    valid_file = tmp_path / "sellers.csv"
    valid_file.write_text(
        "seller_id,seller_name,city,state\n"
        "1,Vendedor A,Uberaba,MG\n"
        "2,Vendedor B,Sao Paulo,SP\n"
    )

    df = read_csv("sellers.csv", "sellers")

    assert len(df) == 2
    assert list(df.columns) == [
        "seller_id",
        "seller_name",
        "city",
        "state",
    ]



def _write_minimal_raw_files(raw_dir):
    """Cria os 6 CSVs mínimos e válidos exigidos por extract_data()."""

    (raw_dir / "customers.csv").write_text(
        "customer_id,name,email,city,state,created_at\n"
        "1,Cliente A,a@teste.com,Uberaba,MG,2024-01-01\n"
    )

    (raw_dir / "products.csv").write_text(
        "product_id,product_name,category,price,cost,stock\n"
        "1,Produto A,Books,10.0,5.0,100\n"
    )

    (raw_dir / "sellers.csv").write_text(
        "seller_id,seller_name,city,state\n"
        "1,Vendedor A,Uberaba,MG\n"
    )

    (raw_dir / "orders.csv").write_text(
        "order_id,customer_id,seller_id,order_date,status,"
        "payment_method,total_amount\n"
        "1,1,1,2024-01-01,completed,pix,100.0\n"
    )

    (raw_dir / "order_items.csv").write_text(
        "order_item_id,order_id,product_id,quantity,unit_price,discount\n"
        "1,1,1,2,10.0,0.0\n"
    )

    (raw_dir / "payments.csv").write_text(
        "payment_id,order_id,payment_date,amount,status\n"
        "1,1,2024-01-01,100.0,paid\n"
    )


def test_extract_data_reads_all_six_datasets(tmp_path, monkeypatch):

    monkeypatch.setattr(extract, "RAW_DIR", tmp_path)

    _write_minimal_raw_files(tmp_path)

    data = extract_data()

    assert set(data.keys()) == {
        "customers",
        "products",
        "sellers",
        "orders",
        "order_items",
        "payments",
    }

    for dataset_name, df in data.items():
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1


def test_extract_data_raises_if_one_file_is_missing(tmp_path, monkeypatch):

    monkeypatch.setattr(extract, "RAW_DIR", tmp_path)

    _write_minimal_raw_files(tmp_path)

    (tmp_path / "payments.csv").unlink()

    with pytest.raises(FileNotFoundError):
        extract_data()