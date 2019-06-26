from lmf.dbv2 import db_command

from zhulong.jiangxi import dexing
from zhulong.jiangxi import fengcheng
from zhulong.jiangxi import fuzhou
from zhulong.jiangxi import ganzhou
from zhulong.jiangxi import gaoan
from zhulong.jiangxi import jian
from zhulong.jiangxi import jiangxi
from zhulong.jiangxi import jingdezhen
from zhulong.jiangxi import jinggangshan
from zhulong.jiangxi import lushan
from zhulong.jiangxi import nanchang
from zhulong.jiangxi import ruichang
from zhulong.jiangxi import ruijin
from zhulong.jiangxi import shangrao
from zhulong.jiangxi import xinyu
from zhulong.jiangxi import yichun
from zhulong.jiangxi import yingtan
from zhulong.jiangxi import zhangshu
from zhulong.jiangxi import jingdezhen2


from os.path import join, dirname


import time

from zhulong.util.conf import get_conp,get_conp1


# 1
def task_dexing(**args):
    conp = get_conp(dexing._name_)
    dexing.work(conp, **args)


# 2
def task_fengcheng(**args):
    conp = get_conp(fengcheng._name_)
    fengcheng.work(conp, **args)


# 3
def task_fuzhou(**args):
    conp = get_conp(fuzhou._name_,'jiangxi')
    fuzhou.work(conp ,**args)


# 4
def task_ganzhou(**args):
    conp = get_conp(ganzhou._name_)
    ganzhou.work(conp, **args)


# 5
def task_gaoan(**args):
    conp = get_conp(gaoan._name_)
    gaoan.work(conp, **args)



# 6
def task_jian(**args):
    conp = get_conp(jian._name_)
    jian.work(conp , **args)


# 7
def task_jiangxi(**args):
    conp = get_conp(jiangxi._name_)
    jiangxi.work(conp, **args)




# 8
def task_jingdezhen(**args):
    conp = get_conp(jingdezhen._name_)
    jingdezhen.work(conp, **args)


# 9
def task_jinggangshan(**args):
    conp = get_conp(jinggangshan._name_)
    jinggangshan.work(conp, **args)


# 10
def task_lushan(**args):
    conp = get_conp(lushan._name_)
    lushan.work(conp, **args)


# 11
def task_nanchang(**args):
    conp = get_conp(nanchang._name_)
    nanchang.work(conp ,**args)


# 12
def task_ruichang(**args):
    conp = get_conp(ruichang._name_)
    ruichang.work(conp, **args)


# 13
def task_ruijin(**args):
    conp = get_conp(ruijin._name_)
    ruijin.work(conp, **args)


# 14
def task_shangrao(**args):
    conp = get_conp(shangrao._name_)
    shangrao.work(conp, **args)


# 15
def task_xinyu(**args):
    conp = get_conp(xinyu._name_)
    xinyu.work(conp, **args)

#16
def task_yichun(**args):
    conp = get_conp(yichun._name_,'jiangxi')
    yichun.work(conp, **args)

#17
def task_yingtan(**args):
    conp = get_conp(yingtan._name_)
    yingtan.work(conp, **args)

#18
def task_zhangshu(**args):
    conp = get_conp(zhangshu._name_)
    zhangshu.work(conp, **args)



def task_jingdezhen2(**args):
    conp = get_conp(jingdezhen2._name_)
    jingdezhen2.work(conp, **args)



def task_all():
    bg = time.time()
    try:
        task_dexing()
        task_fengcheng()
        task_fuzhou()
        task_ganzhou()
        task_gaoan()
    except:
        print("part1 error!")

    try:
        task_jian()
        task_jiangxi()
        task_jingdezhen()
        task_jinggangshan()
        task_jingdezhen2()


        task_lushan()
    except:
        print("part2 error!")

    try:
        task_nanchang()
        task_ruichang()
        task_ruijin()
        task_shangrao()
        task_xinyu()
    except:
        print("part3 error!")

    try:

        task_yichun()
        task_yingtan()
        task_zhangshu()
    except:
        print("part4 error!")


    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('jiangxi')
    arr = ["dexing","fengcheng",'fuzhou','ganzhou','gaoan','jian','jiangxi','jingdezhen',
           'jinggangshan','lushan','nanchang','ruichang','ruijin','shangrao',
            'xinyu','yichun','yingtan','zhangshu','jingdezhen2']
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)




