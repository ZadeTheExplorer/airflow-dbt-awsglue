from datetime import datetime
from airflow import DAG
from ultils.dbt_task_generator import DbtTaskGenerator
import json


default_args = {
    'owner': 'duckuser',
    'depends_on_past': False,
    'start_date': datetime(2023, 12, 12),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1
}

dag = DAG('dbt_connected_task_creator_test_dag', default_args=default_args, schedule_interval=None)
manifest_file = open('./dbt/target/manifest.json', 'r')
manifest = json.loads(manifest_file.read())

dbt_task_generator = DbtTaskGenerator(dag, manifest)
dbt_task_generator.add_all_tasks()