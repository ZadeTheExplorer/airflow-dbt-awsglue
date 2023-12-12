import pandas as pd
import duckdb
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

def _exec_query(ti):
    """
    Use DuckDB to aggregate the data
    """
    # hook = DuckDBHook.get_hook('motherducktest')
    # conn = hook.get_conn()

    # # x = conn.execute('select * from my_db.main.hacker_news limit 100').df()
    # x = conn.execute('select 1').df()
    # print(x)
    # print("DONE")

    # initiate the MotherDuck connection through a service token through
    con = duckdb.connect('md:my_db?motherduck_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXNzaW9uIjoiaGF0cmlzeS5nbWFpbC5jb20iLCJlbWFpbCI6ImhhdHJpc3lAZ21haWwuY29tIiwidXNlcklkIjoiZDZhNWIzODYtOWRlZC00OWMxLTg1MzctMjBiMjUxMTc2MTgyIiwiaWF0IjoxNzAxMjE2MDg3LCJleHAiOjE3MzI3NzM2ODd9.CLcOUKJ5FA3ZjSP_6euRTv5lmVfHEyyL2Xs5a--jzq8') 

    # connect to your MotherDuck database through 'md:mydatabase' or 'motherduck:mydatabase'
    # if the database doesn't exist, MotherDuck creates it when you connect
    # con = duckdb.connect('md:mydatabase')

    # run a query to check verify that you are connected
    con.sql("Select * from main.hacker_news limit 10;").show()



process_user = PythonOperator(
    dag=dag,
    task_id='exec_query',
    python_callable=_exec_query
)
