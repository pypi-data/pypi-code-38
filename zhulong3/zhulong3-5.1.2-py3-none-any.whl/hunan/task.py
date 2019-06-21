from lmf.dbv2 import db_command

from zhulong3.hunan import changsha1
from zhulong3.hunan import changsha2
from zhulong3.hunan import huaihua
from zhulong3.hunan import loudi
from zhulong3.hunan import shaoyang
from zhulong3.hunan import shenghui
from zhulong3.hunan import wugang
from zhulong3.hunan import yueyang


from os.path import join, dirname


import time

from zhulong3.util.conf import get_conp,get_conp1


# 1
def task_changsha1(**args):
    conp = get_conp(changsha1._name_)
    changsha1.work(conp, **args)

def task_changsha2(**args):
    conp = get_conp(changsha2._name_)
    changsha2.work(conp, **args)

# 2
def task_huaihua(**args):
    conp = get_conp(huaihua._name_)
    huaihua.work(conp, **args)


# 3
def task_loudi(**args):
    conp = get_conp(loudi._name_)
    loudi.work(conp ,**args)


# 4
def task_shaoyang(**args):
    conp = get_conp(shaoyang._name_)
    shaoyang.work(conp, **args)

def task_shenghui(**args):
    conp = get_conp(shenghui._name_)
    shenghui.work(conp, **args)

def task_wugang(**args):
    conp = get_conp(wugang._name_)
    wugang.work(conp, **args)

def task_yueyang(**args):
    conp = get_conp(yueyang._name_)
    yueyang.work(conp, **args)

def task_all():
    bg = time.time()
    try:
        task_changsha1()
        task_changsha2()
        task_loudi()
        task_huaihua()

    except:
        print("part1 error!")
    try:
        task_shaoyang()
        task_shenghui()
        task_wugang()
        task_yueyang()
    except:
        print('part2 error!')
    ed=time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('gcjs')
    arr = ["hunan_changsha1","hunan_changsha2",'hunan_huaihua','hunan_loudi',
           'hunan_shaoyang','hunan_shenghui','hunan_wugang','hunan_yueyang']
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)




