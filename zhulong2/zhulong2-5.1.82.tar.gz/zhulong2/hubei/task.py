from lmf.dbv2 import db_command

from zhulong2.hubei import ezhou
from zhulong2.hubei import huanggang
from zhulong2.hubei import hubei
from zhulong2.hubei import jingmen
from zhulong2.hubei import shiyan
from zhulong2.hubei import wuhan
from zhulong2.hubei import wuhan2


from os.path import join, dirname


import time

from zhulong2.util.conf import get_conp,get_conp1


# 1
def task_ezhou(**args):
    conp = get_conp(ezhou._name_)
    ezhou.work(conp,headless=False,**args)

# 2
def task_huanggang(**args):
    conp = get_conp(huanggang._name_)
    huanggang.work(conp, **args)

# 3
def task_hubei(**args):
    conp = get_conp(hubei._name_)
    hubei.work(conp, **args)


# 4
def task_jingmen(**args):
    conp = get_conp(jingmen._name_)
    jingmen.work(conp, **args)

# 5
def task_shiyan(**args):
    conp = get_conp(shiyan._name_)
    shiyan.work(conp, **args)

# 6
def task_wuhan(**args):
    conp = get_conp(wuhan._name_)
    wuhan.work(conp, **args)
# 7
def task_wuhan2(**args):
    conp = get_conp(wuhan2._name_)
    wuhan2.work(conp, **args)



def task_all():
    bg = time.time()
    try:
        task_ezhou()
        task_huanggang()
        task_hubei()
        task_jingmen()
        task_shiyan()
        task_wuhan()
        task_wuhan2()

    except:
        print("part1 error!")


    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('zfcg')
    arr = ['ezhou','huanggang','hubei','jingmen','shiyan','wuhan','wuhan2']

    for diqu in arr:
        sql = "create schema if not exists %s" % ('hubei_' + diqu)
        db_command(sql, dbtype="postgresql", conp=conp)




