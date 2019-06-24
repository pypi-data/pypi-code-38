from lmf.dbv2 import db_command

from zhulong.yunnan import baoshan
from zhulong.yunnan import chuxiong
from zhulong.yunnan import dali
from zhulong.yunnan import lijiang
from zhulong.yunnan import lincang
from zhulong.yunnan import puer
from zhulong.yunnan import tengchong
from zhulong.yunnan import wenshan
from zhulong.yunnan import yunnan
from zhulong.yunnan import yuxi
from zhulong.yunnan import zhaotong
from zhulong.yunnan import kunming



##新增
from zhulong.yunnan import xishuangbanna
from zhulong.yunnan import dehong
from zhulong.yunnan import honghe
from zhulong.yunnan import yunnan2



from os.path import join, dirname


import time

from zhulong.util.conf import get_conp,get_conp1


# 1
def task_baoshan(**args):
    conp = get_conp(baoshan._name_)
    baoshan.work(conp, **args)


# 2
def task_chuxiong(**args):
    conp = get_conp(chuxiong._name_)
    chuxiong.work(conp, **args)


# 3
def task_dali(**args):
    conp = get_conp(dali._name_)
    dali.work(conp,**args)


# 4
def task_lijiang(**args):
    conp = get_conp(lijiang._name_)
    lijiang.work(conp, **args)


# 5
def task_puer(**args):
    conp = get_conp(puer._name_)
    puer.work(conp , **args)



# 6
def task_tengchong(**args):
    conp = get_conp(tengchong._name_)
    tengchong.work(conp, **args)


# 7
def task_wenshan(**args):
    conp = get_conp(wenshan._name_)
    wenshan.work(conp, **args)




# 8
def task_yunnan(**args):
    conp = get_conp(yunnan._name_)
    yunnan.work(conp, **args)


# 9
def task_yuxi(**args):
    conp = get_conp(yuxi._name_)
    yuxi.work(conp, **args)


# 10
def task_zhaotong(**args):
    conp = get_conp(zhaotong._name_)
    zhaotong.work(conp, **args)


# 11
def task_lincang(**args):
    conp = get_conp(lincang._name_)
    lincang.work(conp ,**args)

def task_kunming(**args):
    conp = get_conp(kunming._name_)
    kunming.work(conp,**args)

def task_xishuangbanna(**args):
    conp = get_conp(xishuangbanna._name_)
    xishuangbanna.work(conp,**args)

def task_dehong(**args):
    conp = get_conp(dehong._name_)
    dehong.work(conp,**args)

def task_honghe(**args):
    conp = get_conp(honghe._name_)
    honghe.work(conp,**args)


def task_yunnan2(**args):
    conp = get_conp(yunnan2._name_)
    yunnan2.work(conp,**args)




def task_all():
    bg = time.time()
    try:
        task_baoshan()
        task_chuxiong()
        task_dali()
        task_lijiang()
        task_lincang()
        task_kunming()
    except:
        print("part1 error!")

    try:
        task_puer()
        task_tengchong()
        task_wenshan()
        task_yunnan()
        task_yuxi()
        task_zhaotong()

    except:
        print("part2 error!")

    try:
        task_xishuangbanna()
        task_dehong()
        task_honghe()
        task_yunnan2()
    except:
        print('part 3 error!')


    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('yunnan')
    arr = ['baoshan','chuxiong','dali','lijiang','lincang','puer',
           'tengchong','wenshan','yunnan','yuxi','zhaotong','kunming',
            "xishuangbanna","dehong","honghe","yunnan2",  ##新增
           ]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)




