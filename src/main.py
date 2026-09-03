from src.extract import extract_data
from src.transform import transform_data, save_processed_data
from src.load import load_data
from src.validate import validate_database


def main():

    print("\n" + "=" * 70)
    print("🚀 E-COMMERCE DATA PLATFORM")
    print("=" * 70)

    try:

        # 1. EXTRACT
        extracted_data = extract_data()

        # 2. TRANSFORM
        transformed_data = transform_data(
            extracted_data
        )

        # 3. SAVE PROCESSED DATA
        save_processed_data(
            transformed_data
        )

        # 4. LOAD
        load_data()

        # 5. VALIDATE
        validate_database()

        print("\n" + "=" * 70)
        print("🎉 PIPELINE EXECUTADO COM SUCESSO")
        print("=" * 70)

    except Exception as error:

        print("\n" + "=" * 70)
        print("❌ PIPELINE FALHOU")
        print("=" * 70)

        print(f"Erro: {error}")

        raise


if __name__ == "__main__":

    main()