import time

from zhulong.fujian import fujian2

from zhulong.fujian import fujian

from zhulong.fujian import fuqing

from zhulong.fujian import fuzhou

from zhulong.fujian import jianou

from zhulong.fujian import longyan

from zhulong.fujian import nanan

from zhulong.fujian import nanping

from zhulong.fujian import ningde

from zhulong.fujian import putian

from zhulong.fujian import quanzhou

from zhulong.fujian import sanming

from zhulong.fujian import shaowu

from zhulong.fujian import wuyishan

from zhulong.fujian import xiamen

from zhulong.fujian import yongan

from zhulong.fujian import zhangzhou

from lmf.dbv2 import db_command
from os.path import join, dirname

from zhulong.util.conf import get_conp, get_conp1


# 1
def task_fujian(**args):
    conp = get_conp(fujian._name_)
    fujian.work(conp, **args)


# 2
def task_fujian2(**args):
    conp = get_conp(fujian2._name_)
    fujian2.work(conp, **args)


# 3
def task_fuqing(**args):
    conp = get_conp(fuqing._name_)
    fuqing.work(conp, **args)


# 3
def task_fuzhou(**args):
    conp = get_conp(fuzhou._name_, 'fujian')
    fuzhou.work(conp, pageloadtimeout=180, **args)


# 4
def task_jianou(**args):
    conp = get_conp(jianou._name_)
    jianou.work(conp, **args)


# 5
def task_longyan(**args):
    conp = get_conp(longyan._name_)
    longyan.work(conp, **args)


# 6
def task_nanan(**args):
    conp = get_conp(nanan._name_)
    nanan.work(conp, **args)


# 7
def task_nanping(**args):
    conp = get_conp(nanping._name_)
    nanping.work(conp, pageloadtimeout=180,**args)


# 8
def task_ningde(**args):
    conp = get_conp(ningde._name_)
    ningde.work(conp, pageloadtimeout=180, pageloadstrategy="none",**args)


# 9
def task_putian(**args):
    conp = get_conp(putian._name_)
    putian.work(conp,pageloadtimeout=180, pageloadstrategy="none",**args)


# 10
def task_quanzhou(**args):
    conp = get_conp(quanzhou._name_)
    quanzhou.work(conp, pageloadtimeout=180, **args)


# 11
def task_sanming(**args):
    conp = get_conp(sanming._name_)
    sanming.work(conp, **args)


# 12
def task_shaowu(**args):
    conp = get_conp(shaowu._name_)
    shaowu.work(conp, **args)


#
# #13
def task_wuyishan(**args):
    conp = get_conp(wuyishan._name_)
    wuyishan.work(conp, pageloadtimeout=180, **args)


# 14
def task_xiamen(**args):
    conp = get_conp(xiamen._name_)
    xiamen.work(conp, **args)


# 15
def task_yongan(**args):
    conp = get_conp(yongan._name_)
    yongan.work(conp, **args)


# 16
def task_zhangzhou(**args):
    conp = get_conp(zhangzhou._name_)
    zhangzhou.work(conp, pageloadtimeout=180,**args)


def task_all():
    bg = time.time()
    try:
        task_fujian()
        task_fuqing()
        task_fuzhou()
        task_jianou()
        task_longyan()
    except:
        print("part1 error!")

    try:
        task_nanan()
        task_nanping()
        task_ningde()
        task_putian()
        task_quanzhou()
    except:
        print("part2 error!")

    try:
        task_sanming()
        # task_shaowu()
        # task_wuyishan()
        task_xiamen()
        task_yongan()
        task_zhangzhou()
    except:
        print("part3 error!")

    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('fujian')
    arr = ["fujian", "fujian2", "fuqing", "fuzhou", "jianou", "longyan",
           "nanan", "nanping", "ningde", "putian", "quanzhou",
           "sanming", "shaowu", "wuyishan", "xiamen", "yongan",
           "zhangzhou", ]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)
