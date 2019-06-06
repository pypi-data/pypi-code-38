import time

from zhulong3.shanxi import ankang
from zhulong3.shanxi import baoji
from zhulong3.shanxi import hanzhong
from zhulong3.shanxi import xian
from zhulong3.shanxi import xianyang
from zhulong3.shanxi import yanan
from zhulong3.shanxi import yulin

from lmf.dbv2 import db_command

from zhulong3.util.conf import get_conp,get_conp1

#1
def task_ankang(**args):
    conp=get_conp(ankang._name_)
    ankang.work(conp,pageloadtimeout=120,pageLoadStrategy="none",**args)

#2
def task_baoji(**args):
    conp=get_conp(baoji._name_)
    baoji.work(conp,**args)

#3
def task_hanzhong(**args):
    conp=get_conp(hanzhong._name_)
    hanzhong.work(conp,**args)

#4
def task_xian(**args):
    conp=get_conp(xian._name_)
    xian.work(conp,**args)

#5
def task_xianyang(**args):
    conp=get_conp(xianyang._name_)
    xianyang.work(conp,**args)

#6
def task_yanan(**args):
    conp=get_conp(yanan._name_)
    yanan.work(conp,**args)

#7
def task_yulin(**args):
    conp=get_conp(yulin._name_)
    yulin.work(conp,**args)


def task_all():
    bg=time.time()
    try:
        task_ankang()
        task_baoji()
        task_hanzhong()
        task_xian()
        task_xianyang()
    except:
        print("part1 error!")

    try:
        task_yanan()
        task_yulin()
    except:
        print("part2 error!")

    ed=time.time()


    cos=int((ed-bg)/60)

    print("共耗时%d min"%cos)


def create_schemas():
    conp=get_conp1('gcjs')
    arr=["shanxi_ankang","shanxi_baoji","shanxi_hanzhong",
         "shanxi_xian","shanxi_xianyang","shanxi_yanan","shanxi_yulin"]
    for diqu in arr:
        sql="create schema if not exists %s"%diqu
        db_command(sql,dbtype="postgresql",conp=conp)




