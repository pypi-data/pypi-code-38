from lmf.dbv2 import db_command

from zhulong.ningxia import ningxia
from zhulong.ningxia import yinchuan
from zhulong.ningxia import guyuan


from os.path import join, dirname


import time

from zhulong.util.conf import get_conp,get_conp1


# 1
def task_guyuan(**args):
    conp = get_conp(guyuan._name_)
    guyuan.work(conp, **args)


# 2
def task_ningxia(**args):
    conp = get_conp(ningxia._name_)
    ningxia.work(conp, **args)


# 3
def task_yinchuan(**args):
    conp = get_conp(yinchuan._name_)
    yinchuan.work(conp,**args)



def task_all():
    bg = time.time()
    try:
        task_guyuan()

    except:
        print("part1 error!")

    try:
        task_ningxia()



    except:
        print("part2 error!")

    try:
        task_yinchuan()

    except:
        print("part3 error!")


    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('ningxia')
    arr = ['guyuan','ningxia','yinchuan']
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)




