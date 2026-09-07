from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from datetime import datetime

with DAG("retail_pipeline", start_date=datetime(2024,1,1), schedule_interval=None, catchup=False) as dag:

    run_sp = BigQueryInsertJobOperator(
        task_id="run_stored_procedure",
        configuration={
            "query": {
                "query": "CALL retail_dataset.sp_clean_orders();",
                "useLegacySql": False,
            }
        }
    )

    run_sp