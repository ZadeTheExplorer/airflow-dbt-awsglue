FROM apache/airflow:2.7.3
USER root
RUN apt-get update -y \
    && apt-get install git -y
COPY requirements.txt /
# AWS CLI installation
# RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
# RUN unzip awscliv2.zip && ./aws/install

USER airflow
# Required package installation
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /requirements.txt