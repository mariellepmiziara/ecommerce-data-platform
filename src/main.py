import logging

# Configura o root logger ANTES de importar os módulos da pipeline,
# para que os `logger.info(...)` deles já saiam formatados desde a
# primeira linha. Rodar via Airflow não passa por este arquivo, então
# não há conflito com a configuração de logging do próprio Airflow.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

from src.extract import extract_data
from src.transform import transform_data, save_processed_data
from src.load import load_data
from src.validate import validate_database

logger = logging.getLogger(__name__)


def main():

    logger.info("🚀 E-COMMERCE DATA PLATFORM — iniciando pipeline")

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

        logger.info("🎉 PIPELINE EXECUTADO COM SUCESSO")

    except Exception:

        logger.exception("❌ PIPELINE FALHOU")

        raise


if __name__ == "__main__":

    main()