from lmf.dbv2 import db_command

from zhulong2.fujian import nanping
from zhulong2.fujian import sanming
from zhulong2.fujian import sanming1


from os.path import join, dirname

import time

from zhulong2.util.conf import get_conp,get_conp1


# 1
def task_nanping(**args):
    conp = get_conp(nanping._name_)
    nanping.work(conp, **args)

# 2
def task_sanming(**args):
    conp = get_conp(sanming._name_)
    sanming.work(conp, **args)

# 3
def task_sanming1(**args):
    conp = get_conp(sanming1._name_)
    sanming1.work(conp, **args)


def task_all():
    bg = time.time()
    try:
        task_nanping()
        task_sanming()
        task_sanming1()

    except:
        print("part1 error!")


    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('zfcg')
    arr = ['nanping','sanming','sanming1']
    for diqu in arr:
        sql = "create schema if not exists %s" % ('fujian_' + diqu)
        db_command(sql, dbtype="postgresql", conp=conp)




