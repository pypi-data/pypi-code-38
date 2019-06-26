from lmf.dbv2 import db_command
import time
from zhulong.neimenggu import baotou

from zhulong.neimenggu import bayannaoer

from zhulong.neimenggu import chifeng

from zhulong.neimenggu import eeduosi

from zhulong.neimenggu import huhehaote

from zhulong.neimenggu import hulunbeier

from zhulong.neimenggu import manzhouli

from zhulong.neimenggu import xinganmeng

from zhulong.neimenggu import tongliao

from zhulong.neimenggu import wuhai

from zhulong.neimenggu import wulanchabu

from zhulong.neimenggu import xilinguolemeng

from zhulong.neimenggu import neimenggu
from zhulong.neimenggu import alashan



from os.path import join, dirname


from zhulong.util.conf import get_conp,get_conp1


# 1
def task_baotou(**args):
    conp = get_conp(baotou._name_)
    baotou.work(conp, **args)


# 2
def task_bayannaoer(**args):
    conp = get_conp(bayannaoer._name_)
    bayannaoer.work(conp, **args)


# 3
def task_hulunbeier(**args):
    conp = get_conp(hulunbeier._name_)
    hulunbeier.work(conp, **args)


# 4
def task_chifeng(**args):
    conp = get_conp(chifeng._name_)
    chifeng.work(conp, **args)


# 5
def task_eeduosi(**args):
    conp = get_conp(eeduosi._name_)
    eeduosi.work(conp, **args)


# 6
def task_huhehaote(**args):
    conp = get_conp(huhehaote._name_)
    huhehaote.work(conp, **args)


# 7
def task_manzhouli(**args):
    conp = get_conp(manzhouli._name_)
    manzhouli.work(conp, **args)


# 8
def task_xinganmeng(**args):
    conp = get_conp(xinganmeng._name_)
    xinganmeng.work(conp, **args)


# 9
def task_tongliao(**args):
    conp = get_conp(tongliao._name_)
    tongliao.work(conp, **args)


# 10
def task_wuhai(**args):
    conp = get_conp(wuhai._name_)
    wuhai.work(conp, **args)


# 11



# 12
def task_wulanchabu(**args):
    conp = get_conp(wulanchabu._name_)
    wulanchabu.work(conp, **args)


# 13
def task_xilinguolemeng(**args):
    conp = get_conp(xilinguolemeng._name_)
    xilinguolemeng.work(conp, **args)


# 14
def task_neimenggu(**args):
    conp = get_conp(neimenggu._name_)
    neimenggu.work(conp, **args)


# 15
def task_alashan(**args):
    conp = get_conp(alashan._name_)
    alashan.work(conp, **args)



# 16



# 17



# 18



def task_all():
    bg = time.time()
    try:
        task_baotou()
        task_bayannaoer()
        task_hulunbeier()
        task_chifeng()
        task_eeduosi()
    except:
        print("part1 error!")

    try:
        task_huhehaote()
        task_manzhouli()
        task_xinganmeng()
        task_tongliao()
        task_wuhai()
    except:
        print("part2 error!")

    try:
        task_wulanchabu()
        task_xilinguolemeng()
        task_xinganmeng()
        task_alashan()
    except:
        print("part3 error!")



    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('neimenggu')

    arr = [
        "baotou", "bayannaoer", "chifeng", "eeduosi", "huhehaote",
        "hulunbeier", "manzhouli", "xinganmeng", "tongliao", "wuhai",
        "wulanchabu", "xilinguolemeng", "xinganmeng",'alashan'
    ]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)

