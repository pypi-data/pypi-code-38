import time

from zhulong.zhejiang import cixi

from zhulong.zhejiang import dongyang

from zhulong.zhejiang import hangzhou

from zhulong.zhejiang import huzhou

from zhulong.zhejiang import jiaxing

from zhulong.zhejiang import jinhua

from zhulong.zhejiang import linhai

from zhulong.zhejiang import lishui

from zhulong.zhejiang import ningbo

from zhulong.zhejiang import pinghu

from zhulong.zhejiang import quzhou

from zhulong.zhejiang import ruian

from zhulong.zhejiang import shaoxing

from zhulong.zhejiang import shengzhou

from zhulong.zhejiang import taizhou

from zhulong.zhejiang import tongxiang

from zhulong.zhejiang import wenling

from zhulong.zhejiang import wenzhou

from zhulong.zhejiang import yiwu

from zhulong.zhejiang import yueqing

from zhulong.zhejiang import yuhuan

from zhulong.zhejiang import zhejiang

from zhulong.zhejiang import zhoushan

from zhulong.zhejiang import zhuji

from zhulong.zhejiang import longquan

from lmf.dbv2 import db_command 
from os.path import join ,dirname 

from zhulong.util.conf import get_conp,get_conp1


#1
def task_cixi(**args):
    conp=get_conp(cixi._name_)
    cixi.work(conp,pageloadtimeout=180,**args)
#2
def task_dongyang(**args):
    conp=get_conp(dongyang._name_)
    dongyang.work(conp,pageloadtimeout=180,**args)
#3
def task_hangzhou(**args):
    conp=get_conp(hangzhou._name_)
    hangzhou.work(conp,**args)


#4
def task_huzhou(**args):
    conp=get_conp(huzhou._name_)
    huzhou.work(conp,**args)
#5
def task_jiaxing(**args):
    conp=get_conp(jiaxing._name_)
    jiaxing.work(conp,**args)
#6
def task_jinhua(**args):
    conp=get_conp(jinhua._name_)
    jinhua.work(conp,pageloadtimeout=120,**args)


#7
def task_linhai(**args):
    conp=get_conp(linhai._name_)
    linhai.work(conp,pageloadtimeout=240, pageLoadStrategy="none",**args)
#8
def task_lishui(**args):
    conp=get_conp(lishui._name_)
    lishui.work(conp,pageloadtimeout=180,**args)

#9
def task_longquan(**args):
    conp=get_conp(longquan._name_)
    longquan.work(conp,**args)

#10
def task_ningbo(**args):
    conp=get_conp(ningbo._name_)
    ningbo.work(conp,pageloadtimeout=240,**args)
#11
def task_pinghu(**args):
    conp=get_conp(pinghu._name_)
    pinghu.work(conp,**args)
#12
def task_quzhou(**args):
    conp=get_conp(quzhou._name_)
    quzhou.work(conp,**args)

#13
def task_ruian(**args):
    conp=get_conp(ruian._name_)
    ruian.work(conp,**args)
#14
def task_shaoxing(**args):
    conp=get_conp(shaoxing._name_)
    shaoxing.work(conp,**args)
#15
def task_shengzhou(**args):
    conp=get_conp(shengzhou._name_)
    shengzhou.work(conp,**args)

#16
def task_taizhou(**args):
    conp=get_conp(taizhou._name_,'zhejiang')
    taizhou.work(conp,**args)
#17
def task_tongxiang(**args):
    conp=get_conp(tongxiang._name_)
    tongxiang.work(conp,**args)
#18
def task_wenling(**args):
    conp=get_conp(wenling._name_)
    wenling.work(conp,**args)

#19
def task_wenzhou(**args):
    conp=get_conp(wenzhou._name_)
    wenzhou.work(conp,pageloadtimeout=120,**args)
#20
def task_yiwu(**args):
    conp=get_conp(yiwu._name_)
    yiwu.work(conp,**args)

#21
def task_yueqing(**args):
    conp=get_conp(yueqing._name_)
    yueqing.work(conp,**args)
#22
def task_yuhuan(**args):
    conp=get_conp(yuhuan._name_)
    yuhuan.work(conp,pageloadtimeout=180,**args)

#23
def task_zhejiang(**args):
    conp=get_conp(zhejiang._name_)
    zhejiang.work(conp,**args)

#24
def task_zhoushan(**args):
    conp=get_conp(zhoushan._name_)
    zhoushan.work(conp,**args)

#25

def task_zhuji(**args):
    conp=get_conp(zhuji._name_)
    zhuji.work(conp,**args)





def task_all():
    bg=time.time()
    try:
        task_cixi()
        task_dongyang()
        task_hangzhou()
        task_huzhou()
        task_jiaxing()
    except:
        print("part1 error!")

    try:
        task_jinhua()
        task_linhai()
        task_lishui()
        task_ningbo()
    except:
        print("part2 error!")

    try:
        task_pinghu()
        task_quzhou()
        task_ruian()
        task_shaoxing()
        task_shengzhou()
    except:
        print("part3 error!")

    try:

        task_taizhou()
        task_tongxiang()
        task_wenling()
        task_wenzhou()
        task_yiwu()
    except:
        print("part4 error!")

    try:
        task_yueqing()
        task_yuhuan()
        task_zhejiang()
        task_zhoushan()
        task_zhuji()
    except:
        print("part5 error!")

    ed=time.time()


    cos=int((ed-bg)/60)

    print("共耗时%d min"%cos)


#write_profile('postgres,since2015,127.0.0.1,shandong')



def create_schemas():
    conp=get_conp1('zhejiang')
    arr=["cixi","dongyang","hangzhou","huzhou","jiaxing",
         "jinhua","linhai","lishui","ningbo",
         "pinghu","quzhou","ruian","shaoxing","shengzhou",
        "taizhou","tongxiang","wenling","wenzhou","yiwu",
        "yueqing","yuhuan","zhejiang","zhoushan","zhuji"
    ]
    for diqu in arr:
        sql="create schema if not exists %s"%diqu
        db_command(sql,dbtype="postgresql",conp=conp)




