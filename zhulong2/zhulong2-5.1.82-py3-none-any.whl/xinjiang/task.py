import time
from zhulong2.xinjiang import akesu
from zhulong2.xinjiang import alashankou
from zhulong2.xinjiang import changji
from zhulong2.xinjiang import hetian
from zhulong2.xinjiang import kashi
from zhulong2.xinjiang import kelamayi
from zhulong2.xinjiang import tacheng
from zhulong2.xinjiang import tulufan
from zhulong2.xinjiang import wulumuqi
from zhulong2.xinjiang import shenghui
from zhulong2.xinjiang import shenghui2
from zhulong2.xinjiang import yining
# 新增
from zhulong2.xinjiang import changji2

from lmf.dbv2 import db_command

from zhulong2.util.conf import get_conp,get_conp1

#1
def task_akesu(**args):
    conp=get_conp(akesu._name_)
    akesu.work(conp,pageloadtimeout=120,**args)

#2
def task_alashankou(**args):
    conp=get_conp(alashankou._name_)
    alashankou.work(conp,**args)

#3
def task_changji(**args):
    conp=get_conp(changji._name_)
    changji.work(conp,**args)

#4
def task_hetian(**args):
    conp=get_conp(hetian._name_)
    hetian.work(conp,**args)

#5
def task_kashi(**args):
    conp=get_conp(kashi._name_)
    kashi.work(conp,pageloadtimeout=120,**args)

#6
def task_kelamayi(**args):
    conp=get_conp(kelamayi._name_)
    kelamayi.work(conp,pageloadtimeout=120,**args)


#8
def task_tacheng(**args):
    conp=get_conp(tacheng._name_)
    tacheng.work(conp,pageloadtimeout=120,**args)

#9
def task_tulufan(**args):
    conp=get_conp(tulufan._name_)
    tulufan.work(conp,pageloadtimeout=120,**args)
#10
def task_wulumuqi(**args):
    conp=get_conp(wulumuqi._name_)
    wulumuqi.work(conp,**args)

#11
def task_shenghui(**args):
    conp=get_conp(shenghui._name_)
    shenghui.work(conp,pageloadtimeout=120,**args)

#12
def task_shenghui2(**args):
    conp=get_conp(shenghui2._name_)
    shenghui2.work(conp,pageloadtimeout=120,**args)

#13
def task_yining(**args):
    conp=get_conp(yining._name_)
    yining.work(conp,pageloadtimeout=120,**args)

#14
def task_changji2(**args):
    conp=get_conp(changji2._name_)
    changji2.work(conp,**args)



def task_all():
    bg=time.time()
    try:
        task_akesu()
        task_alashankou()
        task_shenghui()
        task_shenghui2()
        task_changji()
        task_hetian()
    except:
        print("part1 error!")

    try:
        task_wulumuqi()
        task_kashi()
        task_kelamayi()
        task_tacheng()
        task_tulufan()
        task_yining()
        task_changji2()
    except:
        print("part2 error!")

    ed=time.time()
    cos=int((ed-bg)/60)
    print("共耗时%d min"%cos)


def create_schemas():
    conp=get_conp1('zfcg')
    arr=["xinjiang_akesu","xinjiang_alashankou","xinjiang_shenghui","xinjiang_shenghui2","xinjiang_changji",
         "xinjiang_hetian","xinjiang_wulumuqi","xinjiang_kashi","xinjiang_kelamayi",
        "xinjiang_tacheng", "xinjiang_tulufan", "xinjiang_yining","xinjiang_changji2"]
    for diqu in arr:
        sql="create schema if not exists %s"%diqu
        db_command(sql,dbtype="postgresql",conp=conp)




