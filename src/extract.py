from pathlib import Path 
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"

def validate_extracted_data(
        df: pd.DataFrame,
        dataset_name: str 
) -> None:
    total_records = len(df)
    total_columns = len(df.columns)

    duplicated_records = int(
        df.duplicated().sum()
    )

    null_records = int(
        df.isnull().sum().sum()
    )

    print("\n" + "-" * 60) 
    print(f"📊 DATASET: {dataset_name}") 
    print("-" * 60) 
    print( f"Registros : {total_records:,}" ) 
    print( f"Colunas : {total_columns}" ) 
    print( f"Nulos : {null_records:,}" ) 
    print( f"Duplicados: {duplicated_records:,}" ) 
    print("\nTipos de dados:") 
    print(df.dtypes)


def read_csv(
    filename: str,
) -> pd.DataFrame:
    file_path = RAW_DIR / filename

    try:
        if not file_path.exists():
            raise FileNotFoundError(
                f"Arquivo não encontrado: {file_path}"
            )

        df = pd.read_csv(file_path, encoding="utf-8")  # ← CORRIGIDO: utf-8

        print(f"✅ Extração realizada: {filename}")

        validate_extracted_data(df, filename)
        return df

    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {file_path}")
        raise

    except pd.errors.EmptyDataError:
        print(f"❌ Arquivo vazio: {filename}")
        raise

    except pd.errors.ParserError:
        print(f"❌ Erro ao interpretar CSV: {filename}")
        raise

    except Exception as error:
        print(f"❌ Erro inesperado ao ler {filename}: {error}")
        raise


def extract_data() -> dict[str, pd.DataFrame]:
    files = { "customers": "customers.csv", 
            "products": "products.csv", 
            "orders": "orders.csv", 
            "order_items": "order_items.csv", 
            "sellers": "sellers.csv", 
            "payments": "payments.csv", 
    }

    extracted_data = {}

    print("\n" + "=" * 60) 
    print("📥 ETAPA EXTRACT") 
    print("=" * 60) 

    for dataset_name, filename in files.items():
        extracted_data[dataset_name] = read_csv(filename
    )   

    print("\n" + "=" * 60) 
    print("✅ EXTRAÇÃO CONCLUÍDA") 
    print("=" * 60) 
    return extracted_data



if __name__ == "__main__":
    data = extract_data()
    print("\n📦 Datasets extraídos:")

    for name, df in data.items():
        print( 
            f" - {name}: " 
            f"{df.shape[0]:,} registros × " 
            f"{df.shape[1]} colunas"
        )