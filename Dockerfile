FROM python:3.7
RUN pip install 'apache-airflow[postgres]==2.2.0' && pip install dbt-postgres 
RUN apt-get install git -y

