from lmf.dbv2 import db_command
import time

from zhulong3.zhejiang import shenghui
from zhulong3.zhejiang import huzhou
from zhulong3.zhejiang import hangzhou
from zhulong3.zhejiang import zhoushan

from zhulong3.zhejiang import jinhua


from zhulong3.util.conf import get_conp,get_conp1




# 28
def task_hangzhou(**args):
    conp = get_conp(hangzhou._name_)
    hangzhou.work(conp, num=25, pageloadtimeout=50,**args)


# 29
def task_zhoushan(**args):
    conp = get_conp(zhoushan._name_)
    zhoushan.work(conp, **args)


# 31
def task_shenghui(**args):
    conp = get_conp(shenghui._name_)
    shenghui.work(conp, **args)

# 32
def task_huzhou(**args):
    conp = get_conp(huzhou._name_)
    huzhou.work(conp,num=30,pageloadtimeout=50, **args)



# 32
def task_jinhua(**args):
    conp = get_conp(jinhua._name_)
    jinhua.work(conp, **args)


def task_all():
    bg = time.time()

    try:
        task_zhoushan()
        task_hangzhou()
        task_shenghui()
        task_huzhou()
        task_jinhua()
    except:
        print("part1 ZheJiang error!")


    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)

def create_schemas():
    conp = get_conp1('gcjs')
    arr = [
        "zhejiang_hangzhou", "zhejiang_zhoushan","zhejiang_shenghui", "zhejiang_huzhou"
        , "zhejiang_jinhua"
    ]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)