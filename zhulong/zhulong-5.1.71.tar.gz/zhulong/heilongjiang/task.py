from lmf.dbv2 import db_command
from zhulong.heilongjiang import daqing
from zhulong.heilongjiang import hegang
from zhulong.heilongjiang import heilongjiang
from zhulong.heilongjiang import qiqihaer
from zhulong.heilongjiang import yichun
from zhulong.heilongjiang import haerbin_zfcg


from os.path import join, dirname


import time

from zhulong.util.conf import get_conp,get_conp1


# 1
def task_daqing(**args):
    conp = get_conp(daqing._name_)
    daqing.work(conp, **args)


# 2
def task_hegang(**args):
    conp = get_conp(hegang._name_)
    hegang.work(conp, **args)


# 3
def task_heilongjiang(**args):
    conp = get_conp(heilongjiang._name_)
    heilongjiang.work(conp ,**args)


# 4
def task_qiqihaer(**args):
    conp = get_conp(qiqihaer._name_)
    qiqihaer.work(conp, **args)


# 5
def task_yichun(**args):
    conp = get_conp(yichun._name_,'heilongjiang')
    yichun.work(conp , **args)

#6
def task_haerbin_zfcg(**args):
    conp = get_conp(haerbin_zfcg._name_)
    haerbin_zfcg.work(conp , **args)





def task_all():
    bg = time.time()
    try:
        task_daqing()
        task_hegang()
        task_qiqihaer()

    except:
        print("part1 error!")

    try:
        task_heilongjiang()
        task_yichun()

    except:
        print("part2 error!")




    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('heilongjiang')
    arr = ["daqing","hegang","heilongjiang",'qiqihaer','yichun','haerbin_zfcg','haerbin_gcjs'
           ]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)




