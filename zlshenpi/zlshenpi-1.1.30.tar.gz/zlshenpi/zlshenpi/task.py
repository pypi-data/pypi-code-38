from lmf.dbv2 import db_command
from zlshenpi.zlshenpi import guangdongsheng
from zlshenpi.zlshenpi import fujiansheng
from zlshenpi.zlshenpi import jiangxisheng
from zlshenpi.zlshenpi import henansheng
from zlshenpi.zlshenpi import hubeisheng
from zlshenpi.zlshenpi import hunansheng
from zlshenpi.zlshenpi import sichuansheng

from zlshenpi.zlshenpi import anhuisheng
from zlshenpi.zlshenpi import beijingshi
from zlshenpi.zlshenpi import hebeisheng
from zlshenpi.zlshenpi import heilongjiangsheng
from zlshenpi.zlshenpi import jilinsheng

from zlshenpi.zlshenpi import neimenggusheng
from zlshenpi.zlshenpi import shanxisheng1
from zlshenpi.zlshenpi import zhejiangsheng

from zlshenpi.zlshenpi import gansusheng
from zlshenpi.zlshenpi import ningxiasheng
from zlshenpi.zlshenpi import qinghaisheng
from zlshenpi.zlshenpi import shanxisheng
from zlshenpi.zlshenpi import xiamenshi
from zlshenpi.zlshenpi import yunnansheng
from zlshenpi.zlshenpi import xinjiangsheng

import time

from zlshenpi.util.conf import get_conp, get_conp1


# 1
def task_guangdongsheng(**args):
    conp = get_conp(guangdongsheng._name_)
    guangdongsheng.work(conp, cdc_total=10, **args)


# 2
def task_fujiansheng(**args):
    conp = get_conp(fujiansheng._name_)
    fujiansheng.work(conp, cdc_total=10, **args)


# 3
def task_jiangxisheng(**args):
    conp = get_conp(jiangxisheng._name_)
    jiangxisheng.work(conp, cdc_total=10, **args)


# 4
def task_henansheng(**args):
    conp = get_conp(henansheng._name_)
    henansheng.work(conp, pageloadtimeout=60, cdc_total=10, **args)


# 5
def task_hebeisheng(**args):
    conp = get_conp(hebeisheng._name_)
    hebeisheng.work(conp, cdc_total=10, **args)


# 6
def task_zhejiangsheng(**args):
    conp = get_conp(zhejiangsheng._name_)
    zhejiangsheng.work(conp, cdc_total=10, **args)


# 7
def task_shanxisheng1(**args):
    conp = get_conp(shanxisheng1._name_)
    shanxisheng1.work(conp, cdc_total=10, **args)


# 8
def task_neimenggusheng(**args):
    conp = get_conp(neimenggusheng._name_)
    neimenggusheng.work(conp, cdc_total=10, **args)


# 9
def task_jilinsheng(**args):
    conp = get_conp(jilinsheng._name_)
    jilinsheng.work(conp, cdc_total=10, **args)


# 10
def task_heilongjiangsheng(**args):
    conp = get_conp(heilongjiangsheng._name_)
    heilongjiangsheng.work(conp, cdc_total=10, **args)


# 11
def task_beijingshi(**args):
    conp = get_conp(beijingshi._name_)
    beijingshi.work(conp, cdc_total=10, **args)


# 12
def task_anhuisheng(**args):
    conp = get_conp(anhuisheng._name_)
    anhuisheng.work(conp, cdc_total=10, **args)


# 13
def task_hubeisheng(**args):
    conp = get_conp(hubeisheng._name_)
    hubeisheng.work(conp, cdc_total=10, pageloadtimeout=200, **args)


# 14
def task_hunansheng(**args):
    conp = get_conp(hunansheng._name_)
    hunansheng.work(conp,pageloadtimeout=100, cdc_total=10, **args)


# 1
def task_gansusheng(**args):
    conp = get_conp(gansusheng._name_)
    gansusheng.work(conp,pageloadtimeout=120, cdc_total=10, **args)


# 2
def task_ningxiasheng(**args):
    conp = get_conp(ningxiasheng._name_)
    ningxiasheng.work(conp,pageloadtimeout=120, cdc_total=10, **args)


# 3
def task_qinghaisheng(**args):
    conp = get_conp(qinghaisheng._name_)
    qinghaisheng.work(conp,pageloadtimeout=120 , cdc_total=10, **args)


# 4
def task_shanxisheng(**args):
    conp = get_conp(shanxisheng._name_)
    shanxisheng.work(conp, cdc_total=10, **args)


# 5
def task_xiamenshi(**args):
    conp = get_conp(xiamenshi._name_)
    xiamenshi.work(conp,pageloadtimeout=120, cdc_total=10, **args)


# 6
def task_xinjiangsheng(**args):
    conp = get_conp(xinjiangsheng._name_)
    xinjiangsheng.work(conp, pageloadtimeout=120 , cdc_total=10, **args)


# 6
def task_sichuansheng(**args):
    conp = get_conp(sichuansheng._name_)
    sichuansheng.work(conp, cdc_total=10, **args)

# 6
def task_yunnansheng(**args):
    conp = get_conp(yunnansheng._name_)
    yunnansheng.work(conp, cdc_total=10, **args)


def task_all():
    bg = time.time()
    try:
        task_henansheng()
        task_jiangxisheng()
        task_fujiansheng()
        task_guangdongsheng()
        task_hubeisheng()

    except:
        print("part1 error!")
    try:
        task_anhuisheng()
        task_beijingshi()
        task_hebeisheng()
        task_heilongjiangsheng()
        task_sichuansheng()


    except:

        print("part2 error!")

    try:
        task_jilinsheng()
        task_neimenggusheng()
        task_shanxisheng1()
        task_hunansheng()
        task_yunnansheng()
        task_zhejiangsheng()

    except:
        print("part3 error!")
    try:
        task_gansusheng()
        task_ningxiasheng()
        task_qinghaisheng()
        task_shanxisheng()
        task_xiamenshi()
        task_xinjiangsheng()
    except:
        print("part4 error!")

    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('zlshenpi')
    arr = ["guangdongsheng", 'fujiansheng', 'jiangxisheng', 'henansheng', 'hubeisheng', 'hunansheng', 'sichuansheng','yunnansheng',

           "anhuisheng", 'beijingshi', 'hebeisheng', 'heilongjiangsheng', 'jilinsheng',
           "neimenggusheng", 'shanxisheng1', 'zhejiangsheng',

           'xinjiangsheng', 'xiamenshi', 'shanxisheng', 'qinghaisheng', 'ningxiasheng', 'gansusheng',

           ]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)

# get_conp('hubeisheng')
