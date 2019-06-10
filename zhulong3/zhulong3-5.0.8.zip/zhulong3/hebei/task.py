from lmf.dbv2 import db_command
import time
from zhulong3.hebei import shenghui
from zhulong3.hebei import langfang
from zhulong3.hebei import shijiazhuang
from zhulong3.hebei import tangshan
from zhulong3.hebei import xingtai
from zhulong3.util.conf import get_conp,get_conp1
# 3
def task_shenghui(**args):
    conp = get_conp(shenghui._name_)
    shenghui.work(conp, num=40, pageloadtimeout=40, **args)

# 4
def task_langfang(**args):
    conp = get_conp(langfang._name_)
    langfang.work(conp, **args)


# 5
def task_shijiazhuang(**args):
    conp = get_conp(shijiazhuang._name_)
    shijiazhuang.work(conp, **args)


# 6
def task_tangshan(**args):
    conp = get_conp(tangshan._name_)
    tangshan.work(conp, **args)


# 7
def task_xingtai(**args):
    conp = get_conp(xingtai._name_)
    xingtai.work(conp,pageloadstrategy='none',pageloadtimeout=40, **args)


def task_all():
    bg = time.time()
    try:
        task_shenghui()
        task_tangshan()
        task_xingtai()
        task_langfang()
        task_shijiazhuang()
    except:
        print("part1 HeBei error!")

    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)

def create_schemas():
    conp = get_conp1('gcjs')
    arr = [
        "hebei_shenghui", "hebei_langfang", "hebei_shijiazhuang",
        "hebei_tangshan", "hebei_xingtai"
    ]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)