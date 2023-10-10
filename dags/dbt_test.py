from airflow.operators.email_operator import EmailOperator
from airflow.providers.amazon.aws.operators.glue import AwsGlueJobOperator
from datetime import datetime, timedelta


# glue job specific variables
glue_job_name = "my_glue_job"
glue_iam_role = "AWSGlueServiceRole"
region_name = "us-west-2"
email_recipient = "me@gmail.com"

default_args = {
    'owner': 'me',
    'start_date': datetime(2020, 1, 1),
    'retry_delay': timedelta(minutes=5),
    'tag': ["airflow_practice"]
}

with DAG(dag_id='dbt_test',
         default_args=default_args,
         schedule_interval=None) as dag:

    glue_job_step = AwsGlueJobOperator(
        task_id="glue_job",
        job_name=glue_job_name,
        job_desc=f"triggering glue job {glue_job_name}",
        region_name=region_name,
        iam_role_name=glue_iam_role,
        num_of_dpus=1,
        dag=dag
    )

    glue_job_step
