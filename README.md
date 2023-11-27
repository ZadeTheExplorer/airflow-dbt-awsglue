# airflow-dbt-awsglue
An airflow project with use DBT to transform data from AWS Glue

# Requirements:
1. Docker & Docker compose installment

# How to run:
1. run docker deamon `dockerd` or turn on docker desktop
2. `docker-compose build`
3. `docker-compose up`
4. Open Airflow web: http://localhost:8080
5. Login to airflow using Username and Password. As default, they both are `airflow`
6. Create new Airflow connection.
    - Choose `Duckdb` connection type
    - connection name `ducktest1` for examples

# Working on this projects:
Locate `dags` folder and start creating airflow dags python file under this section

## Enjoy developing guys :)