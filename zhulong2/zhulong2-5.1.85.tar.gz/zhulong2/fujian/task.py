from lmf.dbv2 import db_command

from zhulong2.fujian import nanping
from zhulong2.fujian import sanming
from zhulong2.fujian import sanming1

##新增
from zhulong2.fujian import fuzhou
from zhulong2.fujian import longyan
from zhulong2.fujian import nanping1
from zhulong2.fujian import ningde
from zhulong2.fujian import putian
from zhulong2.fujian import quanzhou
from zhulong2.fujian import xiamen
from zhulong2.fujian import zhangzhou

from os.path import join, dirname

import time

from zhulong2.util.conf import get_conp,get_conp1


# 1
def task_nanping(**args):
    conp = get_conp(nanping._name_)
    nanping.work(conp, **args)

def task_nanping1(**args):
    conp = get_conp(nanping1._name_)
    nanping1.work(conp, **args)


# 2
def task_sanming(**args):
    conp = get_conp(sanming._name_)
    sanming.work(conp, **args)

# 3
def task_sanming1(**args):
    conp = get_conp(sanming1._name_)
    sanming1.work(conp, **args)

def task_fuzhou(**args):
    conp = get_conp(fuzhou._name_)
    fuzhou.work(conp, **args)

def task_longyan(**args):
    conp = get_conp(longyan._name_)
    longyan.work(conp, **args)


def task_ningde(**args):
    conp = get_conp(ningde._name_)
    ningde.work(conp, **args)


def task_putian(**args):
    conp = get_conp(putian._name_)
    putian.work(conp, **args)


def task_quanzhou(**args):
    conp = get_conp(quanzhou._name_)
    quanzhou.work(conp, **args)


def task_xiamen(**args):
    conp = get_conp(xiamen._name_)
    xiamen.work(conp, **args)


def task_zhangzhou(**args):
    conp = get_conp(zhangzhou._name_)
    zhangzhou.work(conp, **args)


def task_all():
    bg = time.time()
    try:
        task_nanping()
        task_sanming()
        task_sanming1()
        task_fuzhou()
        task_quanzhou()
        task_zhangzhou()
        task_longyan()
        task_nanping1()
        task_ningde()
        task_xiamen()
        task_putian()

    except:
        print("part1 error!")


    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('zfcg')
    arr = ['nanping','sanming','sanming1',
    "fuzhou","longyan","nanping1","ningde","putian","quanzhou","xiamen","zhangzhou", ## 新增

    ]

    for diqu in arr:
        sql = "create schema if not exists %s" % ('fujian_' + diqu)
        db_command(sql, dbtype="postgresql", conp=conp)




