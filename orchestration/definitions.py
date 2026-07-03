"""Dagster entry point: runs the dbt project on a daily schedule.

Local dev UI:  dagster dev -f orchestration/definitions.py
That opens a browser UI where you can see the schedule, trigger a manual
run, and watch dbt's own logs stream in per model.
"""
import sys
from pathlib import Path

from dagster import Definitions, ScheduleDefinition, define_asset_job
from dagster_dbt import DbtCliResource, DbtProject, dbt_assets

DBT_PROJECT_DIR = Path(__file__).parent.parent / "dbt"
# dbt is only installed inside this project's venv, not on the system PATH —
# resolve it next to whichever Python is currently running this file.
DBT_EXECUTABLE = Path(sys.executable).parent / "dbt"

dbt_project = DbtProject(project_dir=DBT_PROJECT_DIR)
dbt_project.prepare_if_dev()  # runs `dbt parse` once so Dagster can see the models


@dbt_assets(manifest=dbt_project.manifest_path)
def trendstamp_dbt_assets(context, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()


daily_job = define_asset_job(name="daily_trendstamp_analytics", selection="*")

daily_schedule = ScheduleDefinition(
    job=daily_job,
    cron_schedule="0 9 * * *",  # 9am every day, in whatever timezone this runs on
)

defs = Definitions(
    assets=[trendstamp_dbt_assets],
    schedules=[daily_schedule],
    resources={
        "dbt": DbtCliResource(project_dir=dbt_project, dbt_executable=str(DBT_EXECUTABLE))
    },
)
