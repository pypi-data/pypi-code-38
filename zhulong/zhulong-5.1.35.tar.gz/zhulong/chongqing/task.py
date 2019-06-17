from lmf.dbv2 import db_command
from zhulong.chongqing import yongchuan
from zhulong.chongqing import chongqing

from os.path import join, dirname


import time

from zhulong.util.conf import get_conp,get_conp1


# 1
def task_yongchuan(**args):
    conp = get_conp(yongchuan._name_)
    yongchuan.work(conp, **args)


# 2
def task_chongqing(**args):
    conp = get_conp(chongqing._name_)
    chongqing.work(conp, **args)


def task_all():
    bg = time.time()
    try:
        task_yongchuan()
        task_chongqing()

    except:
        print("part1 error!")


    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('chongqing')
    arr = ["yongchuan","chongqing"]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)




