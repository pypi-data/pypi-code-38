from lmf.dbv2 import db_command

from zhulong.qinghai import qinghai
from zhulong.qinghai import xining


from os.path import join, dirname


import time

from zhulong.util.conf import get_conp,get_conp1


# 1
def task_qinghai(**args):
    conp = get_conp(qinghai._name_)
    qinghai.work(conp, **args)


###网站失效
# 2
def task_xining(**args):
    conp = get_conp(xining._name_)
    xining.work(conp, **args)



def task_all():
    bg = time.time()
    try:
        task_qinghai()
        # task_xining()


    except:
        print("part1 error!")


    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('qinghai')
    arr = ['qinghai','xining']
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)




