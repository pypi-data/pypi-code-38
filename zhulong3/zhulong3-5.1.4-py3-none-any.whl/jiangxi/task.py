from lmf.dbv2 import db_command

from zhulong3.jiangxi import jiujiang
from zhulong3.jiangxi import nanchang
from zhulong3.jiangxi import pingxiang
from zhulong3.jiangxi import shangrao


from os.path import join, dirname


import time

from zhulong3.util.conf import get_conp,get_conp1


# 1
def task_jiujiang(**args):
    conp = get_conp(jiujiang._name_)
    jiujiang.work(conp, **args)


# 2
def task_nanchang(**args):
    conp = get_conp(nanchang._name_)
    nanchang.work(conp, **args)


# 3
def task_pingxiang(**args):
    conp = get_conp(pingxiang._name_)
    pingxiang.work(conp ,**args)


# 4
def task_shangrao(**args):
    conp = get_conp(shangrao._name_)
    shangrao.work(conp, **args)



def task_all():
    bg = time.time()
    try:
        task_pingxiang()
        task_nanchang()
        task_jiujiang()
        task_shangrao()
    except:
        print("part1 error!")
    ed=time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('gcjs')
    arr = ["jiangxi_jiujiang",'jiangxi_nanchang','jiangxi_pingxiang','jiangxi_shangrao']
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)




