from lmf.dbv2 import db_command
import time
from zhulong.guangxi import baise
from zhulong.guangxi import beihai
from zhulong.guangxi import chongzuo
from zhulong.guangxi import fangchenggang
from zhulong.guangxi import guangxi
from zhulong.guangxi import guigang
from zhulong.guangxi import guilin
from zhulong.guangxi import hechi
from zhulong.guangxi import hezhou
from zhulong.guangxi import laibin
from zhulong.guangxi import nanning
from zhulong.guangxi import qinzhou
from zhulong.guangxi import wuzhou
from zhulong.guangxi import liuzhou

from os.path import join, dirname

from zhulong.util.conf import get_conp, get_conp1


# 1
def task_baise(**args):
    conp = get_conp(baise._name_)
    baise.work(conp, **args)


# 2
def task_beihai(**args):
    conp = get_conp(beihai._name_)
    beihai.work(conp, **args)


# 3
def task_guigang(**args):
    conp = get_conp(guigang._name_)
    guigang.work(conp, **args)


# 4
def task_chongzuo(**args):
    conp = get_conp(chongzuo._name_)
    chongzuo.work(conp, **args)


# 5
def task_fangchenggang(**args):
    conp = get_conp(fangchenggang._name_)
    fangchenggang.work(conp, **args)


# 6
def task_guangxi(**args):
    conp = get_conp(guangxi._name_)
    guangxi.work(conp, **args)


# 7
def task_guilin(**args):
    conp = get_conp(guilin._name_)
    guilin.work(conp, **args)


# 8
def task_hechi(**args):
    conp = get_conp(hechi._name_)
    hechi.work(conp, **args)


# 9
def task_hezhou(**args):
    conp = get_conp(hezhou._name_)
    hezhou.work(conp, **args)


# 10
def task_laibin(**args):
    conp = get_conp(laibin._name_)
    laibin.work(conp, **args)


# 11
def task_liuzhou(**args):
    conp = get_conp(liuzhou._name_)
    liuzhou.work(conp, **args)


# 12
def task_nanning(**args):
    conp = get_conp(nanning._name_)
    nanning.work(conp, **args)


# 13
def task_wuzhou(**args):
    conp = get_conp(wuzhou._name_)
    wuzhou.work(conp, **args)


# 13
def task_qinzhou(**args):
    conp = get_conp(qinzhou._name_)
    qinzhou.work(conp, **args)


def task_all():
    bg = time.time()
    try:
        task_baise()
        task_beihai()
        task_guigang()
        task_chongzuo()
        task_fangchenggang()
    except:
        print("part1 error!")

    try:
        task_guangxi()
        task_guilin()
        task_hechi()
        task_hezhou()
        task_laibin()
    except:
        print("part2 error!")

    try:
        task_liuzhou()
        task_nanning()
        task_qinzhou()
        task_wuzhou()
    except:
        print("part3 error!")

    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('guangxi')
    arr = [
        "baise", "beihai", "chongzuo", "fangchenggang", "guangxi",
        "guigang", "guilin", "hechi", "hezhou", "laibin",
        "liuzhou", "nanning", "qinzhou", "wuzhou",
    ]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)
