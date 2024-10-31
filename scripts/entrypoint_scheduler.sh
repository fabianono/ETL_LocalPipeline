#!/bin/bash

set -e

if [ -e "/opt/airflow/docker_AirflowScheduler_requirements.txt" ]; then
    python3 -m pip install -r /opt/airflow/docker_AirflowScheduler_requirements.txt
fi

exec airflow scheduler