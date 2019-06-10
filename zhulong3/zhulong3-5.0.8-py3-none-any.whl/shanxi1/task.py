from lmf.dbv2 import db_command
import time
from zhulong3.shanxi1 import datong
from zhulong3.shanxi1 import linfen
from zhulong3.shanxi1 import taiyuan
from zhulong3.shanxi1 import xinzhou

from zhulong3.util.conf import get_conp,get_conp1


# 24
def task_datong(**args):
    conp = get_conp(datong._name_)
    datong.work(conp, **args)


# 25
def task_linfen(**args):
    conp = get_conp(linfen._name_)
    linfen.work(conp, **args)


# 26
def task_taiyuan(**args):
    conp = get_conp(taiyuan._name_)
    taiyuan.work(conp, num=20,pageloadtimeout=50, pageloadstrategy='none',**args)


# 27
def task_xinzhou(**args):
    conp = get_conp(xinzhou._name_)
    xinzhou.work(conp,pageloadstrategy='none', **args)




def task_all():
    bg = time.time()

    try:
        task_taiyuan()
        task_linfen()
        task_datong()
        task_xinzhou()
    except:
        print("part6 shanxi11 error!")

    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)

def create_schemas():
    conp = get_conp1('gcjs')
    arr = ["shanxi1_datong","shanxi1_linfen", "shanxi1_taiyuan", "shanxi1_xinzhou",]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)