from lmf.dbv2 import db_command
import time
from zhulong3.neimenggu import shenghui

from zhulong3.util.conf import get_conp,get_conp1



# 23
def task_shenghui(**args):
    conp = get_conp(shenghui._name_)
    shenghui.work(conp,pageloadstrategy='none',num=20,pageloadtimeout=50, **args)




def task_all():
    bg = time.time()

    try:
        task_shenghui()

    except:
        print("part1 NeiMenggu  error!")

    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)

def create_schemas():
    conp = get_conp1('gcjs')
    arr = [
        "neimenggu_shenghui",
    ]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)