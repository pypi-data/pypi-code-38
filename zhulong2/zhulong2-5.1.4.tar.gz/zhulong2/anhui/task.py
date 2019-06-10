from zhulong2.anhui import shenghui
from zhulong2.anhui import anqing
from zhulong2.anhui import huainan
from zhulong2.anhui import luan




from lmf.dbv2 import db_command


from os.path import join ,dirname 

import time 

from zhulong2.util.conf import get_conp,get_conp1

#1
def task_shenghui(**args):
    conp=get_conp(shenghui._name_)
    shenghui.work(conp,**args)

#2
def task_anqing(**args):
    conp=get_conp(anqing._name_)
    anqing.work(conp,**args)

#3
def task_huainan(**args):
    conp=get_conp(huainan._name_)
    huainan.work(conp,**args)

#4
def task_luan(**args):
    conp=get_conp(luan._name_)
    luan.work(conp,**args)







def task_all():
    bg = time.time()
    try:

        task_shenghui()
        task_anqing()
        task_huainan()
        task_luan()

    except:
        print("part Anhui error!")

    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)

def create_schemas():
    conp = get_conp1('zfcg')
    arr = [
        'anhui_anqing','anhui_huainan','anhui_shenghui','anhui_luan'
    ]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)
    
