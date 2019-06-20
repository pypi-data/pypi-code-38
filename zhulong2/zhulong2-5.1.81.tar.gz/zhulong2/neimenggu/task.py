from zhulong2.neimenggu import shenghui
from zhulong2.neimenggu import baotou
from zhulong2.neimenggu import eerduosi
from zhulong2.neimenggu import huhehaote
from zhulong2.neimenggu import tongliao
from zhulong2.neimenggu import bayannaoer





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
def task_baotou(**args):
    conp=get_conp(baotou._name_)
    baotou.work(conp,**args)
#10
def task_eerduosi(**args):
    conp=get_conp(eerduosi._name_)
    eerduosi.work(conp,**args)

def task_huhehaote(**args):
    conp=get_conp(huhehaote._name_)
    huhehaote.work(conp,**args)
def task_tongliao(**args):
    conp=get_conp(tongliao._name_)
    tongliao.work(conp,**args)
def task_bayannaoer(**args):
    conp=get_conp(bayannaoer._name_)
    bayannaoer.work(conp,**args)





def task_all():
    bg = time.time()
    try:

        task_shenghui()
        task_baotou()
        task_eerduosi()
        task_huhehaote()
        task_tongliao()
        task_bayannaoer()

    except:
        print("part neimenggu error!")

    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)

def create_schemas():
    conp = get_conp1('zfcg')
    arr = [
        'neimenggu_huhehaote',
        'neimenggu_shenghui',
        'neimenggu_baotou',
        'neimenggu_eerduosi',
        'neimenggu_tongliao',
        'neimenggu_bayannaoer',
    ]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)
    
