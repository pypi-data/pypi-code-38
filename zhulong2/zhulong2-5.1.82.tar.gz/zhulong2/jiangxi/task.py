from lmf.dbv2 import db_command

from zhulong2.jiangxi import jian
from zhulong2.jiangxi import jiangxi
from zhulong2.jiangxi import nanchang
from zhulong2.jiangxi import pingxiang



from os.path import join, dirname


import time

from zhulong2.util.conf import get_conp,get_conp1


# 1
def task_jian(**args):
    conp = get_conp(jian._name_)
    jian.work(conp, **args)

# 2
def task_jiangxi(**args):
    conp = get_conp(jiangxi._name_)
    jiangxi.work(conp, **args)

# 3
def task_nanchang(**args):
    conp = get_conp(nanchang._name_)
    nanchang.work(conp, **args)

# 4
def task_pingxiang(**args):
    conp = get_conp(pingxiang._name_)
    pingxiang.work(conp, **args)


def task_all():
    bg = time.time()
    try:
        task_jian()
        task_jiangxi()
        task_nanchang()
        task_pingxiang()

    except:
        print("part1 error!")


    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('zfcg')
    arr = ['jian','jiangxi','nanchang','pingxiang']
    for diqu in arr:
        sql = "create schema if not exists %s" % ('jiangxi_'+diqu)
        db_command(sql, dbtype="postgresql", conp=conp)




