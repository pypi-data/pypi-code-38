from lmf.dbv2 import db_command

from zhulong2.shandong import dezhou
from zhulong2.shandong import dongying
from zhulong2.shandong import laiwu
from zhulong2.shandong import liaocheng
from zhulong2.shandong import linyi
from zhulong2.shandong import qingdao
from zhulong2.shandong import rizhao
from zhulong2.shandong import shandong
from zhulong2.shandong import weihai
from zhulong2.shandong import yantai


from os.path import join, dirname


import time

from zhulong2.util.conf import get_conp,get_conp1


# 1
def task_dezhou(**args):
    conp = get_conp(dezhou._name_)
    dezhou.work(conp, **args)

# 2
def task_dongying(**args):
    conp = get_conp(dongying._name_)
    dongying.work(conp,**args)

# 3
def task_laiwu(**args):
    conp = get_conp(laiwu._name_)
    laiwu.work(conp, **args)

# 4
def task_liaocheng(**args):
    conp = get_conp(liaocheng._name_)
    liaocheng.work(conp,cdc_total=2, **args)

# 5
def task_linyi(**args):
    conp = get_conp(linyi._name_)
    linyi.work(conp, **args)

# 6
def task_qingdao(**args):
    conp = get_conp(qingdao._name_)
    qingdao.work(conp, **args)


# 7
def task_rizhao(**args):
    conp = get_conp(rizhao._name_)
    rizhao.work(conp, **args)

# 8
def task_shandong(**args):
    conp = get_conp(shandong._name_)
    shandong.work(conp, **args)

# 9
def task_weihai(**args):
    conp = get_conp(weihai._name_)
    weihai.work(conp, **args)

# 10
def task_yantai(**args):
    conp = get_conp(yantai._name_)
    yantai.work(conp, **args)


def task_all():
    bg = time.time()
    try:
        task_dezhou()
        task_dongying()
        task_laiwu()
        task_liaocheng()
        task_linyi()

    except:
        print("part1 error!")

    try:
        task_qingdao()
        task_rizhao()
        task_shandong()
        task_weihai()
        task_yantai()

    except:
        print("part1 error!")

    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('zfcg')
    arr = ['dezhou','dongying','laiwu','liaocheng','linyi','qingdao','rizhao','shandong','weihai','yantai']

    for diqu in arr:
        sql = "create schema if not exists %s" % ('shandong_'+diqu)
        db_command(sql, dbtype="postgresql", conp=conp)




