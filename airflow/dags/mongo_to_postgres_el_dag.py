from __future__ import annotations

import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

sys.path.append("/opt/airflow/jobs")

from el_mongo_to_postgres import run_el_mongo_to_postgres


default_args = {
    "owner": "data-platform",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="mongo_to_postgres_el_dag",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    tags=["airfares", "el", "postgres"],
) as dag:
    el_mongo_to_postgres = PythonOperator(
        task_id="el_mongo_to_postgres",
        python_callable=run_el_mongo_to_postgres,
    )

    trigger_dbt_dag = TriggerDagRunOperator(
        task_id="trigger_dbt_dag",
        trigger_dag_id="dbt_transformations_dag",
        wait_for_completion=False,
    )

    el_mongo_to_postgres >> trigger_dbt_dag
