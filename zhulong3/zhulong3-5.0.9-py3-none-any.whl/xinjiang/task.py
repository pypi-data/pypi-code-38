import time

from zhulong3.xinjiang import akesu
from zhulong3.xinjiang import atushi
from zhulong3.xinjiang import bole
from zhulong3.xinjiang import changji
from zhulong3.xinjiang import hami
from zhulong3.xinjiang import kashi
from zhulong3.xinjiang import tacheng
from zhulong3.xinjiang import wulumuqi
from zhulong3.xinjiang import shenghui
from zhulong3.xinjiang import yining


from lmf.dbv2 import db_command

from zhulong3.util.conf import get_conp,get_conp1

#1
def task_akesu(**args):
    conp=get_conp(akesu._name_)
    akesu.work(conp,**args)

#2
def task_atushi(**args):
    conp=get_conp(atushi._name_)
    atushi.work(conp,**args)

#3
def task_bole(**args):
    conp=get_conp(bole._name_)
    bole.work(conp,**args)

#4
def task_changji(**args):
    conp=get_conp(changji._name_)
    changji.work(conp,**args)

#5
def task_hami(**args):
    conp=get_conp(hami._name_)
    hami.work(conp,**args)

#6
def task_kashi(**args):
    conp=get_conp(kashi._name_)
    kashi.work(conp,**args)

#7
def task_tacheng(**args):
    conp=get_conp(tacheng._name_)
    tacheng.work(conp,**args)


#8
def task_wulumuqi(**args):
    conp=get_conp(wulumuqi._name_)
    wulumuqi.work(conp,**args)

#9
def task_shenghui(**args):
    conp=get_conp(shenghui._name_)
    shenghui.work(conp,**args)

#10
def task_yining(**args):
    conp=get_conp(yining._name_)
    yining.work(conp,**args)


def task_all():
    bg=time.time()
    try:
        task_akesu()
        task_atushi()
        task_bole()
        task_changji()
        task_hami()
    except:
        print("part1 error!")

    try:
        task_kashi()
        task_tacheng()
        task_wulumuqi()
        task_shenghui()
        task_yining()
    except:
        print("part2 error!")

    ed=time.time()


    cos=int((ed-bg)/60)

    print("共耗时%d min"%cos)


def create_schemas():
    conp=get_conp1('gcjs')
    arr=["xinjiang_yining","xinjiang_shenghui","xinjiang_wulumuqi","xinjiang_tacheng","xinjiang_kashi",
         "xinjiang_hami","xinjiang_changji","xinjiang_bole","xinjiang_atushi","xinjiang_akesu"]
    for diqu in arr:
        sql="create schema if not exists %s"%diqu
        db_command(sql,dbtype="postgresql",conp=conp)




