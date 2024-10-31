#!/bin/bash

set -e


if [ ! -f "/opt/airflow/airflow.db" ]; then
    airflow db init && \
    airflow users create \
        --username admin \
        --firstname firstname \
        --lastname lastname \
        --role Admin \
        --email admin@admin.com \
        --password admin
fi

$(command -v airflow) db migrate

exec airflow webserver