from __future__ import annotations

import os
from datetime import datetime, timedelta

import httpx

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator


def trigger_price_generation() -> None:
    app_host = os.getenv("APP_INTERNAL_HOST", "app")
    app_port = os.getenv("APP_PORT", "8000")
    url = f"http://{app_host}:{app_port}/api/v1/prices/generate"
    payload = {"days_ahead": 60}
    response = httpx.post(url, json=payload, timeout=30)
    response.raise_for_status()


default_args = {
    "owner": "data-platform",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="flight_price_generate_dag",
    start_date=datetime(2025, 1, 1),
    schedule_interval="0 */6 * * *",
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    tags=["airfares", "generate", "mongo"],
) as dag:
    generate_prices = PythonOperator(
        task_id="generate_prices",
        python_callable=trigger_price_generation,
    )

    trigger_el_dag = TriggerDagRunOperator(
        task_id="trigger_el_dag",
        trigger_dag_id="mongo_to_postgres_el_dag",
        wait_for_completion=False,
    )

    generate_prices >> trigger_el_dag
