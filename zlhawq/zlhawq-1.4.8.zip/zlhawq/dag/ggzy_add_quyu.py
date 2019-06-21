from zlhawq.data import zhulong_diqu_dict
import sys 
import os
def write_dag(dirname,**krg):
    
    para={
    "tag":"all",
    "start_date":"(2019,6,18)",
    "cron":"0 0 1/20 * *",

    }
    para.update(krg)
    tag=para["tag"]
    start_date=para["start_date"]

    cron=para["cron"]

    
    part1="""
from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime,timedelta
from zlhawq.api import add_quyu1_sheng


tag='%s'


default_args = {'owner': 'root',
                'depends_on_past': False,
                'start_date': datetime%s, }

d = DAG('abc_zzz_ggzy_flush'
        , default_args=default_args
        , schedule_interval="%s"
        ,max_active_runs=1) 
"""%(tag,start_date,cron)

    shengs=list(zhulong_diqu_dict.keys())
    shengs.sort()
    part2_arr=[]
    i=0
    for sheng in shengs:



        part2="""
t%d=PythonOperator(task_id="abc_zzz_ggzy_%s"
                ,python_callable=add_quyu1_sheng
                ,op_kwargs={'sheng':'%s','tag':tag}
                ,dag=d
                ,trigger_rule="all_done"

                ,depends_on_past=False

                ,execution_timeout=timedelta(minutes=60)) 

    """%(i,sheng,sheng)
        i+=1
        part2_arr.append(part2)

    part2s=''.join(part2_arr)


    part3='\n'+'>>'.join([ 't%d'%i for i in range(len(shengs)) ])

    page=part1+part2s+part3 
    with open(os.path.join(dirname,'abc_zzz.py') ,'w',encoding='utf8') as f:
        f.write(page)




