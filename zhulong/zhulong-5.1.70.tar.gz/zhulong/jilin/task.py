from lmf.dbv2 import db_command
from zhulong.jilin import baicheng
from zhulong.jilin import baishan
from zhulong.jilin import changchun
from zhulong.jilin import jilin
from zhulong.jilin import jilinshi
from zhulong.jilin import liaoyuan
from zhulong.jilin import siping
from zhulong.jilin import songyuan
from zhulong.jilin import tonghua

from os.path import join, dirname


import time

from zhulong.util.conf import get_conp,get_conp1

# 1
def task_baicheng(**args):
    conp = get_conp(baicheng._name_)
    baicheng.work(conp, **args)


# 2
def task_baishan(**args):
    conp = get_conp(baishan._name_)
    baishan.work(conp, **args)


# 3
def task_changchun(**args):
    conp = get_conp(changchun._name_)
    changchun.work(conp ,**args)


# 4
def task_jilin(**args):
    conp = get_conp(jilin._name_)
    jilin.work(conp, **args)


# 5
def task_jilinshi(**args):
    conp = get_conp(jilinshi._name_)
    jilinshi.work(conp , **args)

# 6
def task_liaoyuan(**args):
    conp = get_conp(liaoyuan._name_)
    liaoyuan.work(conp , **args)

# 7
def task_siping(**args):
    conp = get_conp(siping._name_)
    siping.work(conp, **args)

# 8
def task_songyuan(**args):
    conp = get_conp(songyuan._name_)
    songyuan.work(conp, **args)

# 9
def task_tonghua(**args):
    conp = get_conp(tonghua._name_)
    tonghua.work(conp, **args)



def task_all():
    bg = time.time()
    try:
        task_baicheng()
        task_baishan()
        task_changchun()
        task_jilin()
        task_jilinshi()
    except:
        print("part1 error!")

    try:
        task_liaoyuan()
        task_siping()
        task_songyuan()

        #网站最近有问题
        task_tonghua()
    except:
        print("part2 error!")


    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('jilin')
    arr = ['baicheng','baishan','changchun','jilin','jilinshi','liaoyuan','siping','songyuan','tonghua'
           ]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)




