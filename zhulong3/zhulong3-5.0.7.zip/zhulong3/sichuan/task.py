import time

from zhulong3.sichuan import bazhong
from zhulong3.sichuan import chengdu
from zhulong3.sichuan import mianyang
from zhulong3.sichuan import shenghui
from zhulong3.sichuan import zigong


from lmf.dbv2 import db_command 
from os.path import join ,dirname 

from zhulong3.util.conf import get_conp,get_conp1

#1
def task_bazhong(**args):
    conp=get_conp(bazhong._name_)
    bazhong.work(conp,**args)
#2
def task_chengdu(**args):
    conp=get_conp(chengdu._name_)
    chengdu.work(conp,**args)

#3
def task_mianyang(**args):
    conp=get_conp(mianyang._name_)
    mianyang.work(conp,pageloadtimeout=60,pageLoadStrategy="none",**args)

#4
def task_shenghui(**args):
    conp=get_conp(shenghui._name_)
    shenghui.work(conp,**args)

#5
def task_zigong(**args):
    conp=get_conp(zigong._name_)
    zigong.work(conp,**args)



def task_all():
    bg=time.time()
    try:
        task_bazhong()
        task_chengdu()
        task_mianyang()
        task_shenghui()
        task_zigong()
    except:
        print("part1 error!")


    ed=time.time()


    cos=int((ed-bg)/60)

    print("共耗时%d min"%cos)



def create_schemas():
    conp=get_conp1('gcjs')
    arr=["sichuan_bazhong","sichuan_chengdu","sichuan_mianyang","sichuan_shenghui","sichuan_zigong"]
    for diqu in arr:
        sql="create schema if not exists %s"%diqu
        db_command(sql,dbtype="postgresql",conp=conp)




