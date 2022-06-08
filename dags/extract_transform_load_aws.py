from airflow import DAG 
from datetime import datetime 
from airflow.operators.python import PythonOperator,BranchPythonOperator
from airflow.operators.bash import BashOperator
from random import randint
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import os

#Variables
s3_url = 's3://jweirtestbucket/OngoingData(excel_files)/'
file_in_s3 =  'Monthly Sales Report, Supplier filter only_Colgate 2019-12-30.xlsx'

# adding defined functions (will throw these into a container later)

def download_from_s3(key: str, bucket_name: str, local_path: str) -> str:
    hook = S3Hook('s3_conn')
    file_name = hook.download_file(key=key, bucket_name=bucket_name, local_path=local_path)
    return file_name

def rename_file(ti, new_name: str) -> None:
    downloaded_file_name = ti.xcom_pull(task_ids=['extract_transform_load_aws'])
    downloaded_file_path = '/'.join(downloaded_file_name[0].split('/')[:-1])
    os.rename(src=downloaded_file_name[0], dst=f"{downloaded_file_path}/{new_name}") 

with DAG("extract_transform_load_aws",start_date=datetime(2022,1,1),schedule_interval="@daily",catchup=False) as dag:

    extract_transform_load_aws = PythonOperator(
        task_id='extract_transform_load_aws',
        python_callable=download_from_s3,
        op_kwargs={
            'key': file_in_s3,
            'bucket_name': s3_url,
            'local_path': '/Users/jasonweir/airflow-docker/data/'
        }
    )

    task_rename_file = PythonOperator(
        task_id='rename_file',
        python_callable=rename_file,
        op_kwargs={
            'new_name': 'metcash_data.xls'
        }
    )

    task_download_from_s3 >> task_rename_file

    