from lmf.dbv2 import db_command
import time
from zhulong3.zhixiashi import shanghai
from zhulong3.zhixiashi import beijing
from zhulong3.zhixiashi import chongqing
from zhulong3.zhixiashi import tianjin

from zhulong3.util.conf import get_conp,get_conp1


# 24
def task_shanghai(**args):
    conp = get_conp(shanghai._name_)
    shanghai.work(conp, **args)


# 25
def task_beijing(**args):
    conp = get_conp(beijing._name_)
    beijing.work(conp, **args)


# 26
def task_chongqing(**args):
    conp = get_conp(chongqing._name_)
    chongqing.work(conp,**args)


# 27
def task_tianjin(**args):
    conp = get_conp(tianjin._name_)
    tianjin.work(conp, **args)




def task_all():
    bg = time.time()

    try:
        task_chongqing()
        task_beijing()
        task_shanghai()
        task_tianjin()
    except:
        print("part6 shanxi11 error!")

    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)

def create_schemas():

    conp = get_conp1('gcjs')
    arr = ["beijing","tianjin", "shanghai", "chongqing",]
    for diqu in arr:
        sql = "create schema if not exists %s" % ("zhixiashi_"+diqu)
        db_command(sql, dbtype="postgresql", conp=conp)