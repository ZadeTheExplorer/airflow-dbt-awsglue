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

dag = DAG('dbt_transform', default_args=default_args, schedule_interval=None)



def aggregate() -> pd.DataFrame:
    """
    Use DuckDB to aggregate the data111
    """
    hook = DuckDBHook.get_hook('ducktest1')
    conn = hook.get_conn()

    # aggregate
    return conn.execute("SELECT * FROM dbt.main.d_usersname").df()

def _process_user(ti):
    aggregate_res = aggregate()
    print(aggregate_res)
    print("DONE")


task_3 = BashOperator(
    task_id='check_dbt_debug',
    bash_command='dbt debug --project-dir /opt/airflow/dbt --profiles-dir /opt/airflow/dbt',
    # bash_command='cat /opt/airflow/dbt/logs/dbt.log',
    dag=dag,
)

task_4 = BashOperator(
    task_id='dbt_run',
    bash_command='dbt run --select d_usersname --project-dir /opt/airflow/dbt --profiles-dir /opt/airflow/dbt',
    # bash_command='cat /opt/airflow/dbt/logs/dbt.log',
    dag=dag,
)

process_user = PythonOperator(
    dag=dag,
    task_id='process_user',
    python_callable=_process_user
)

end_task = DummyOperator(task_id='end_task', dag=dag)

task_3 >> task_4 >> process_user