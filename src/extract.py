import logging
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"


# CONTRATO DOS DATASETS

REQUIRED_COLUMNS = {
    "customers": [
        "customer_id",
        "name",
        "email",
        "city",
        "state",
        "created_at",
    ],
    "products": [
        "product_id",
        "product_name",
        "category",
        "price",
        "cost",
        "stock",
    ],
    "sellers": [
        "seller_id",
        "seller_name",
        "city",
        "state",
    ],
    "orders": [
        "order_id",
        "customer_id",
        "seller_id",
        "order_date",
        "status",
        "payment_method",
        "total_amount",
    ],
    "order_items": [
        "order_item_id",
        "order_id",
        "product_id",
        "quantity",
        "unit_price",
        "discount",
    ],
    "payments": [
        "payment_id",
        "order_id",
        "payment_date",
        "amount",
        "status",
    ],
}


# VALIDAÇÃO DE SCHEMA

def validate_schema(
    df: pd.DataFrame,
    dataset_name: str,
) -> None:

    required_columns = REQUIRED_COLUMNS[dataset_name]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"❌ Schema inválido para '{dataset_name}'. "
            f"Colunas ausentes: {missing_columns}"
        )



def validate_extracted_data(
    df: pd.DataFrame,
    dataset_name: str,
) -> dict:
    """
    Gera um relatório inicial de qualidade do dataset.
    """

    total_records = len(df)
    total_columns = len(df.columns)

    duplicated_records = int(df.duplicated().sum())
    null_records = int(df.isnull().sum().sum())

    if total_records > 0:
        completeness = (
            (1 - df.isnull().sum() / total_records) * 100
        ).mean()
    else:
        completeness = 0.0

    logger.info(
        "📊 DATASET %s | registros=%s colunas=%s nulos=%s "
        "duplicados=%s completude_media=%.2f%%",
        dataset_name,
        f"{total_records:,}",
        total_columns,
        f"{null_records:,}",
        f"{duplicated_records:,}",
        completeness,
    )

    logger.debug("Tipos de dados de %s:\n%s", dataset_name, df.dtypes)

    return {
        "dataset": dataset_name,
        "rows": total_records,
        "columns": total_columns,
        "nulls": null_records,
        "duplicates": duplicated_records,
        "completeness_pct": round(completeness, 2),
    }



def read_csv(filename: str, dataset_name: str) -> pd.DataFrame:
    """
    Lê um arquivo CSV da camada raw.
    """

    file_path = RAW_DIR / filename

    try:
        if not file_path.exists():
            raise FileNotFoundError(
                f"Arquivo não encontrado: {file_path}"
            )

        df = pd.read_csv(
            file_path,
            encoding="utf-8",
        )

        if df.empty:
            raise ValueError(
                f"O arquivo '{filename}' está vazio."
            )

        validate_schema(df, dataset_name)

        logger.info("✅ Extração realizada: %s", filename)

        validate_extracted_data(
            df,
            dataset_name,
        )

        return df

    except FileNotFoundError:
        logger.error("❌ Arquivo não encontrado: %s", file_path)
        raise

    except pd.errors.EmptyDataError:
        logger.error("❌ Arquivo vazio: %s", filename)
        raise

    except pd.errors.ParserError:
        logger.error("❌ Erro ao interpretar CSV: %s", filename)
        raise

    except Exception as error:
        logger.error("❌ Erro ao ler '%s': %s", filename, error)
        raise



def extract_data() -> dict[str, pd.DataFrame]:
    """
    Extrai todos os datasets da camada raw.
    """

    files = {
        "customers": "customers.csv",
        "products": "products.csv",
        "orders": "orders.csv",
        "order_items": "order_items.csv",
        "sellers": "sellers.csv",
        "payments": "payments.csv",
    }

    extracted_data = {}

    logger.info("📥 ETAPA EXTRACT — iniciando")

    for dataset_name, filename in files.items():

        extracted_data[dataset_name] = read_csv(
            filename,
            dataset_name,
        )

    logger.info("✅ EXTRAÇÃO CONCLUÍDA")

    return extracted_data



if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    data = extract_data()

    logger.info("📦 Datasets extraídos:")

    for name, df in data.items():

        logger.info(
            " - %s: %s registros × %s colunas",
            name,
            f"{df.shape[0]:,}",
            df.shape[1],
        )