from zhulong2.liaoning import chaoyang
from zhulong2.liaoning import dalian
from zhulong2.liaoning import shenyang
from zhulong2.liaoning import wafangdian





from lmf.dbv2 import db_command


from os.path import join ,dirname 

import time 

from zhulong2.util.conf import get_conp,get_conp1

#6
#8
def task_chaoyang(**args):
    conp=get_conp(chaoyang._name_)
    chaoyang.work(conp,**args)
#9
def task_shenyang(**args):
    conp=get_conp(shenyang._name_)
    shenyang.work(conp,**args)
#10
def task_wafangdian(**args):
    conp=get_conp(wafangdian._name_)
    wafangdian.work(conp,**args)

def task_dalian(**args):
    conp=get_conp(dalian._name_)
    dalian.work(conp,pageloadstrategy='none',pageloadtimeout=40,**args)





def task_all():
    bg = time.time()
    try:

        task_chaoyang()
        task_shenyang()
        task_wafangdian()
        task_dalian()

    except:
        print("part liaoning error!")

    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)

def create_schemas():
    conp = get_conp1('zfcg')
    arr = [
        'liaoning_dalian',
        'liaoning_chaoyang',
        'liaoning_shenyang',
        'liaoning_wafangdian',
    ]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)
    
