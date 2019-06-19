from zhulong2.heilongjiang import shenghui
from zhulong2.heilongjiang import yichun




from lmf.dbv2 import db_command


from os.path import join ,dirname 

import time 

from zhulong2.util.conf import get_conp,get_conp1

#6
def task_shenghui(**args):
    conp=get_conp(shenghui._name_)
    shenghui.work(conp,**args)

#7
def task_yichun(**args):
    conp=get_conp(yichun._name_)
    yichun.work(conp,**args)






def task_all():
    bg = time.time()
    try:

        task_shenghui()
        task_yichun()


    except:
        print("part heilongjiang error!")

    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)

def create_schemas():
    conp = get_conp1('zfcg')
    arr = [
        'heilongjiang_shenghui',
        'heilongjiang_yichun',
    ]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)
    
