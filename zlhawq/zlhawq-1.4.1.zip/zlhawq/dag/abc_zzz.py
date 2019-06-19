
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime,timedelta
from zlhawq.api import add_quyu2_sheng


tag='all'


default_args = {'owner': 'root',
                'depends_on_past': False,
                'start_date': datetime(2019,6,18), }

d = DAG('zzz_flush'
        , default_args=default_args
        , schedule_interval="0 0 1/10 * *"
        ,max_active_runs=1) 

t0=PythonOperator(task_id="zzz_zfcg"
                ,python_callable=add_quyu2_sheng
                ,op_kwargs={'sheng':'zfcg','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t1=PythonOperator(task_id="zzz_gcjs"
                ,python_callable=add_quyu2_sheng
                ,op_kwargs={'sheng':'gcjs','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t2=PythonOperator(task_id="zzz_qycg"
                ,python_callable=add_quyu2_sheng
                ,op_kwargs={'sheng':'qycg','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 




    
t0>>t1>>t2