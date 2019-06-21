import time

from zhulong.shanxi import shanxi

from zhulong.shanxi import xian

from zhulong.shanxi import yanan

from zhulong.shanxi import weinan

from zhulong.shanxi import xianyang

from zhulong.shanxi import chenzhou
# 新增
from zhulong.shanxi import ankang
from zhulong.shanxi import xianyang2

from lmf.dbv2 import db_command 
from os.path import join ,dirname 
from zhulong.util.conf import get_conp1,get_conp


#1

def task_shanxi(**args):
    conp=get_conp(shanxi._name_,'shanxi')
    shanxi.work(conp,**args)
#2
def task_xian(**args):
    conp=get_conp(xian._name_,'shanxi')
    xian.work(conp,**args)
#3
def task_yanan(**args):
    conp=get_conp(yanan._name_,'shanxi')
    yanan.work(conp,**args)

#4
def task_weinan(**args):
    conp=get_conp(weinan._name_,'shanxi')
    weinan.work(conp,pageloadtimeout=60,pageLoadStrategy="none",**args)

#5
def task_xianyang(**args):
    conp=get_conp(xianyang._name_,'shanxi')
    xianyang.work(conp,**args)

#6
def task_chenzhou(**args):
    conp=get_conp(chenzhou._name_,'shanxi')
    chenzhou.work(conp,**args)

#7
def task_ankang(**args):
    conp=get_conp(ankang._name_,'shanxi')
    ankang.work(conp,**args)

#8
def task_xianyang2(**args):
    conp=get_conp(xianyang2._name_,'shanxi')
    xianyang2.work(conp,**args)


def task_all():
    bg=time.time()
    try:
        task_shanxi()
        task_xian()
        task_yanan()
        task_weinan()
        task_xianyang()
    except:
        print("part1 error!")

    try:
        task_chenzhou()
        task_ankang()
        task_xianyang2()
    except:
        print("part1 error!")


    ed=time.time()


    cos=int((ed-bg)/60)

    print("共耗时%d min"%cos)


#write_profile('postgres,since2015,127.0.0.1,shandong')



def create_schemas():
    conp=get_conp1('shanxi')
    print(conp)
    arr=["shanxi","xian","yanan","weinan","xianyang",
         "chenzhou","ankang","xianyang2"
    ]
    for diqu in arr:
        sql="create schema if not exists %s"%diqu
        db_command(sql,dbtype="postgresql",conp=conp)



# create_schemas()
