from lmf.dbv2 import db_command

from zhulong2.hunan import changsha
from zhulong2.hunan import changde
from zhulong2.hunan import chenzhou
from zhulong2.hunan import hengyang
from zhulong2.hunan import hunan
from zhulong2.hunan import xiangtan
from zhulong2.hunan import yiyang
from zhulong2.hunan import yueyang
from zhulong2.hunan import zhangjiajie
from zhulong2.hunan import zhuzhou


from os.path import join, dirname


import time

from zhulong2.util.conf import get_conp,get_conp1


# 1
def task_changde(**args):
    conp = get_conp(changde._name_)
    changde.work(conp, **args)

# 2
def task_changsha(**args):
    conp = get_conp(changsha._name_)
    changsha.work(conp, **args)

# 3
def task_chenzhou(**args):
    conp = get_conp(chenzhou._name_)
    chenzhou.work(conp, **args)

# 4
def task_hengyang(**args):
    conp = get_conp(hengyang._name_)
    hengyang.work(conp, **args)

# 5
def task_hunan(**args):
    conp = get_conp(hunan._name_)
    hunan.work(conp, **args)

# 6
def task_xiangtan(**args):
    conp = get_conp(xiangtan._name_)
    xiangtan.work(conp, **args)


# 7
def task_yiyang(**args):
    conp = get_conp(yiyang._name_)
    yiyang.work(conp, **args)

# 8
def task_yueyang(**args):
    conp = get_conp(yueyang._name_)
    yueyang.work(conp, **args)

# 9
def task_zhangjiajie(**args):
    conp = get_conp(zhangjiajie._name_)
    zhangjiajie.work(conp, **args)

# 10
def task_zhuzhou(**args):
    conp = get_conp(zhuzhou._name_)
    zhuzhou.work(conp, **args)


def task_all():
    bg = time.time()
    try:
        task_changde()
        task_changsha()
        task_chenzhou()
        task_hengyang()
        task_hunan()

    except:
        print("part1 error!")

    try:
        task_xiangtan()
        task_yiyang()
        task_yueyang()
        task_zhangjiajie()
        task_zhuzhou()

    except:
        print("part1 error!")

    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('zfcg')
    arr = ['changde','changsha','chenzhou','hengyang','hunan','xiangtan','yiyang','yueyang','zhangjiajie','zhuzhou']

    for diqu in arr:
        sql = "create schema if not exists %s" % ('hunan_'+diqu)
        db_command(sql, dbtype="postgresql", conp=conp)




