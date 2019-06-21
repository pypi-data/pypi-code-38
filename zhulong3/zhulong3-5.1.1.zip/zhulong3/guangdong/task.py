from lmf.dbv2 import db_command
from lmfscrap import web

from zhulong3.guangdong import shantou
from zhulong3.guangdong import shaoguan
from zhulong3.guangdong import shenghui
from zhulong3.guangdong import shenzhen
from zhulong3.guangdong import yangjiang
from zhulong3.guangdong import yunfu
from zhulong3.guangdong import zhongshan
from zhulong3.guangdong import dongguan



from os.path import join, dirname


import time

from zhulong3.util.conf import get_conp,get_conp1


# 1
def task_shantou(**args):
    conp = get_conp(shantou._name_)
    shantou.work(conp, **args)


# 2
def task_shaoguan(**args):
    conp = get_conp(shaoguan._name_)
    shaoguan.work(conp,pageloadstrategy='none',pageloadtimeout=120, **args)


# 3
def task_shenghui(**args):
    conp = get_conp(shenghui._name_)
    shenghui.work(conp,num=20,**args)


# 4
def task_shenzhen(**args):
    conp = get_conp(shenzhen._name_)
    shenzhen.work(conp,pageloadstrategy='none',pageloadtimeout=120, **args)

#1
def task_yangjiang(**args):
    conp=get_conp(yangjiang._name_)
    yangjiang.work(conp,**args)

#2
def task_yunfu(**args):
    conp=get_conp(yunfu._name_)
    yunfu.work(conp,pageloadstrategy='none',pageloadtimeout=120,**args)

#3
def task_zhongshan(**args):
    conp=get_conp(zhongshan._name_)
    zhongshan.work(conp,**args)

def task_dongguan(**args):
    conp=get_conp(dongguan._name_)
    dongguan.work(conp,pageloadtimeout=120,**args)

#


def task_all():
    bg = time.time()
    try:
        task_shenghui()
        task_shantou()
        task_shenzhen()
        task_shaoguan()
    except:
        print("part1 error!")

    try:
        task_yangjiang()
        task_yunfu()
        task_zhongshan()
        task_dongguan()
    except:
        print("part2 error!")



    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('gcjs')
    arr = ["shantou",'shaoguan','shenghui','shenzhen',"yangjiang","yunfu","zhongshan","dongguan"]

    for diqu in arr:
        sql = "create schema if not exists %s" % ('guangdong_'+diqu)
        db_command(sql, dbtype="postgresql", conp=conp)





