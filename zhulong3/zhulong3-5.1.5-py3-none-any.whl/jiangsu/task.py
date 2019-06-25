from lmf.dbv2 import db_command
import time
from zhulong3.jiangsu import shenghui
from zhulong3.jiangsu import changzhou
from zhulong3.jiangsu import nanjing
from zhulong3.jiangsu import nantong
from zhulong3.jiangsu import yangzhou
from zhulong3.util.conf import get_conp,get_conp1

# 11
def task_shenghui(**args):
    conp = get_conp(shenghui._name_)
    shenghui.work(conp, num=200, pageloadtimeout=50, pageloadstrategy="none",**args)


# 12
def task_changzhou(**args):
    conp = get_conp(changzhou._name_)
    changzhou.work(conp,num=30, pageloadtimeout=40, **args)


# 13
def task_nanjing(**args):
    conp = get_conp(nanjing._name_)
    nanjing.work(conp, **args)


# 14
def task_nantong(**args):
    conp = get_conp(nantong._name_)
    nantong.work(conp,num=40, pageloadtimeout=40, **args)


# 15
def task_yangzhou(**args):
    conp = get_conp(yangzhou._name_)
    yangzhou.work(conp, **args)


def task_all():
    bg = time.time()
    try:
        task_shenghui()
        task_changzhou()
        task_nanjing()
        task_nantong()
        task_yangzhou()
    except:
        print("part3 JiangSu error!")

    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)

def create_schemas():
    conp = get_conp1('gcjs')
    arr = [
        "jiangsu_shenghui", "jiangsu_changzhou", "jiangsu_nanjing", "jiangsu_nantong","jiangsu_yangzhou"]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)