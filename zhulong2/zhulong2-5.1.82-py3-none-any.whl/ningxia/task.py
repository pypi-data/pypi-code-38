import time

from zhulong2.ningxia import shenghui
# 新增
from zhulong2.ningxia import yinchuan


from lmf.dbv2 import db_command

from zhulong2.util.conf import get_conp,get_conp1

#1
def task_shenghui(**args):
    conp=get_conp(shenghui._name_)
    shenghui.work(conp,pageloadtimeout=120,**args)

#2
def task_yinchuan(**args):
    conp=get_conp(yinchuan._name_)
    yinchuan.work(conp,pageloadtimeout=120,**args)


def task_all():
    bg=time.time()
    try:
        task_shenghui()
        task_yinchuan()
    except:
        print("part1 error!")

    ed=time.time()
    cos=int((ed-bg)/60)
    print("共耗时%d min"%cos)


def create_schemas():
    conp=get_conp1('zfcg')
    arr=["ningxia_shenghui","ningxia_yinchuan"]
    for diqu in arr:
        sql="create schema if not exists %s"%diqu
        db_command(sql,dbtype="postgresql",conp=conp)




