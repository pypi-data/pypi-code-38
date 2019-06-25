import time

from zhulong2.sichuan import shenghui
from zhulong2.sichuan import mianyang

from lmf.dbv2 import db_command

from zhulong2.util.conf import get_conp,get_conp1

#1
def task_shenghui(**args):
    conp=get_conp(shenghui._name_)
    shenghui.work(conp,pageloadtimeout=180,pageLoadStrategy="none",**args)

#2
def task_mianyang(**args):
    conp=get_conp(mianyang._name_)
    mianyang.work(conp,pageloadtimeout=120,pageLoadStrategy="none",**args)



def task_all():
    bg=time.time()
    try:
        task_shenghui()
        task_mianyang()
    except:
        print("part1 error!")

    ed=time.time()
    cos=int((ed-bg)/60)
    print("共耗时%d min"%cos)


def create_schemas():
    conp=get_conp1('zfcg')
    arr=["sichuan_shenghui","sichuan_mianyang"]
    for diqu in arr:
        sql="create schema if not exists %s"%diqu
        db_command(sql,dbtype="postgresql",conp=conp)




