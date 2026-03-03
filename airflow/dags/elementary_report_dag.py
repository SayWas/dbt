from __future__ import annotations

import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

sys.path.append("/opt/airflow/jobs")

from run_dbt import run_elementary_report

default_args = {
    "owner": "data-platform",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="elementary_report_dag",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    tags=["airfares", "elementary", "report"],
) as dag:
    generate_elementary_report = PythonOperator(
        task_id="generate_elementary_report",
        python_callable=run_elementary_report,
    )
