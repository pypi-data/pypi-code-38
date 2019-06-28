from zhulong.jiangsu import changshu
from zhulong.jiangsu import changzhou
from zhulong.jiangsu import danyang
from zhulong.jiangsu import dongtai
from zhulong.jiangsu import huaian

from zhulong.jiangsu import jiangyin
from zhulong.jiangsu import kunshan
from zhulong.jiangsu import lianyungang
from zhulong.jiangsu import nanjing
from zhulong.jiangsu import nantong

from zhulong.jiangsu import jiangsu
from zhulong.jiangsu import suqian
from zhulong.jiangsu import suzhou
from zhulong.jiangsu import taizhou
from zhulong.jiangsu import wuxi

from zhulong.jiangsu import xinyi
from zhulong.jiangsu import xuzhou
from zhulong.jiangsu import yancheng
from zhulong.jiangsu import yizheng
from zhulong.jiangsu import yangzhou

from zhulong.jiangsu import zhangjiagang
from zhulong.jiangsu import zhenjiang

from lmf.dbv2 import db_command
from os.path import join, dirname

import time


from zhulong.util.conf import get_conp,get_conp1


# 1
def task_changshu(**args):
    conp = get_conp(changshu._name_)
    changshu.work(conp, **args)


# 2
def task_changzhou(**args):
    conp = get_conp(changzhou._name_)
    changzhou.work(conp, **args)


# 3
def task_danyang(**args):
    conp = get_conp(danyang._name_)
    danyang.work(conp, **args)


# 4
def task_dongtai(**args):
    conp = get_conp(dongtai._name_)
    dongtai.work(conp, **args)


# 5
def task_huaian(**args):
    conp = get_conp(huaian._name_)
    huaian.work(conp, **args)


# 6
def task_jiangyin(**args):
    conp = get_conp(jiangyin._name_)
    jiangyin.work(conp, **args)


# 7
def task_kunshan(**args):
    conp = get_conp(kunshan._name_)
    kunshan.work(conp, **args)


# 8
def task_lianyungang(**args):
    conp = get_conp(lianyungang._name_)
    lianyungang.work(conp, **args)


# 9
def task_nanjing(**args):
    conp = get_conp(nanjing._name_)
    nanjing.work(conp, **args)


# 10
def task_nantong(**args):
    conp = get_conp(nantong._name_)
    nantong.work(conp, **args)


# 11
def task_jiangsu(**args):
    conp = get_conp(jiangsu._name_)
    jiangsu.work(conp, **args)


# 12
def task_suqian(**args):
    conp = get_conp(suqian._name_)
    suqian.work(conp, **args)




# 13
def task_suzhou(**args):
    conp = get_conp(suzhou._name_,'jiangsu')
    suzhou.work(conp, **args)


# 14
def task_taizhou(**args):
    conp = get_conp(taizhou._name_,'jiangsu')
    taizhou.work(conp, **args)


# 15
def task_wuxi(**args):
    conp = get_conp(wuxi._name_)
    wuxi.work(conp,pageloadtimetou=60, **args)


# 16
def task_xinyi(**args):
    conp = get_conp(xinyi._name_)
    xinyi.work(conp, **args)


# 17
def task_xuzhou(**args):
    conp = get_conp(xuzhou._name_)
    xuzhou.work(conp, **args)


# 18
def task_yancheng(**args):
    conp = get_conp(yancheng._name_)
    yancheng.work(conp, **args)


# 19
def task_yangzhou(**args):
    conp = get_conp(yangzhou._name_)
    yangzhou.work(conp, **args)


# 20
def task_yizheng(**args):
    conp = get_conp(yizheng._name_)
    yizheng.work(conp, **args)


# 21
def task_zhangjiagang(**args):
    conp = get_conp(zhangjiagang._name_)
    zhangjiagang.work(conp, **args)


# 22
def task_zhenjiang(**args):
    conp = get_conp(zhenjiang._name_)
    zhenjiang.work(conp, **args)


def task_all():
    task_changshu()
    task_changzhou()
    task_danyang()
    task_dongtai()
    task_huaian()

    task_jiangyin()
    task_kunshan()
    task_lianyungang()
    task_nanjing()
    task_nantong()

    task_jiangsu()
    task_suqian()
    task_suzhou()
    task_taizhou()
    task_wuxi()

    task_xinyi()
    task_xuzhou()
    task_yancheng()
    task_yangzhou()
    task_yizheng()

    task_zhangjiagang()
    task_zhenjiang()


def create_schemas():
    conp = get_conp1('jiangsu')
    arr = ["changshu", "changzhou", "danyang", "dongtai", "huaian"
        , "jiangyin", "kunshan", "lianyungang", "nanjing", "nantong"
        , "jiangsu", "suqian", "suzhou", "taizhou", "wuxi"
        , "xinyi", "xuzhou", "yancheng", "yangzhou", "yizheng"
        , "zhangjiagang", "zhenjiang"
           ]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)
