from lmf.dbv2 import db_command
from zhulong.xinjiang import xinjiang
from zhulong.xinjiang import wulumuqi
from zhulong.xinjiang import kezhou
from zhulong.xinjiang import beitun
from zhulong.xinjiang import akesu
from zhulong.xinjiang import aletai


from os.path import join, dirname


import time

from zhulong.util.conf import get_conp,get_conp1


# 1
def task_xinjiang(**args):
    conp = get_conp(xinjiang._name_)
    xinjiang.work(conp,pageLoadStrategy = "none",pageloadtimeout=80, **args)


# 2
def task_wulumuqi(**args):
    conp = get_conp(wulumuqi._name_)
    wulumuqi.work(conp, **args)


# 3
def task_beitun(**args):
    conp = get_conp(beitun._name_)
    beitun.work(conp,pageLoadStrategy = "none",**args)


# 4
def task_kezhou(**args):
    conp = get_conp(kezhou._name_)
    kezhou.work(conp, **args)
# 5
def task_akesu(**args):
    conp = get_conp(akesu._name_)
    akesu.work(conp, **args)

def task_aletai(**args):
    conp = get_conp(aletai._name_)
    aletai.work(conp, **args)




def task_all():
    bg = time.time()
    try:
        task_xinjiang()
        task_wulumuqi()
        task_beitun()
        task_kezhou()
        task_akesu()
        task_aletai()


    except:
        print("part1 error!")





    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('xinjiang')
    arr = ["xinjiang","beitun","kezhou","wulumuqi","akesu","aletai"]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)
