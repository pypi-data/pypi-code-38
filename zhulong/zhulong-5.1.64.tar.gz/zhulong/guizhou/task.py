
from zhulong.guizhou import anshun
from zhulong.guizhou import bijie
from zhulong.guizhou import guiyang
from zhulong.guizhou import liupanshui
from zhulong.guizhou import shenghui
from zhulong.guizhou import shenghui2
from zhulong.guizhou import tongren
from zhulong.guizhou import zunyi

##新增
from zhulong.guizhou import qiandong
from zhulong.guizhou import qianxi
from zhulong.guizhou import qiannan


from lmf.dbv2 import db_command


from os.path import join ,dirname
from zhulong.util.conf import get_conp,get_conp1

import time



#1
def task_anshun(**args):
    conp=get_conp(anshun._name_)
    anshun.work(conp,pageloadstrategy='none',**args)

#2
def task_bijie(**args):
    conp=get_conp(bijie._name_)
    bijie.work(conp,**args)

#3
def task_guiyang(**args):
    conp=get_conp(guiyang._name_)
    guiyang.work(conp,**args)

#4
def task_liupanshui(**args):
    conp=get_conp(liupanshui._name_)
    liupanshui.work(conp,**args)

#5
def task_shenghui(**args):
    conp=get_conp(shenghui._name_)
    shenghui.work(conp,**args)

#6
def task_shenghui2(**args):
    conp=get_conp(shenghui2._name_)
    shenghui2.work(conp,**args)

#7
def task_tongren(**args):
    conp=get_conp(tongren._name_)
    tongren.work(conp,**args)

##网站有问题
def task_zunyi(**args):
    conp=get_conp(zunyi._name_)
    zunyi.work(conp,**args)


def task_qiandong(**args):
    conp=get_conp(qiandong._name_)
    qiandong.work(conp,**args)

def task_qianxi(**args):
    conp=get_conp(qianxi._name_)
    qianxi.work(conp,**args)

def task_qiannan(**args):
    conp=get_conp(qiannan._name_)
    qiannan.work(conp,**args)



def task_all():


    task_bijie()
    task_guiyang()
    task_liupanshui()
    task_shenghui()


    task_shenghui2()
    task_tongren()
    task_zunyi()
    task_qiandong()
    task_qiannan()
    task_qianxi()




def create_schemas():
    conp=get_conp1('guizhou')

    arr=["anshun","bijie","guiyang","liupanshui","shenghui","tongren","shenghui2","zunyi",
         "qiandong","qianxi","qiannan" ]#新增
    for diqu in arr:
        sql="create schema if not exists %s"%diqu
        db_command(sql,dbtype="postgresql",conp=conp)



