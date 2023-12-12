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

USER root
RUN apt-get install unzip

RUN curl -SL https://ext.motherduck.com/linux_arm64_gcc4/duckdb_0.9.2_linux_arm64_gcc4_extensions.zip -o duckdb.zip
RUN mkdir -p /home/airflow/.duckdb/extensions/v0.9.2/linux_arm64_gcc4 \
    && unzip duckdb.zip -d /home/airflow/.duckdb/extensions/v0.9.2/linux_arm64_gcc4/
RUN chmod -R a+rwx /home/airflow/.duckdb/extensions/v0.9.2/linux_arm64_gcc4/
# RUN mkdir -p /temp/duckdb/extensions \
#     && cd /temp/duckdb/extensions \
#     && curl -SL https://ext.motherduck.com/linux_arm64_gcc4/duckdb_0.9.2_linux_arm64_gcc4_extensions.zip \
#     | tar -xJC /temp/duckdb/extensions \
#     && make -C /temp/duckdb/extensions all