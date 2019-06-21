from zhulong.hunan import changde
from zhulong.hunan import chenzhou
from zhulong.hunan import hengyang
from zhulong.hunan import zhuzhou

from zhulong.hunan import huaihua
from zhulong.hunan import loudi
from zhulong.hunan import shaoyang
from zhulong.hunan import xiangtan

from zhulong.hunan import yiyang
from zhulong.hunan import yongzhou
from zhulong.hunan import yueyang
from zhulong.hunan import zhangjiajie

from zhulong.hunan import yuanjiang
from zhulong.hunan import liuyang
from zhulong.hunan import liling
from zhulong.hunan import changsha
from zhulong.hunan import hunan
from zhulong.hunan import xiangxi
from lmf.dbv2 import db_command
from os.path import join, dirname

import time

from zhulong.util.conf import get_conp, get_conp1


# 1
def task_changde(**args):
    conp = get_conp(changde._name_)
    changde.work(conp, **args)


# 2
def task_chenzhou(**args):
    conp = get_conp(chenzhou._name_)
    chenzhou.work(conp, **args)


# 3
def task_hengyang(**args):
    conp = get_conp(hengyang._name_)
    hengyang.work(conp, **args)


# 4
def task_huaihua(**args):
    conp = get_conp(huaihua._name_)
    huaihua.work(conp, **args)


# 5
def task_loudi(**args):
    conp = get_conp(loudi._name_)
    loudi.work(conp, **args)


# 6
def task_shaoyang(**args):
    conp = get_conp(shaoyang._name_)
    shaoyang.work(conp, **args)


# 7
def task_xiangtan(**args):
    conp = get_conp(xiangtan._name_)
    xiangtan.work(conp, **args)


# 8
def task_yiyang(**args):
    conp = get_conp(yiyang._name_)
    yiyang.work(conp, **args)


# 9
def task_yongzhou(**args):
    conp = get_conp(yongzhou._name_)
    yongzhou.work(conp, **args)


# 10
def task_yueyang(**args):
    conp = get_conp(yueyang._name_)
    yueyang.work(conp, **args)


# 11
def task_zhangjiajie(**args):
    conp = get_conp(zhangjiajie._name_)
    zhangjiajie.work(conp, **args)


# 12
def task_zhuzhou(**args):
    conp = get_conp(zhuzhou._name_)
    zhuzhou.work(conp, **args)


# 13
def task_yuanjiang(**args):
    conp = get_conp(yuanjiang._name_)
    yuanjiang.work(conp, pageloadtimeout=40, pageloadstrategy='none', **args)


# 14
def task_liling(**args):
    conp = get_conp(liling._name_)
    liling.work(conp, **args)


# 15
def task_liuyang(**args):
    conp = get_conp(liuyang._name_)
    liuyang.work(conp, **args)


# 16
def task_changsha(**args):
    conp = get_conp(changsha._name_)
    changsha.work(conp, **args)


# 17
def task_hunan(**args):
    conp = get_conp(hunan._name_)
    hunan.work(conp,pageloadstrategy='none',pageloadtimeout=60,num=30,**args)


# 17
def task_xiangxi(**args):
    conp = get_conp(xiangxi._name_)
    xiangxi.work(conp, **args)


def task_all():
    task_changde()
    task_chenzhou()
    task_hengyang()
    task_zhuzhou()

    task_huaihua()
    task_loudi()
    task_shaoyang()
    task_xiangtan()

    task_yiyang()
    task_yongzhou()
    task_yueyang()
    task_zhangjiajie()

    task_liling()
    task_liuyang()
    task_yuanjiang()
    task_hunan()
    task_xiangxi()


def create_schemas():
    conp = get_conp1('hunan')
    arr = ["changde", "chenzhou", "hengyang", "huaihua", "loudi", "shaoyang"
        , "xiangtan", "yiyang", "yongzhou", "yueyang", "zhangjiajie", "zhuzhou",
           "liling", "liuyang", "yuanjiang", 'changsha', 'hunan', 'xiangxi'
           ]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)
