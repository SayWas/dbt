from __future__ import annotations

import os
import shutil
import subprocess


def _resolve_executable(executable_name: str) -> str:
    executable = shutil.which(executable_name)
    if not executable:
        msg = f"Required executable not found in PATH: {executable_name}"
        raise RuntimeError(msg)
    return executable


def _run_checked(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)  # noqa: S603


def run_dbt_build(select: str = "tag:stg tag:ods tag:dwh tag:dm") -> None:
    project_dir = os.getenv("DBT_PROJECT_DIR", "/opt/airflow/dbt")
    profiles_dir = os.getenv("DBT_PROFILES_DIR", "/opt/airflow/dbt_profiles")
    dbt_bin = _resolve_executable("dbt")
    base_cmd = ["--project-dir", project_dir, "--profiles-dir", profiles_dir]

    # Refresh package dependencies before each dbt execution in Airflow workers.
    _run_checked([dbt_bin, "deps", *base_cmd])
    _run_checked([dbt_bin, "run", *base_cmd, "--select", select])
    # Elementary own models are required for anomaly monitoring artifacts.
    _run_checked([dbt_bin, "run", *base_cmd, "--select", "elementary"])
    _run_checked([dbt_bin, "test", *base_cmd, "--select", select])


def run_elementary_report() -> None:
    project_dir = os.getenv("DBT_PROJECT_DIR", "/opt/airflow/dbt")
    profiles_dir = os.getenv("DBT_PROFILES_DIR", "/opt/airflow/dbt_profiles")
    report_path = os.getenv(
        "ELEMENTARY_REPORT_FILE_PATH",
        "/opt/airflow/reports/elementary_report.html",
    )
    target_path = os.getenv("ELEMENTARY_TARGET_PATH", "/opt/airflow/reports")
    edr_bin = _resolve_executable("edr")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    cmd = [
        edr_bin,
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
    _run_checked(cmd)
