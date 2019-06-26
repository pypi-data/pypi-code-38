
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime,timedelta
from zlhawq.api import add_quyu1_sheng


tag='all'


default_args = {'owner': 'root',
                'depends_on_past': False,
                'start_date': datetime(2019,4,27), }

d = DAG('abc_zzz_ggzy_flush'
        , default_args=default_args
        , schedule_interval="0 6 1/10 * *"
        ,max_active_runs=1) 

t0=PythonOperator(task_id="abc_zzz_ggzy_anhui"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'anhui','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t1=PythonOperator(task_id="abc_zzz_ggzy_chongqing"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'chongqing','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t2=PythonOperator(task_id="abc_zzz_ggzy_fujian"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'fujian','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t3=PythonOperator(task_id="abc_zzz_ggzy_gansu"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'gansu','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t4=PythonOperator(task_id="abc_zzz_ggzy_guangdong"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'guangdong','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t5=PythonOperator(task_id="abc_zzz_ggzy_guangxi"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'guangxi','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t6=PythonOperator(task_id="abc_zzz_ggzy_guizhou"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'guizhou','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t7=PythonOperator(task_id="abc_zzz_ggzy_hainan"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'hainan','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t8=PythonOperator(task_id="abc_zzz_ggzy_hebei"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'hebei','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t9=PythonOperator(task_id="abc_zzz_ggzy_heilongjiang"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'heilongjiang','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t10=PythonOperator(task_id="abc_zzz_ggzy_henan"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'henan','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t11=PythonOperator(task_id="abc_zzz_ggzy_hubei"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'hubei','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t12=PythonOperator(task_id="abc_zzz_ggzy_hunan"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'hunan','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t13=PythonOperator(task_id="abc_zzz_ggzy_jiangsu"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'jiangsu','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t14=PythonOperator(task_id="abc_zzz_ggzy_jiangxi"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'jiangxi','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t15=PythonOperator(task_id="abc_zzz_ggzy_jilin"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'jilin','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t16=PythonOperator(task_id="abc_zzz_ggzy_liaoning"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'liaoning','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t17=PythonOperator(task_id="abc_zzz_ggzy_neimenggu"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'neimenggu','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t18=PythonOperator(task_id="abc_zzz_ggzy_ningxia"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'ningxia','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t19=PythonOperator(task_id="abc_zzz_ggzy_qinghai"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'qinghai','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t20=PythonOperator(task_id="abc_zzz_ggzy_shandong"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'shandong','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t21=PythonOperator(task_id="abc_zzz_ggzy_shanxi"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'shanxi','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t22=PythonOperator(task_id="abc_zzz_ggzy_shanxi1"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'shanxi1','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t23=PythonOperator(task_id="abc_zzz_ggzy_sichuan"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'sichuan','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t24=PythonOperator(task_id="abc_zzz_ggzy_xinjiang"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'xinjiang','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t25=PythonOperator(task_id="abc_zzz_ggzy_xizang"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'xizang','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t26=PythonOperator(task_id="abc_zzz_ggzy_yunnan"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'yunnan','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t27=PythonOperator(task_id="abc_zzz_ggzy_zhejiang"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'zhejiang','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    
t0>>t1>>t2>>t3>>t4>>t5>>t6>>t7>>t8>>t9>>t10>>t11>>t12>>t13>>t14>>t15>>t16>>t17>>t18>>t19>>t20>>t21>>t22>>t23>>t24>>t25>>t26>>t27