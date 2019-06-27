import sys
import os 
from zlhawq.dag.data_gcjs import para 

def write_dag(quyu,dirname,**krg):
    
    para={
    "tag":"cdc",
    "start_date":"(2019,5,18)",
    "cron":"0 0/12 * * *",
    "timeout":'minutes=60'
    }
    para.update(krg)
    tag=para["tag"]
    start_date=para["start_date"]

    cron=para["cron"]

    timeout=para["timeout"]
    

    arr=quyu.split("_")
    db,schema=arr[0],'_'.join(arr[1:])
    sheng,shi=schema.split("_")[0],'_'.join(schema.split("_")[1:])

    filename="v3_%s.py"%quyu
    path1=os.path.join(os.path.dirname(__file__),'template','gcjs.txt')
    path2=os.path.join(dirname,filename)

    with open(path1,'r',encoding='utf8') as f :
        content=f.read()

    #from ##zhulong.anqing## import ##task_anqing## 

    content=content.replace("##zhulong3.anhui##",'zhulong3.%s'%sheng)
    content=content.replace("##task_anqing##","task_%s"%shi)

    #tag='##cdc##'
    #datetime##(2019,4,27)##, }
    content=content.replace("##cdc##",tag)
    content=content.replace("##(2019,4,27)##",start_date)

    """
    d = DAG('##abc_anhui_anqing##'
            , default_args=default_args
            , schedule_interval="##0 0/12 * * *##"
            ,max_active_runs=1) 
    """
    content=content.replace("##v3_gcjs_anhui_anqing##","v3_%s"%quyu)

    content=content.replace("##0 0/12 * * *##",cron)

    #task_id="##anqing_a1##"

    content=content.replace("##gcjs_anhui_anqing_a1##","%s_a1"%quyu)

    content=content.replace("##minutes=60##",timeout)

    content=content.replace("##gcjs_anhui_anqing_b1##","%s_b1"%quyu)

    content=content.replace("##gcjs_anhui_anqing##",quyu)




    with open(path2,'w',encoding='utf-8') as f:
        f.write(content)



#write_dag('gcjs_fujian_fuqing',sys.path[0])
def write_dags(dirname,**krg):
    for w in para:
        quyu='_'.join(w[:2])
        timeout=w[2]
        krg.update({"timeout":timeout})
        write_dag(quyu,dirname,**krg)



#write_dags("d:/dag3",start_date='(2019,5,20)',cron='0 0 1/2 * *')