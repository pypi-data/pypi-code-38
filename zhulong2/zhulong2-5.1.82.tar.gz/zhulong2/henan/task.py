from lmf.dbv2 import db_command

from zhulong2.henan import anyang
from zhulong2.henan import hebi
from zhulong2.henan import henan
from zhulong2.henan import jiaozuo
from zhulong2.henan import kaifeng
from zhulong2.henan import luohe
from zhulong2.henan import luoyang
from zhulong2.henan import nanyang
from zhulong2.henan import pingdingshan
from zhulong2.henan import puyang
from zhulong2.henan import sanmenxia
from zhulong2.henan import shangqiu
from zhulong2.henan import xinxiang
from zhulong2.henan import xinyang
from zhulong2.henan import xuchang
from zhulong2.henan import zhengzhou
from zhulong2.henan import zhoukou
from zhulong2.henan import zhumadian



from os.path import join, dirname


import time

from zhulong2.util.conf import get_conp,get_conp1


# 1
def task_anyang(**args):
    conp = get_conp(anyang._name_)
    anyang.work(conp, **args)

# 2
def task_hebi(**args):
    conp = get_conp(hebi._name_)
    hebi.work(conp, **args)

# 3
def task_henan(**args):
    conp = get_conp(henan._name_)
    henan.work(conp, **args)

# 4
def task_jiaozuo(**args):
    conp = get_conp(jiaozuo._name_)
    jiaozuo.work(conp, **args)

# 5
def task_kaifeng(**args):
    conp = get_conp(kaifeng._name_)
    kaifeng.work(conp, **args)

# 6
def task_luohe(**args):
    conp = get_conp(luohe._name_)
    luohe.work(conp, **args)

# 7
def task_luoyang(**args):
    conp = get_conp(luoyang._name_)
    luoyang.work(conp, **args)

# 8
def task_nanyang(**args):
    conp = get_conp(nanyang._name_)
    nanyang.work(conp, **args)

# 9
def task_pingdingshan(**args):
    conp = get_conp(pingdingshan._name_)
    pingdingshan.work(conp, **args)

# 10
def task_puyang(**args):
    conp = get_conp(puyang._name_)
    puyang.work(conp, **args)

# 11
def task_sanmenxia(**args):
    conp = get_conp(sanmenxia._name_)
    sanmenxia.work(conp, **args)

# 12
def task_shangqiu(**args):
    conp = get_conp(shangqiu._name_)
    shangqiu.work(conp, **args)

# 13
def task_xinxiang(**args):
    conp = get_conp(xinxiang._name_)
    xinxiang.work(conp, **args)

# 14
def task_xinyang(**args):
    conp = get_conp(xinyang._name_)
    xinyang.work(conp, **args)

# 15
def task_xuchang(**args):
    conp = get_conp(xuchang._name_)
    xuchang.work(conp, **args)

# 16
def task_zhengzhou(**args):
    conp = get_conp(zhengzhou._name_)
    zhengzhou.work(conp, **args)

# 17
def task_zhoukou(**args):
    conp = get_conp(zhoukou._name_)
    zhoukou.work(conp, **args)

# 18
def task_zhumadian(**args):
    conp = get_conp(zhumadian._name_)
    zhumadian.work(conp, **args)



def task_all():
    bg = time.time()
    try:
        task_anyang()
        task_hebi()
        task_henan()
        task_jiaozuo()
        task_kaifeng()

    except:
        print("part1 error!")
    try:
        task_kaifeng()
        task_luohe()
        task_luoyang()
        task_nanyang()
        task_pingdingshan()

    except:
        print("part2 error!")

    try:
        task_puyang()
        task_sanmenxia()
        task_shangqiu()
        task_xinxiang()
        task_xinyang()

    except:
        print("part3 error!")

    try:
        task_xuchang()
        task_zhengzhou()
        task_zhoukou()
        task_zhumadian()

    except:
        print("part4 error!")


    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('zfcg')
    arr = ['anyang','hebi','henan','jiaozuo','kaifeng','luohe',
           'luoyang','nanyang','pingdingshan','puyang','sanmenxia',
           'shangqiu','xinxiang','xinyang','xuchang','zhengzhou','zhoukou','zhumadian']
    for diqu in arr:
        sql = "create schema if not exists %s" % ('henan_' + diqu)
        db_command(sql, dbtype="postgresql", conp=conp)




