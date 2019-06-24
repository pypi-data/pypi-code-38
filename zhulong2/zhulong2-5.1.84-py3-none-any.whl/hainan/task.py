import time

from zhulong2.hainan import haikou
from zhulong2.hainan import shenghui
from zhulong2.hainan import sanya
from zhulong2.hainan import wenchang

from lmf.dbv2 import db_command

from zhulong2.util.conf import get_conp,get_conp1

#1
def task_haikou(**args):
    conp=get_conp(haikou._name_)
    haikou.work(conp,pageloadtimeout=120,pageLoadStrategy="none",**args)

#2
def task_shenghui(**args):
    conp=get_conp(shenghui._name_)
    shenghui.work(conp,pageloadtimeout=120,pageLoadStrategy="none",**args)

#3
def task_sanya(**args):
    conp=get_conp(sanya._name_)
    sanya.work(conp,**args)

#4
def task_wenchang(**args):
    conp=get_conp(wenchang._name_)
    wenchang.work(conp,**args)


def task_all():
    bg=time.time()
    try:
        task_haikou()
        task_shenghui()
        task_sanya()
        task_wenchang()
    except:
        print("part1 error!")

    ed=time.time()
    cos=int((ed-bg)/60)
    print("共耗时%d min"%cos)


def create_schemas():
    conp=get_conp1('zfcg')
    arr=["hainan_haikou","hainan_shenghui","hainan_sanya","hainan_wenchang"]
    for diqu in arr:
        sql="create schema if not exists %s"%diqu
        db_command(sql,dbtype="postgresql",conp=conp)




