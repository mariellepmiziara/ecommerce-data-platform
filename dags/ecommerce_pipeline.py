from datetime import datetime
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from src.extract import extract_data
from src.transform import transform_data, save_processed_data
from src.load import load_data
from src.validate import validate_database


def run_extract():
    extract_data()


def run_transform():
    data = extract_data()

    transformed_data = transform_data(data)

    save_processed_data(transformed_data)


with DAG(
    dag_id="ecommerce_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["ecommerce", "etl", "data-engineering"],
) as dag:

    extract = PythonOperator(
        task_id="extract",
        python_callable=run_extract,
    )

    transform = PythonOperator(
        task_id="transform",
        python_callable=run_transform,
    )

    load = PythonOperator(
        task_id="load",
        python_callable=load_data,
    )

    validate = PythonOperator(
        task_id="validate",
        python_callable=validate_database,
    )

    extract >> transform >> load >> validate