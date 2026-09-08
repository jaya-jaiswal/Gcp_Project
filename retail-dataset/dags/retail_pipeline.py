from airflow import DAG
from airflow.providers.google.cloud.operators.dataflow import DataflowCreatePythonJobOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from datetime import datetime

PROJECT_ID = "project-d0445eef-b5cb-453b-a9a"
REGION = "us-central1"
BUCKET = "us-central1-airflow3-cc018626-bucket"

with DAG(
    dag_id="retail_end_to_end_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule="0 10 * * *",
    catchup=False
) as dag:

    # 🚀 1. Dataflow Job
    run_dataflow = DataflowCreatePythonJobOperator(
        task_id="run_dataflow",
        py_file=f"gs://{BUCKET}/dataflow/job.py",
        location=REGION,
        project_id=PROJECT_ID,
        options={
            "temp_location": f"gs://{BUCKET}/temp",
        }
    )

    # 🧠 2. Run Stored Procedure
    run_sp = BigQueryInsertJobOperator(
        task_id="run_stored_procedure",
        configuration={
            "query": {
                "query": "CALL `retail_dataset.sp_clean_orders`()",
                "useLegacySql": False,
            }
        },
        location=REGION,
    )

    # 🔗 Dependency
    run_dataflow >> run_sp