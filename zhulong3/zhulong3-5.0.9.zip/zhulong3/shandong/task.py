from lmf.dbv2 import db_command

from zhulong3.shandong import dongying
from zhulong3.shandong import heze
from zhulong3.shandong import jinan
from zhulong3.shandong import linyi
from zhulong3.shandong import rizhao
from zhulong3.shandong import shenghui
from zhulong3.shandong import zaozhuang



from os.path import join, dirname


import time

from zhulong3.util.conf import get_conp,get_conp1


# 1
def task_dongying(**args):
    conp = get_conp(dongying._name_)
    dongying.work(conp,pageloadtimeout=40, **args)


# 2
def task_heze(**args):
    conp = get_conp(heze._name_)
    heze.work(conp, **args)


# 3
def task_jinan(**args):
    conp = get_conp(jinan._name_)
    jinan.work(conp ,**args)


# 4
def task_linyi(**args):
    conp = get_conp(linyi._name_)
    linyi.work(conp, **args)

# 5
def task_rizhao(**args):
    conp = get_conp(rizhao._name_)
    rizhao.work(conp, **args)

# 6
def task_shenghui(**args):
    conp = get_conp(shenghui._name_)
    shenghui.work(conp, **args)

# 7
def task_zaozhuang(**args):
    conp = get_conp(zaozhuang._name_)
    zaozhuang.work(conp, **args)


def task_all():
    bg = time.time()
    try:
        task_shenghui()
        task_dongying()
        task_heze()
        task_jinan()
    except:
        print("part1 error!")


    try:
        task_linyi()
        task_rizhao()
        task_zaozhuang()
    except:
        print("part2 error!")
    ed=time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('gcjs')
    arr = ["dongying",'heze','jinan','linyi','rizhao','shenghui','zaozhuang']
    for diqu in arr:
        sql = "create schema if not exists %s" % ('shandong_'+diqu)
        db_command(sql, dbtype="postgresql", conp=conp)




