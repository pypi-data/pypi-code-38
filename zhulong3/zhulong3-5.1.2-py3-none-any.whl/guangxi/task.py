import time

from zhulong3.guangxi import baise
from zhulong3.guangxi import beihai
from zhulong3.guangxi import fangchenggang
from zhulong3.guangxi import shenghui
from zhulong3.guangxi import qinzhou



from lmf.dbv2 import db_command

from zhulong3.util.conf import get_conp,get_conp1

#1
def task_baise(**args):
    conp=get_conp(baise._name_)
    baise.work(conp,**args)

#2
def task_beihai(**args):
    conp=get_conp(beihai._name_)
    beihai.work(conp,**args)

#3
def task_fangchenggang(**args):
    conp=get_conp(fangchenggang._name_)
    fangchenggang.work(conp,**args)

#4
def task_shenghui(**args):
    conp=get_conp(shenghui._name_)
    shenghui.work(conp,**args)

#5
def task_qinzhou(**args):
    conp=get_conp(qinzhou._name_)
    qinzhou.work(conp,**args)


def task_all():
    bg=time.time()
    try:
        task_baise()
        task_beihai()
        task_fangchenggang()
        task_shenghui()
        task_qinzhou()
    except:
        print("part1 error!")

    ed=time.time()


    cos=int((ed-bg)/60)

    print("共耗时%d min"%cos)


def create_schemas():
    conp=get_conp1('gcjs')
    arr=["guangxi_baise","guangxi_beihai","guangxi_fangchenggang",
         "guangxi_shenghui","guangxi_qinzhou"]
    for diqu in arr:
        sql="create schema if not exists %s"%diqu
        db_command(sql,dbtype="postgresql",conp=conp)




