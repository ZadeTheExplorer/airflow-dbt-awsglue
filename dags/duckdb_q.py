import pandas as pd

from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from datetime import datetime

from duckdb_provider.hooks.duckdb_hook import DuckDBHook

default_args = {
    'owner': 'duckuser',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1
}

dag = DAG('duckdb_query', default_args=default_args, schedule_interval=None)

def _process_user(ti):
    """
    Use DuckDB to aggregate the data
    """
    hook = DuckDBHook.get_hook('ducktest1')
    conn = hook.get_conn()

    x = conn.execute('SELECT * FROM dbt.main."Telco-Customer-Churn"').df()
    print(x)
    print("DONE")



process_user = PythonOperator(
    dag=dag,
    task_id='process_user',
    python_callable=_process_user
)
