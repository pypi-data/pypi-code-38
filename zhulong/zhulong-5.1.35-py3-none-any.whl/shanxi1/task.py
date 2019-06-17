from lmf.dbv2 import db_command, db_query

from zhulong.shanxi1 import shanxi
from zhulong.shanxi1 import shanxi_cdc
from zhulong.shanxi1 import shanxi2

from os.path import join, dirname


import time

from zhulong.util.conf import get_conp,get_conp1


# 1
def task_shanxi(**args):
    conp = get_conp(shanxi._name_,'shanxi1')

    sql = """select table_name from information_schema.tables where table_schema='%s'""" % (conp[4])
    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df["table_name"].values

    if "gg" in arr:
        shanxi_cdc.work(conp,cdc_total=15, **args)
    else:
        shanxi.work(conp, **args)

def task_shanxi2(**args):
    conp = get_conp(shanxi2._name_,'shanxi1')
    shanxi2.work(conp, **args)


def task_all():
    bg = time.time()
    try:
        task_shanxi()
        task_shanxi2()

    except:
        print("part1 error!")



    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('shanxi1')
    arr = ['shanxi','shanxi2']
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)

