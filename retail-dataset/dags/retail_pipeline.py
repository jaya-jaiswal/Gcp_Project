from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.google.cloud.operators.dataflow import DataflowTemplatedJobStartOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from datetime import datetime

PROJECT_ID = "project-d0445eef-b5cb-453b-a9a"
REGION = "us-central1"

default_args = {
    "retries": 2,
}

with DAG(
    dag_id="retail_prod_pipeline_v2",
    start_date=days_ago(1),
    schedule="0 10 * * *",
    catchup=False,
    default_args=default_args,
) as dag:

    run_dataflow = DataflowTemplatedJobStartOperator(
    task_id="run_dataflow",
    template="gs://dataflow-templates-us-central1/latest/GCS_Text_to_BigQuery",
    parameters={
        "inputFilePattern": "gs://project-d0445eef-b5cb-453b-a9a-landing-bucket/*.csv",
        "outputTable": f"{PROJECT_ID}:retail_dataset.raw_orders",
        "schemaJSONPath": "gs://project-d0445eef-b5cb-453b-a9a-landing-bucket/schema.json",
        "bigQueryLoadingTemporaryDirectory": "gs://us-central1-airflow3-cc018626-bucket/temp",
        "writeDisposition": "WRITE_APPEND"
    },
    location=REGION,
    project_id=PROJECT_ID,
    environment={
        "serviceAccountEmail": "dataflow-sa@project-d0445eef-b5cb-453b-a9a.iam.gserviceaccount.com",
        "tempLocation": "gs://us-central1-airflow3-cc018626-bucket/temp",
        "stagingLocation": "gs://us-central1-airflow3-cc018626-bucket/staging"
    }
)

    run_sp = BigQueryInsertJobOperator(
        task_id="run_sp",
        configuration={
            "query": {
                "query": "CALL `retail_dataset.sp_clean_orders`()",
                "useLegacySql": False,
            }
        },
        location=REGION,
    )

    run_dataflow >> run_sp