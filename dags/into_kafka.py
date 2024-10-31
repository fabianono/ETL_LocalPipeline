from airflow.operators.bash import BashOperator
from airflow import DAG
from datetime import datetime, timedelta

default_args={
    'owner':'bryant',
    'retries':1,
    'retry_delay': timedelta(minutes=1)
}

starting_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

with DAG(
    default_args = default_args,
    dag_id = 'into_kafka',
    description = 'Weather API data stream into kafka.',
    start_date = starting_date,
    schedule_interval='*/5 * * * *',
    is_paused_upon_creation = False,
    catchup = False
) as dag:
    datastream = BashOperator(
        task_id='data-injest_kafka',
        bash_command="python3 /opt/airflow/main/kafkastream.py"
    )