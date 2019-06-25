import time

from zhulong2.yunnan import shenghui
from zhulong2.yunnan import yuxi

from lmf.dbv2 import db_command

from zhulong2.util.conf import get_conp,get_conp1

#1
def task_shenghui(**args):
    conp=get_conp(shenghui._name_)
    shenghui.work(conp,pageloadtimeout=180,**args)

#2
def task_yuxi(**args):
    conp=get_conp(yuxi._name_)
    yuxi.work(conp,pageloadtimeout=180,pageLoadStrategy="none",**args)



def task_all():
    bg=time.time()
    try:
        task_shenghui()
        task_yuxi()
    except:
        print("part1 error!")

    ed=time.time()
    cos=int((ed-bg)/60)
    print("共耗时%d min"%cos)


def create_schemas():
    conp=get_conp1('zfcg')
    arr=["yunnan_shenghui","yunnan_yuxi"]
    for diqu in arr:
        sql="create schema if not exists %s" %diqu
        db_command(sql,dbtype="postgresql",conp=conp)




