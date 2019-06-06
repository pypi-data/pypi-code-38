from lmf.dbv2 import db_command
import time

from zhulong3.liaoning import shenghui
from zhulong3.liaoning import dalian
from zhulong3.liaoning import shenyang
from zhulong3.util.conf import get_conp,get_conp1



# 20
def task_shenghui(**args):
    conp = get_conp(shenghui._name_)
    shenghui.work(conp, **args)


# 21
def task_shenyang(**args):
    conp = get_conp(shenyang._name_)
    shenyang.work(conp,num=30,pageloadtimeout=50, **args)


# 22
def task_dalian(**args):
    conp = get_conp(dalian._name_)
    dalian.work(conp, num=30, pageloadtimeout=50, **args)



def task_all():
    bg = time.time()

    try:
        task_shenghui()
        task_shenyang()
        task_dalian()
    except:
        print("part5 LiaoNing  error!")

    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)

def create_schemas():
    conp = get_conp1('gcjs')
    arr = [
        "liaoning_shenghui", "liaoning_dalian", "liaoning_shenyang",
    ]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)