import time

from zhulong2.guizhou import shenghui
# 新增
from zhulong2.guizhou import tongren

from lmf.dbv2 import db_command 
from os.path import join ,dirname 

from zhulong2.util.conf import get_conp,get_conp1
#1
def task_shenghui(**args):
    conp=get_conp(shenghui._name_)
    shenghui.work(conp,**args)

#2
def task_tongren(**args):
    conp=get_conp(tongren._name_)
    tongren.work(conp,**args)

def task_all():
    bg=time.time()
    try:
        task_shenghui()
        task_tongren()
    except:
        print("part1 error!")

    ed=time.time()

    cos=int((ed-bg)/60)

    print("共耗时%d min"%cos)


def create_schemas():
    conp=get_conp1('zfcg')
    arr=["guizhou_shenghui","guizhou_tongren"]
    for diqu in arr:
        sql="create schema if not exists %s"%diqu
        db_command(sql,dbtype="postgresql",conp=conp)




