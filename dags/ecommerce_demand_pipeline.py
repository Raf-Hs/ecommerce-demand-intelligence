"""Airflow DAG orchestrating the ecommerce demand intelligence pipeline."""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def run_ingestion():
    import sys
    sys.path.insert(0, "/opt/airflow/project")
    from scripts.run_ingestion import main
    main()


def run_silver():
    import sys
    sys.path.insert(0, "/opt/airflow/project")
    from src.transformation.silver import build_all
    build_all()


def run_gold():
    import sys
    sys.path.insert(0, "/opt/airflow/project")
    from src.transformation.gold import build_all
    build_all()


def run_synthetic():
    import sys
    sys.path.insert(0, "/opt/airflow/project")
    from src.transformation.synthetic_inventory import generate
    generate()


with DAG(
    dag_id="ecommerce_demand_intelligence",
    default_args=default_args,
    description="End-to-end demand intelligence pipeline (Bronze -> Silver -> Gold)",
    schedule_interval="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["ecommerce", "demand", "inventory"],
) as dag:

    ingestion = PythonOperator(task_id="ingest_sources", python_callable=run_ingestion)
    silver = PythonOperator(task_id="build_silver", python_callable=run_silver)
    gold = PythonOperator(task_id="build_gold", python_callable=run_gold)
    synthetic = PythonOperator(task_id="generate_synthetic_ops", python_callable=run_synthetic)

    ingestion >> silver >> [gold, synthetic]
