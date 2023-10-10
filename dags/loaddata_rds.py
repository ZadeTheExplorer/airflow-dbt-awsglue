from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from airflow.utils.dates import timedelta, datetime


default_args = {
    'owner': 'me',
    'start_date': datetime(2020, 1, 1),
    'retry_delay': timedelta(minutes=5),
    'tag': ["airflow_practice"]
}


def _store_user():
    hook = PostgresHook(postgres_conn_id='psql_aws')
    hook.copy_expert(
        sql="COPY users FROM stdin WITH DELIMITER as ','",
        filename='/opt/airflow/dags/Telco-Customer-Churn.csv'
    )

with DAG('loaddata_rds',
         default_args=default_args,
         schedule_interval=None) as dag:

    create_table = PostgresOperator(
        task_id='create_table',
        postgres_conn_id='psql_aws',
        sql='''
            CREATE TABLE IF NOT EXISTS users (
                customerID TEXT NOT NULL,
                gender TEXT NOT NULL,
                SeniorCitizen TEXT NOT NULL,
                Partner TEXT NOT NULL,
                Dependents TEXT NOT NULL,
                tenure TEXT NOT NULL,
                PhoneService TEXT NOT NULL,
                MultipleLines TEXT NOT NULL,
                InternetService TEXT NOT NULL,
                OnlineSecurity TEXT NOT NULL,
                OnlineBackup TEXT NOT NULL,
                DeviceProtection TEXT NOT NULL,
                TechSupport TEXT NOT NULL,
                StreamingTV TEXT NOT NULL,
                StreamingMovies TEXT NOT NULL,
                Contract TEXT NOT NULL,
                PaperlessBilling TEXT NOT NULL,
                PaymentMethod TEXT NOT NULL,
                MonthlyCharges TEXT NOT NULL,
                TotalCharges TEXT NOT NULL,
                Churn TEXT NOT NULL)
        '''
    )


    load_csv = PythonOperator(
        task_id='load_csv',
        python_callable=_store_user
    )

    create_table  >>  load_csv