from zlhawq.data import zhulong_diqu_dict
import sys 
import os
def write_dag(dirname,**krg):
    
    para={

    "start_date":"(2019,6,20)",
    "cron":"0 5 * * *",

    }
    para.update(krg)

    start_date=para["start_date"]

    cron=para["cron"]

    part1="""
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime,timedelta
from zlhawq.m_gg.api import add_quyus_sheng




default_args = {'owner': 'root',
                'depends_on_past': False,
                'start_date': datetime%s, }

d = DAG('m_gg_add_quyus_all'
        , default_args=default_args
        , schedule_interval="%s"
        ,max_active_runs=1) 
"""%(start_date,cron)
    shengs=list(zhulong_diqu_dict.keys())
    shengs.sort()
    shengs.append('gcjs')
    shengs.append('zfcg')
    shengs.append('qycg')
    part2_arr=[]
    i=0
    for sheng in shengs:
        part2="""
t%d=PythonOperator(task_id="m_gg_add_quyus_%s"
                ,python_callable=add_quyus_sheng
                ,op_kwargs={'sheng':'%s'}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=360)) 

    """%(i,sheng,sheng)
        i+=1
        part2_arr.append(part2)
    part2s=''.join(part2_arr)


    part3='\n'+'>>'.join([ 't%d'%i for i in range(len(shengs)) ])

    page=part1+part2s+part3 
    with open(os.path.join(dirname,'m_gg_update.py') ,'w',encoding='utf8') as f:
        f.write(page)
