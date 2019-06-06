from lmf.dbv2 import db_command
from zhulong3.fujian import fuqing
from zhulong3.fujian import fuzhou
from zhulong3.fujian import quanzhou
from zhulong3.fujian import sanming
from zhulong3.fujian import zhangzhou


from os.path import join, dirname


import time

from zhulong3.util.conf import get_conp,get_conp1


# 1
def task_fuqing(**args):
    conp = get_conp(fuqing._name_)
    fuqing.work(conp, **args)


# 2
def task_fuzhou(**args):
    conp = get_conp(fuzhou._name_)
    fuzhou.work(conp, pageloadtimeout=60,**args)



# 4
def task_quanzhou(**args):
    conp = get_conp(quanzhou._name_)
    quanzhou.work(conp,pageLoadStrategy='none',pageloadtimeout=60, **args)


# 5
def task_sanming(**args):
    conp = get_conp(sanming._name_)
    sanming.work(conp , **args)


# 6
def task_zhangzhou(**args):
    conp = get_conp(zhangzhou._name_)
    zhangzhou.work(conp, **args)



def task_all():
    bg = time.time()
    try:
        task_fuzhou()
        task_fuqing()

    except:
        print("part1 error!")

    try:
        task_quanzhou()
        task_sanming()
        task_zhangzhou()
    except:
        print("part2 error!")




    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('gcjs')
    arr = ["fujian_fuqing","fujian_fuzhou",'fujian_quanzhou','fujian_sanming','fujian_zhangzhou']
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)




