import time

from zhulong.hebei import hebei


from zhulong.henan import qinyang

from lmf.dbv2 import db_command
from os.path import join, dirname

from zhulong.util.conf import get_conp, get_conp1


# 1
def task_hebei(**args):
    conp = get_conp(hebei._name_)
    hebei.work(conp,cdc_total=10, **args)





def task_all():
    bg = time.time()
    try:
        task_hebei()
    except:
        print("part1 error!")


    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)





def create_schemas():
    conp = get_conp1('hebei')
    arr = ["hebei"]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)




