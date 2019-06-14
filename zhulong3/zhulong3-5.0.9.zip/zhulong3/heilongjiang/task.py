from lmf.dbv2 import db_command
import time
from zhulong3.heilongjiang import shenghui
from zhulong3.heilongjiang import haerbin
from zhulong3.heilongjiang import qqhaer
from zhulong3.util.conf import get_conp,get_conp1


# 8
def task_shenghui(**args):
    conp = get_conp(shenghui._name_)
    shenghui.work(conp,num=15, **args)


# 9
def task_haerbin(**args):
    conp = get_conp(haerbin._name_)
    haerbin.work(conp,num=40, pagelosdtimeout=40, **args)


# 10
def task_qqhaer(**args):
    conp = get_conp(qqhaer._name_)
    qqhaer.work(conp,num=15, **args)

def task_all():
    bg = time.time()
    try:

        task_shenghui()
        task_haerbin()
        task_qqhaer()
    except:
        print("part HeiLongJiang error!")

    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)

def create_schemas():
    conp = get_conp1('gcjs')
    arr = [
        "heilongjiang_shenghui", "heilongjiang_haerbin", "heilongjiang_qqhaer",
    ]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)