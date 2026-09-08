from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.google.cloud.sensors.gcs import GCSObjectsWithPrefixExistenceSensor
from airflow.providers.google.cloud.operators.dataflow import DataflowCreatePythonJobOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.utils.trigger_rule import TriggerRule

PROJECT_ID = "project-d0445eef-b5cb-453b-a9a"
REGION = "us-central1"
BUCKET = "us-central1-airflow3-cc018626-bucket"

default_args = {
    "retries": 2,
    "retry_delay": 300,  # 5 min
}

with DAG(
    dag_id="retail_prod_pipeline",
    start_date=days_ago(1),
    schedule="0 10 * * *",
    catchup=False,
    default_args=default_args,
    tags=["retail", "dataflow", "bq"]
) as dag:

    # 🔍 1. Wait for file in GCS
    wait_for_file = GCSObjectsWithPrefixExistenceSensor(
        task_id="wait_for_gcs_file",
        bucket=BUCKET,
        prefix="input/",   # 👈 your incoming data folder
        poke_interval=60,
        timeout=600,
        mode="poke"
    )

    # 🚀 2. Run Dataflow
    run_dataflow = DataflowCreatePythonJobOperator(
        task_id="run_dataflow",
        py_file=f"gs://{BUCKET}/dataflow/job.py",
        location=REGION,
        project_id=PROJECT_ID,
        options={
            "temp_location": f"gs://{BUCKET}/temp",
        }
    )

    # 🧠 3. Run Stored Procedure
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

    # ❌ 4. Failure handler (optional but powerful)
    fail_task = BigQueryInsertJobOperator(
        task_id="on_failure_log",
        configuration={
            "query": {
                "query": """
                INSERT INTO `retail_dataset.pipeline_logs`
                VALUES(CURRENT_TIMESTAMP(), 'FAILED')
                """,
                "useLegacySql": False,
            }
        },
        trigger_rule=TriggerRule.ONE_FAILED,
        location=REGION,
    )

    # 🔗 Pipeline flow
    wait_for_file >> run_dataflow >> run_sp
    [wait_for_file, run_dataflow, run_sp] >> fail_task