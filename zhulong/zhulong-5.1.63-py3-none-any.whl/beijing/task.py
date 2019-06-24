from lmf.dbv2 import db_command
from zhulong.beijing import beijing


from os.path import join, dirname


import time

from zhulong.util.conf import get_conp,get_conp1


# 1
def task_beijing(**args):
    conp = get_conp(beijing._name_)
    beijing.work(conp, **args)






def task_all():
    bg = time.time()
    try:
        task_beijing()

    except:
        print("part1 error!")


    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('beijing')
    arr = ["beijing"
           ]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)




