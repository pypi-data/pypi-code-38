import sys
import os 
from zlhawq.dag.data_ggzy import para 

def write_dag(quyu,dirname,**krg):
    
    para={
    "tag":"cdc",
    "start_date":"(2019,5,18)",
    "cron":"0 0/12 * * *",
    "timeout":'minutes=120'
    }
    para.update(krg)
    tag=para["tag"]
    start_date=para["start_date"]

    cron=para["cron"]

    timeout=para["timeout"]
    

    arr=quyu.split("_")
    db,schema=arr[0],'_'.join(arr[1:])

    filename="abc_%s.py"%quyu
    path1=os.path.join(os.path.dirname(__file__),'template','ggzy.txt')
    path2=os.path.join(dirname,filename)

    with open(path1,'r',encoding='utf8') as f :
        content=f.read()

    #from ##zhulong.anqing## import ##task_anqing## 

    content=content.replace("##zhulong.anhui##",'zhulong.%s'%db)
    content=content.replace("##task_anqing##","task_%s"%schema)

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
    content=content.replace("##abc_anhui_anqing##","abc_%s"%quyu)

    content=content.replace("##0 0/12 * * *##",cron)

    #task_id="##anqing_a1##"

    content=content.replace("##anqing_a1##","%s_a1"%schema)

    content=content.replace("##minutes=60##",timeout)

    content=content.replace("##anqing_b1##","%s_b1"%schema)

    content=content.replace("##anhui_anqing##",quyu)




    with open(path2,'w',encoding='utf-8') as f:
        f.write(content)






#write_dag('anhui_bozhou',sys.path[0])

def write_dags(dirname,**krg):
    for w in para:
        quyu='_'.join(w[:2])
        timeout=w[2]
        krg.update({"timeout":timeout})
        write_dag(quyu,dirname,**krg)



#write_dag('guandong_dongguan','d:/dag',start_date='(2019,6,17)',tiemout='minutes=120')