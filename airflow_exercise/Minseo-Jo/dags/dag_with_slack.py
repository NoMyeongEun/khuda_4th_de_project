from datetime import timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.trigger_rule import TriggerRule
from airflow.providers.amazon.aws.hooks.s3 import S3Hook # 추가

import csv
import sys, os

sys.path.append("/home/ubuntu/airflow")
sys.path.append("/home/ubuntu/airflow/slack")

from slack_sdk import WebClient
from crawling.crawling_event import *
from crawling.crawling_velog import *
from crawling.crawling_contest_final import *
from slack_alert import SlackAlert

slack = SlackAlert('#khuda-4th-de', #발급된 토큰번호)

def upload_to_s3() :
    date = datetime.now().strftime("%Y%m%d")
    hook = S3Hook('airflow') # connection ID 입력

    event_filename = f'/home/ubuntu/airflow/airflow/data/event_{date}.csv'
    velog_filename = f'/home/ubuntu/airflow/airflow/data/velog_{date}.csv'
    contest_filename = f'/home/ubuntu/airflow/airflow/data/contest_{date}.csv'

    event_key = f'data/event_{date}.csv'
    velog_key = f'data/velog_{date}.csv'
    contest_key = f'data/contest_{date}.csv'

    bucket_name = 'airdnb'
    hook.load_file(filename=event_filename, key=event_key, bucket_name=bucket_name)
    hook.load_file(filename=velog_filename, key=velog_key, bucket_name=bucket_name)
    hook.load_file(filename=contest_filename, key=contest_key, bucket_name=bucket_name)

default_args = {
    'owner': 'owner-name',
    'depends_on_past': False,
    'email': ['your-email@g.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    ':retries': 1,
    'retry_delay': timedelta(minutes=30)
   # 'on_success_callback' : slack.notify_msg
}

dag_args = dict(
    dag_id="crawling-upload",
    default_args=default_args,
    description='KHUDA de-project DAG',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 11, 29),
    tags=['de-project'],
)

with DAG( **dag_args ) as dag:
    start = BashOperator(
        task_id='start',
        bash_command='echo "start"'
    )
    
    upload = PythonOperator(
        task_id = 'upload',
        python_callable = upload_to_s3,
        on_success_callback=slack.notify_msg
    )

    # -------- velog -------- #
    velog_get_url_task = PythonOperator(
        task_id='velog_get_url',
        python_callable= velog_get_url
    )

    velog_get_info_task= PythonOperator(
        task_id='velog_get_info',
        python_callable= velog_get_info
    )

    # -------- event -------- #
    event_get_data_task = PythonOperator(
        task_id="event_get_data",
        python_callable= event_get_data
    )

    # -------- contest -------- #
    contest_task = PythonOperator(
        task_id='contest_crawling',
        python_callable=contest_crawling
    )

    complete = BashOperator(
        task_id='complete_bash',
        bash_command='echo "complete"'
    )

    start >> event_get_data_task >> upload >> complete
    start >> velog_get_url_task >> velog_get_info_task >> upload >> complete
    start >> contest_task >> upload >> complete 
