from airflow import DAG 
from datetime import datetime 
from airflow.operators.python import PythonOperator,BranchPythonOperator
from airflow.operators.bash import BashOperator
from random import randint


#aws blob variables

BlobEndpoint= 'https://jweirstorage.blob.core.windows.net/;QueueEndpoint=https://jweirstorage.queue.core.windows.net/;FileEndpoint=https://jweirstorage.file.core.windows.net/;TableEndpoint=https://jweirstorage.table.core.windows.net/;SharedAccessSignature=sv=2020-08-04&ss=bfqt&srt=sco&sp=rwdlacupitfx&se=2022-07-16T10:29:49Z&st=2022-05-16T02:29:49Z&spr=https&sig=zcEk3NZjs89O4LAx%2BDr%2BgNbQduq%2FxjelvczuKK1R2yE%3D'
sas_token ='?sv=2020-08-04&ss=bfqt&srt=sco&sp=rwdlacupitfx&se=2022-07-16T10:29:49Z&st=2022-05-16T02:29:49Z&spr=https&sig=zcEk3NZjs89O4LAx%2BDr%2BgNbQduq%2FxjelvczuKK1R2yE%3D'
s3_url = 's3://jweirtestbucket/OngoingData(excel_files)/'


def _training_model():
    return randint(1,10)

def _choose_best_model(ti):
    accuracies = ti.xcom_pull(task_ids=[
        'training_model_A',
        'training_model_B',
        'training_model_C',
    ])
    best_accuracy = max(accuracies)
    if (best_accuracy >8):
        return 'accurate'
    return 'inaccurate'    



with DAG("my_dag",start_date=datetime(2022,1,1),schedule_interval="@daily",catchup=False) as dag:

    training_model_A = PythonOperator(task_id="training_model_A",python_callable=_training_model)
    training_model_B = PythonOperator(task_id="training_model_B",python_callable=_training_model)
    training_model_C = PythonOperator(task_id="training_model_C",python_callable=_training_model)
    choose_best_model = BranchPythonOperator(task_id="choose_best_model",python_callable=_choose_best_model)
    accurate = BashOperator(task_id="accurate",bash_command="echo 'accurate'")
    inaccurate = BashOperator(task_id="inaccurate",bash_command="echo 'inaccurate'")

[training_model_A,training_model_B,training_model_C]    >> choose_best_model >> [accurate,inaccurate]