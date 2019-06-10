import time

from zhulong2.guangxi import baise
from zhulong2.guangxi import fangchenggang
from zhulong2.guangxi import shenghui
from zhulong2.guangxi import guigang
from zhulong2.guangxi import guilin
from zhulong2.guangxi import liuzhou
from zhulong2.guangxi import nanning
from zhulong2.guangxi import qinzhou
from zhulong2.guangxi import wuzhou



from lmf.dbv2 import db_command

from zhulong2.util.conf import get_conp,get_conp1

#1
def task_baise(**args):
    conp=get_conp(baise._name_)
    baise.work(conp,**args)

#2
def task_fangchenggang(**args):
    conp=get_conp(fangchenggang._name_)
    fangchenggang.work(conp,**args)

#3
def task_shenghui(**args):
    conp=get_conp(shenghui._name_)
    shenghui.work(conp,pageloadtimeout=120,pageLoadStrategy="none",**args)

#4
def task_guigang(**args):
    conp=get_conp(guigang._name_)
    guigang.work(conp,pageloadtimeout=120,**args)

#5
def task_guilin(**args):
    conp=get_conp(guilin._name_)
    guilin.work(conp,**args)

#6
def task_liuzhou(**args):
    conp=get_conp(liuzhou._name_)
    liuzhou.work(conp,**args)

#7
def task_nanning(**args):
    conp=get_conp(nanning._name_)
    nanning.work(conp,**args)

#8
def task_qinzhou(**args):
    conp=get_conp(qinzhou._name_)
    qinzhou.work(conp,**args)

#9
def task_wuzhou(**args):
    conp=get_conp(wuzhou._name_)
    wuzhou.work(conp,**args)




def task_all():
    bg=time.time()
    try:
        task_baise()
        task_fangchenggang()
        task_shenghui()
        task_guigang()
        task_guilin()
    except:
        print("part1 error!")

    try:
        task_liuzhou()
        task_nanning()
        task_qinzhou()
        task_wuzhou()
    except:
        print("part2 error!")

    ed=time.time()
    cos=int((ed-bg)/60)
    print("共耗时%d min"%cos)


def create_schemas():
    conp=get_conp1('zfcg')
    arr=["guangxi_baise","guangxi_fangchenggang","guangxi_shenghui","guangxi_guigang",
         "guangxi_guilin","guangxi_liuzhou","guangxi_nanning","guangxi_qinzhou","guangxi_wuzhou"]
    for diqu in arr:
        sql="create schema if not exists %s"%diqu
        db_command(sql,dbtype="postgresql",conp=conp)




