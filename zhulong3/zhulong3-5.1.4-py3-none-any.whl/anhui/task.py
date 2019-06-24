from lmf.dbv2 import db_command
import time
from zhulong3.anhui import huainan
from zhulong3.anhui import xuancheng
from zhulong3.util.conf import get_conp,get_conp1


# 1
def task_huainan(**args):
    conp = get_conp(huainan._name_)
    huainan.work(conp, **args)


# 2
def task_xuancheng(**args):
    conp = get_conp(xuancheng._name_)
    xuancheng.work(conp, **args)


def task_all():
    bg = time.time()
    try:
        task_huainan()
        task_xuancheng()
    except:
        print("part Anhui error!")

    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)

def create_schemas():
    conp = get_conp1('gcjs')
    arr = [
        'anhui_huainan','anhui_xuancheng'
    ]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)