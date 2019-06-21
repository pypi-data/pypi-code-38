from lmf.dbv2 import db_command
import time

from zhulong3.jilin import shenghui
from zhulong3.jilin import changchun
from zhulong3.jilin import jilin
from zhulong3.jilin import siping
from zhulong3.jilin import tonghua
from zhulong3.util.conf import get_conp,get_conp1


# 16
def task_changchun(**args):
    conp = get_conp(changchun._name_)
    changchun.work(conp, **args)


# 17
def task_jilin(**args):
    conp = get_conp(jilin._name_)
    jilin.work(conp, **args)


# 18
def task_siping(**args):
    conp = get_conp(siping._name_)
    siping.work(conp, **args)


# 19
def task_tonghua(**args):
    conp = get_conp(tonghua._name_)
    tonghua.work(conp, **args)

# 30
def task_shenghui(**args):
    conp = get_conp(shenghui._name_)
    shenghui.work(conp, **args)

def task_all():
    bg = time.time()

    try:
        task_shenghui()
        task_tonghua()
        task_changchun()
        task_jilin()
        task_siping()
    except:
        print("part4 JiLin error!")

    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)

def create_schemas():
    conp = get_conp1('gcjs')
    arr = [
        "jilin_shenghui", "jilin_changchun", "jilin_jilin", "jilin_siping", "jilin_tonghua",
    ]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)