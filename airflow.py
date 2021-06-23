from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator


import pandas as pd
import numpy as np
import json
import time
from google_currency import convert 
import warnings
warnings.filterwarnings('ignore')
from functions import *

extract_data()

transform_data()

default_args = {
    'owner': 'mikel',
    'depends_on_past': False,
    'start_date': datetime(2021, 6, 23),
    'email': ['mikelvallejo9@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'email_on_success': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    'chameleon_pricing',
    description='Price recommender system',
    schedule_interval='0 8 * * *',   # cada 1 minuto día a las 8
    default_args=default_args,
    catchup=False,
)

tarea1=PythonOperator(task_id='extract_data', python_callable=extract_data, dag=dag)

tarea2=PythonOperator(task_id='transform_data', python_callable=transform_data, dag=dag)

# secuencia de tareas
tarea1 >> tarea2