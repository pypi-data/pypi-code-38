from lmf.dbv2 import db_command
from zhulong.anhui import anqing
from zhulong.anhui import bengbu
from zhulong.anhui import bozhou
from zhulong.anhui import chaohu
from zhulong.anhui import chizhou
from zhulong.anhui import chuzhou
from zhulong.anhui import fuyang
from zhulong.anhui import hefei
from zhulong.anhui import huaibei
from zhulong.anhui import huainan
from zhulong.anhui import huangshan
from zhulong.anhui import luan
from zhulong.anhui import maanshan
from zhulong.anhui import suzhou
from zhulong.anhui import tongling
from zhulong.anhui import wuhu
from zhulong.anhui import xuancheng

from os.path import join, dirname


import time

from zhulong.util.conf import get_conp,get_conp1


# 1
def task_anqing(**args):
    conp = get_conp(anqing._name_)
    anqing.work(conp, **args)


# 2
def task_bengbu(**args):
    conp = get_conp(bengbu._name_)
    bengbu.work(conp, **args)


# 3
def task_bozhou(**args):
    conp = get_conp(bozhou._name_)
    bozhou.work(conp,**args)


# 4  ##打不开
def task_chaohu(**args):
    conp = get_conp(chaohu._name_)
    chaohu.work(conp, **args)


# 5
def task_chizhou(**args):
    conp = get_conp(chizhou._name_)
    chizhou.work(conp, **args)


# 6
def task_chuzhou(**args):
    conp = get_conp(chuzhou._name_)
    chuzhou.work(conp,pageLoadStrategy='none',pageloadtimeout=60, **args)


# 7
def task_fuyang(**args):
    conp = get_conp(fuyang._name_)
    fuyang.work(conp, **args)


# 8
def task_hefei(**args):
    conp = get_conp(hefei._name_)
    hefei.work(conp, **args)


# 9
def task_huaibei(**args):
    conp = get_conp(huaibei._name_)
    huaibei.work(conp, **args)


# 10
def task_huainan(**args):
    conp = get_conp(huainan._name_)
    huainan.work(conp, **args)


# 11
def task_huangshan(**args):
    conp = get_conp(huangshan._name_)
    huangshan.work(conp, **args)


# 12
def task_luan(**args):
    conp = get_conp(luan._name_)
    luan.work(conp, **args)


# 13
def task_maanshan(**args):
    conp = get_conp(maanshan._name_)
    maanshan.work(conp, **args)


# 14
def task_suzhou(**args):
    conp = get_conp(suzhou._name_,'anhui')
    suzhou.work(conp, **args)


# 15
def task_tongling(**args):
    conp = get_conp(tongling._name_)
    tongling.work(conp,pageLoadStrategy='none',pageloadtimeout=60,**args)


# 16
def task_wuhu(**args):
    conp = get_conp(wuhu._name_)
    wuhu.work(conp, **args)


# 17
def task_xuancheng(**args):
    conp = get_conp(xuancheng._name_)
    xuancheng.work(conp ,**args)




def task_all():
    bg = time.time()
    try:
        task_anqing()
        task_bengbu()
        task_bozhou()
        # task_chaohu()
        task_chizhou()
    except:
        print("part1 error!")

    try:
        task_chuzhou()
        task_fuyang()
        task_huaibei()
        task_huainan()
        task_huangshan()
    except:
        print("part2 error!")

    try:
        task_luan()
        task_maanshan()
        task_suzhou()
        task_tongling()
        task_wuhu()
    except:
        print("part3 error!")

    try:

        task_xuancheng()
        task_hefei()

    except:
        print("part4 error!")


    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('anhui')
    arr = ["anqing","bengbu","bozhou","chaohu","chizhou","chuzhou","fuyang",
           "huaibei","huainan","huangshan","luan","maanshan"
           ,"suzhou","tongling","wuhu",'xuancheng','hefei'
           ]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)




