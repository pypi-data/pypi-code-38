import time

from zhulong.shanxi import shanxi

from zhulong.shanxi import xian

# from zhulong.shanxi import yanan

from zhulong.shanxi import weinan

from zhulong.shanxi import xianyang

from zhulong.shanxi import chenzhou


from lmf.dbv2 import db_command 
from os.path import join ,dirname 
from zhulong.util.conf import get_conp


#1

def task_shanxi(**args):
    conp=get_conp(shanxi._name_)
    shanxi.work(conp,**args)
#2
def task_xian(**args):
    conp=get_conp(xian._name_)
    xian.work(conp,**args)
#3
# def task_yanan(**args):
#     conp=get_conp(yanan._name_)
#     yanan.work(conp,**args)

#4
def task_weinan(**args):
    conp=get_conp(weinan._name_)
    weinan.work(conp,pageloadtimeout=60,pageLoadStrategy="none",**args)

#5
def task_xianyang(**args):
    conp=get_conp(xianyang._name_)
    xianyang.work(conp,**args)

#6
def task_chenzhou(**args):
    conp=get_conp(chenzhou._name_)
    chenzhou.work(conp,**args)


def task_all():
    bg=time.time()
    try:
        task_shanxi()
        task_xian()
        # task_yanan()
        task_weinan()
        task_xianyang()
        task_chenzhou()
    except:
        print("part1 error!")

    ed=time.time()


    cos=int((ed-bg)/60)

    print("共耗时%d min"%cos)


#write_profile('postgres,since2015,127.0.0.1,shandong')



def create_schemas():
    conp=get_conp('shanxi')
    arr=["shanxi","xian","yanan","weinan","xianyang",
         "chenzhou"
    ]
    for diqu in arr:
        sql="create schema if not exists %s"%diqu
        db_command(sql,dbtype="postgresql",conp=conp)




