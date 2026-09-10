import logging
import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

from src.extract import extract_data
from src.transform import transform_data, save_processed_data
from src.load import load_data
from src.validate import validate_database

logger = logging.getLogger(__name__)


def run_extract():
    extract_data()


def run_transform():
    data = extract_data()

    transformed_data = transform_data(data)

    save_processed_data(transformed_data)


def notify_failure(context: dict) -> None:
    """
    Callback executado automaticamente pelo Airflow sempre que uma task
    desta DAG falha (após esgotar as retries).

    Por padrão, só loga um alerta estruturado — que já aparece nos logs
    da task na UI do Airflow e pode ser coletado por qualquer sistema de
    observabilidade (Datadog, CloudWatch, etc.) sem configuração extra.

    Se a variável de ambiente ALERT_EMAIL estiver definida (e o SMTP do
    Airflow estiver configurado via AIRFLOW__SMTP__* no .env/compose),
    também tenta enviar um e-mail. O envio é best-effort: se falhar ou
    não estiver configurado, a task original continua marcada como
    failed normalmente — o alerta nunca derruba a DAG.
    """

    task_instance = context.get("task_instance")
    exception = context.get("exception")
    dag = context.get("dag")
    execution_date = context.get("logical_date") or context.get("execution_date")

    task_id = task_instance.task_id if task_instance else "desconhecida"
    dag_id = dag.dag_id if dag else "desconhecido"

    logger.error(
        "🚨 ALERTA: task '%s' do DAG '%s' falhou (execução: %s). Erro: %s",
        task_id,
        dag_id,
        execution_date,
        exception,
    )

    alert_email = os.environ.get("ALERT_EMAIL")

    if not alert_email:
        return

    try:
        from airflow.utils.email import send_email

        send_email(
            to=alert_email,
            subject=f"[Airflow] Falha em {dag_id}.{task_id}",
            html_content=(
                f"<p>A task <b>{task_id}</b> do DAG <b>{dag_id}</b> falhou "
                f"em {execution_date}.</p>"
                f"<p>Erro: {exception}</p>"
            ),
        )

    except Exception:
        # Falha ao enviar o alerta não deve afetar o resultado da task/DAG —
        # o alerta já foi registrado no log acima de qualquer forma.
        logger.exception(
            "Não foi possível enviar o e-mail de alerta para %s", alert_email
        )


default_args = {
    "on_failure_callback": notify_failure,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


with DAG(
    dag_id="ecommerce_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["ecommerce", "etl", "data-engineering"],
    default_args=default_args,
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