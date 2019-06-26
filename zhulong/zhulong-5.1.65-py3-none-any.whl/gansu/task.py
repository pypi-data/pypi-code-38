
from zhulong.gansu import baiyin
from zhulong.gansu import dingxi
from zhulong.gansu import jiayuguan
from zhulong.gansu import jiuquan
from zhulong.gansu import lanzhou
from zhulong.gansu import longnan
from zhulong.gansu import pingliang
from zhulong.gansu import qingyang
from zhulong.gansu import tianshui
from zhulong.gansu import wuwei
from zhulong.gansu import zhangye
from zhulong.gansu import gansu


from lmf.dbv2 import db_command


from os.path import join ,dirname
from zhulong.util.conf import get_conp,get_conp1

import time

#1
def task_baiyin(**args):
    conp=get_conp(baiyin._name_)
    baiyin.work(conp,**args)

#2
def task_dingxi(**args):
    conp=get_conp(dingxi._name_)
    dingxi.work(conp,**args)

#3
def task_jiayuguan(**args):
    conp=get_conp(jiayuguan._name_)
    jiayuguan.work(conp,**args)

#4
def task_jiuquan(**args):
    conp=get_conp(jiuquan._name_)
    jiuquan.work(conp,**args)

#5
def task_lanzhou(**args):
    conp=get_conp(lanzhou._name_)
    lanzhou.work(conp,**args)

#6
def task_pingliang(**args):
    conp=get_conp(pingliang._name_)
    pingliang.work(conp,**args)

#7
def task_longnan(**args):
    conp=get_conp(longnan._name_)
    longnan.work(conp,**args)

#8
def task_gansu(**args):
    conp=get_conp(gansu._name_)
    gansu.work(conp,**args)


#9
def task_tianshui(**args):
    conp=get_conp(tianshui._name_)
    tianshui.work(conp,**args)


#10
def task_qingyang(**args):
    conp=get_conp(qingyang._name_)
    qingyang.work(conp,**args)

#11
def task_wuwei(**args):
    conp=get_conp(wuwei._name_)
    wuwei.work(conp,**args)

#12
def task_zhangye(**args):
    conp=get_conp(zhangye._name_)
    zhangye.work(conp,**args)




def task_all():

    task_baiyin()
    task_dingxi()
    task_jiayuguan()
    task_jiuquan()
    task_lanzhou()


    task_pingliang()
    task_longnan()

    task_qingyang()
    task_tianshui()

    task_wuwei()
    task_zhangye()
    task_gansu()





def create_schemas():
    conp=get_conp1('gansu')

    arr=["baiyin","dingxi","gansu","jiayuguan","jiuquan"
        ,"lanzhou","longnan","pingliang"
        ,"qingyang", "tianshui", "wuwei", "zhangye",]
    for diqu in arr:
        sql="create schema if not exists %s"%diqu
        db_command(sql,dbtype="postgresql",conp=conp)


# create_schemas()




