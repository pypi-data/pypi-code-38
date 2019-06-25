import time

from zhulong2.shanxi import shenghui

# 新增
from zhulong2.shanxi import hanzhong
from zhulong2.shanxi import shangluo
from zhulong2.shanxi import xian

from lmf.dbv2 import db_command

from zhulong2.util.conf import get_conp,get_conp1

#1
def task_shenghui(**args):
    conp=get_conp(shenghui._name_)
    shenghui.work(conp,pageloadtimeout=120,**args)

#2
def task_hanzhong(**args):
    conp=get_conp(hanzhong._name_)
    hanzhong.work(conp,pageloadtimeout=120,**args)

#3
def task_shangluo(**args):
    conp=get_conp(shangluo._name_)
    shangluo.work(conp,pageloadtimeout=120,**args)

#4
def task_xian(**args):
    conp=get_conp(xian._name_)
    xian.work(conp,pageloadtimeout=120,**args)


def task_all():
    bg=time.time()
    try:
        task_shenghui()
        task_hanzhong()
        task_shangluo()
        task_xian()
    except:
        print("part1 error!")

    ed=time.time()
    cos=int((ed-bg)/60)
    print("共耗时%d min"%cos)


def create_schemas():
    conp=get_conp1('zfcg')
    arr=["shanxi_shenghui","shanxi_hanzhong","shanxi_shangluo","shanxi_xian"]
    for diqu in arr:
        sql="create schema if not exists %s"%diqu
        db_command(sql,dbtype="postgresql",conp=conp)




