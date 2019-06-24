from zhulong2.jilin import shenghui
from zhulong2.jilin import changchun
from zhulong2.jilin import jilin





from lmf.dbv2 import db_command


from os.path import join ,dirname 

import time 

from zhulong2.util.conf import get_conp,get_conp1

#6
#8
def task_shenghui(**args):
    conp=get_conp(shenghui._name_)
    shenghui.work(conp,**args)
#9
def task_changchun(**args):
    conp=get_conp(changchun._name_)
    changchun.work(conp,**args)
#10
def task_jilin(**args):
    conp=get_conp(jilin._name_)
    jilin.work(conp,**args)





def task_all():
    bg = time.time()
    try:

        task_shenghui()
        task_changchun()
        task_jilin()

    except:
        print("part jiangsu error!")

    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)

def create_schemas():
    conp = get_conp1('zfcg')
    arr = [
        'jilin_shenghui',
        'jilin_changchun',
        'jilin_jilin',
    ]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)
    
