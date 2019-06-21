from lmf.dbv2 import db_command
from zhulong3.henan import kaifeng
from zhulong3.henan import pingdingshan
from zhulong3.henan import puyang
from zhulong3.henan import zhengzhou
from zhulong3.henan import sanmenxia


from os.path import join, dirname


import time

from zhulong3.util.conf import get_conp,get_conp1


# 1 ###网站偶尔打不开
def task_kaifeng(**args):
    conp = get_conp(kaifeng._name_)
    kaifeng.work(conp, **args)


# 2
def task_pingdingshan(**args):
    conp = get_conp(pingdingshan._name_)
    pingdingshan.work(conp, **args)


# 3
def task_puyang(**args):
    conp = get_conp(puyang._name_)
    puyang.work(conp ,**args)



def task_zhengzhou(**args):
    conp = get_conp(zhengzhou._name_)
    zhengzhou.work(conp, **args)

def task_sanmenxia(**args):
    conp = get_conp(sanmenxia._name_)
    sanmenxia.work(conp, **args)



#


def task_all():
    bg = time.time()
    try:
        task_kaifeng()
        task_pingdingshan()
        task_puyang()
        task_sanmenxia()
        task_zhengzhou()
    except:
        print("part1 error!")





    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('gcjs')
    arr = ["kaifeng",'pingdingshan','puyang','zhengzhou','sanmenxia']
    for diqu in arr:
        sql = "create schema if not exists %s" % ('henan_'+diqu)
        db_command(sql, dbtype="postgresql", conp=conp)




