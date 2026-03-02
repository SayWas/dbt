from __future__ import annotations

import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

sys.path.append("/opt/airflow/jobs")

from run_dbt import run_dbt_build


default_args = {
    "owner": "data-platform",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="dbt_transformations_dag",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    tags=["airfares", "dbt", "transformations"],
) as dag:
    dbt_build_and_test = PythonOperator(
        task_id="dbt_build_and_test",
        python_callable=run_dbt_build,
    )

    trigger_elementary_report_dag = TriggerDagRunOperator(
        task_id="trigger_elementary_report_dag",
        trigger_dag_id="elementary_report_dag",
        wait_for_completion=False,
    )

    dbt_build_and_test >> trigger_elementary_report_dag
