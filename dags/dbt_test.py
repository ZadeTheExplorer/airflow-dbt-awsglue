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

dag = DAG('dummy_operator_example', default_args=default_args, schedule_interval=None)

def create_df() -> pd.DataFrame:
    """
    Create a dataframe with some sample data
    """
    df = pd.DataFrame(
        {
            "a": [1, 2, 3],
            "b": [4, 5, 6],
            "c": [7, 8, 9],
        }
    )
    print(df)
    return df


def simple_select(df: pd.DataFrame) -> pd.DataFrame:
    """
    Use DuckDB to select a subset of the data
    """
    hook = DuckDBHook.get_hook('ducktest1')
    conn = hook.get_conn()

    # execute a simple query
    res = conn.execute("SELECT a, b, c FROM df WHERE a >= 2").df()
    print("simple select")
    return res


def add_col(df: pd.DataFrame) -> pd.DataFrame:
    """
    Use DuckDB to add a column to the data
    """
    hook = DuckDBHook.get_hook('ducktest1')
    conn = hook.get_conn()

    # add a column
    conn.execute("CREATE TABLE IF NOT EXISTS tb AS SELECT *, a + b AS d FROM df")

    # get the table
    return conn.execute("SELECT * FROM tb").df()


def aggregate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Use DuckDB to aggregate the data
    """
    hook = DuckDBHook.get_hook('ducktest1')
    conn = hook.get_conn()

    # aggregate
    return conn.execute("SELECT SUM(a), COUNT(b) FROM df").df()

def _process_user(ti):
    create_df_res = create_df()
    simple_select_res = simple_select(create_df_res)
    add_col_res = add_col(simple_select_res)
    aggregate_res = aggregate(add_col_res)
    print(aggregate_res)
    print("DONE")


start_task = DummyOperator(task_id='start_task', dag=dag)

task_2 = BashOperator(
    task_id='check_dbt_version',
    bash_command='dbt --version',
    dag=dag,
)
task_3 = BashOperator(
    task_id='check_dbt_debug',
    bash_command='dbt debug --project-dir /opt/airflow/dbt --profiles-dir /opt/airflow/dbt',
    # bash_command='cat /opt/airflow/dbt/logs/dbt.log',
    dag=dag,
)

task_4 = BashOperator(
    task_id='dbt_seeds',
    bash_command='dbt seed --project-dir /opt/airflow/dbt --profiles-dir /opt/airflow/dbt',
    # bash_command='cat /opt/airflow/dbt/logs/dbt.log',
    dag=dag,
)

process_user = PythonOperator(
    dag=dag,
    task_id='process_user',
    python_callable=_process_user
)

end_task = DummyOperator(task_id='end_task', dag=dag)

start_task >> process_user >> end_task
start_task >> task_2 >> task_3 >> task_4