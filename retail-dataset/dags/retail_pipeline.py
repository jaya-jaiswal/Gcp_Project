from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.google.cloud.operators.dataflow import DataflowStartFlexTemplateOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator

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
) as dag:

    # 🚀 Dataflow via Flex Template (modern way)
    run_dataflow = DataflowStartFlexTemplateOperator(
        task_id="run_dataflow",
        body={
            "launchParameter": {
                "jobName": "retail-dataflow-job",
                "containerSpecGcsPath": "gs://dataflow-templates-us-central1/latest/flex/Word_Count",
                "parameters": {
                    "inputFile": "gs://dataflow-samples/shakespeare/kinglear.txt",
                    "output": "gs://us-central1-airflow3-cc018626-bucket/output/result"
                }
            }
        },
        location=REGION,
        project_id=PROJECT_ID,
    )

    # 🧠 Stored Procedure
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