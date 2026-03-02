from __future__ import annotations

import os
import subprocess


def run_dbt_build(select: str = "tag:stg tag:ods tag:dwh tag:dm") -> None:
    project_dir = os.getenv("DBT_PROJECT_DIR", "/opt/airflow/dbt")
    profiles_dir = os.getenv("DBT_PROFILES_DIR", "/opt/airflow/dbt_profiles")
    base_cmd = ["--project-dir", project_dir, "--profiles-dir", profiles_dir]

    # Refresh package dependencies before each dbt execution in Airflow workers.
    subprocess.run(["dbt", "deps", *base_cmd], check=True)
    subprocess.run(["dbt", "run", *base_cmd, "--select", select], check=True)
    # Elementary own models are required for anomaly monitoring artifacts.
    subprocess.run(["dbt", "run", *base_cmd, "--select", "elementary"], check=True)
    subprocess.run(["dbt", "test", *base_cmd, "--select", select], check=True)


def run_elementary_report() -> None:
    project_dir = os.getenv("DBT_PROJECT_DIR", "/opt/airflow/dbt")
    profiles_dir = os.getenv("DBT_PROFILES_DIR", "/opt/airflow/dbt_profiles")
    report_path = os.getenv("ELEMENTARY_REPORT_FILE_PATH", "/opt/airflow/reports/elementary_report.html")
    target_path = os.getenv("ELEMENTARY_TARGET_PATH", "/opt/airflow/reports")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    cmd = [
        "edr",
        "report",
        "--file-path",
        report_path,
        "--target-path",
        target_path,
        "--project-dir",
        project_dir,
        "--profiles-dir",
        profiles_dir,
        "--project-profile-target",
        "dev",
        "--env",
        os.getenv("APP_ENV", "dev"),
    ]
    subprocess.run(cmd, check=True)
