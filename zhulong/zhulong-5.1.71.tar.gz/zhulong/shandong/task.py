import time

from zhulong.shandong import anqiu

from zhulong.shandong import binzhou

from zhulong.shandong import dezhou

from zhulong.shandong import dongying

from zhulong.shandong import feicheng

from zhulong.shandong import jiaozhou

from zhulong.shandong import jinan

from zhulong.shandong import laiwu

from zhulong.shandong import leling

from zhulong.shandong import linqing

from zhulong.shandong import linyi

from zhulong.shandong import pingdu

from zhulong.shandong import qingdao

from zhulong.shandong import rizhao

from zhulong.shandong import rongcheng

from zhulong.shandong import rushan

from zhulong.shandong import shandong

from zhulong.shandong import taian

from zhulong.shandong import tengzhou

from zhulong.shandong import weifang

from zhulong.shandong import weihai

from zhulong.shandong import xintai

from zhulong.shandong import yantai

from zhulong.shandong import zaozhuang

from zhulong.shandong import zibo

from zhulong.shandong import qufu

from zhulong.shandong import jining

from zhulong.shandong import yucheng

from zhulong.shandong import zoucheng

from zhulong.shandong import liaocheng

from zhulong.shandong import heze
# 新增
from zhulong.shandong import shandong2


from lmf.dbv2 import db_command
from os.path import join ,dirname

# import time


#1
from zhulong.util.conf import get_conp,get_conp1


def task_anqiu(**args):
    conp=get_conp(anqiu._name_)
    anqiu.work(conp,**args)
#2
def task_binzhou(**args):
    conp=get_conp(binzhou._name_)
    binzhou.work(conp, pageloadtimeout=180,**args)
#3
def task_dezhou(**args):
    conp=get_conp(dezhou._name_)
    dezhou.work(conp,**args,pageloadtimeout=120,pageLoadStrategy="none")

#4
def task_dongying(**args):
    conp=get_conp(dongying._name_)
    dongying.work(conp, **args)

#5
def task_feicheng(**args):
    conp=get_conp(feicheng._name_)
    feicheng.work(conp,**args)
#6
def task_jiaozhou(**args):
    conp=get_conp(jiaozhou._name_)
    jiaozhou.work(conp,**args)


#7
def task_jinan(**args):
    conp=get_conp(jinan._name_)
    jinan.work(conp,**args)
#8
def task_laiwu(**args):
    conp=get_conp(laiwu._name_)
    laiwu.work(conp,pageloadtimeout=180,pageLoadStrategy="none",**args)
#9
def task_leling(**args):
    conp=get_conp(leling._name_)
    leling.work(conp,**args)


#10
def task_linqing(**args):
    conp=get_conp(linqing._name_)
    linqing.work(conp,**args)
#11
def task_linyi(**args):
    conp=get_conp(linyi._name_)
    linyi.work(conp,**args)
#12
def task_pingdu(**args):
    conp=get_conp(pingdu._name_)
    pingdu.work(conp,**args)

#13
def task_qingdao(**args):
    conp=get_conp(qingdao._name_)
    qingdao.work(conp,**args)
#14
def task_rizhao(**args):
    conp=get_conp(rizhao._name_)
    rizhao.work(conp,**args)
#15
def task_rongcheng(**args):
    conp=get_conp(rongcheng._name_)
    rongcheng.work(conp,**args)

#16
def task_rushan(**args):
    conp=get_conp(rushan._name_)
    rushan.work(conp,**args)
#17
def task_shandong(**args):
    conp=get_conp(shandong._name_)
    shandong.work(conp,**args)
#18
def task_taian(**args):
    conp=get_conp(taian._name_)
    taian.work(conp,**args)

#19
def task_tengzhou(**args):
    conp=get_conp(tengzhou._name_)
    tengzhou.work(conp,**args)
#20
def task_weifang(**args):
    conp=get_conp(weifang._name_)
    weifang.work(conp,**args)

#21
def task_weihai(**args):
    conp=get_conp(weihai._name_)
    weihai.work(conp,**args)
#22
def task_xintai(**args):
    conp=get_conp(xintai._name_)
    xintai.work(conp,**args)

#23
def task_yantai(**args):
    conp=get_conp(yantai._name_)
    yantai.work(conp,**args)

#24
def task_zaozhuang(**args):
    conp=get_conp(zaozhuang._name_)
    zaozhuang.work(conp,**args)

#25

def task_zibo(**args):
    conp=get_conp(zibo._name_)
    zibo.work(conp,**args)

#26

def task_jining(**args):
    conp=get_conp(jining._name_)
    jining.work(conp,**args)

#27

def task_qufu(**args):
    conp=get_conp(qufu._name_)
    qufu.work(conp,**args)

#28

def task_yucheng(**args):
    conp=get_conp(yucheng._name_)
    yucheng.work(conp,**args)


#29

def task_zoucheng(**args):
    conp=get_conp(zoucheng._name_)
    zoucheng.work(conp,**args)

#30

def task_liaocheng(**args):
    conp=get_conp(liaocheng._name_)
    liaocheng.work(conp,**args)

#31

def task_heze(**args):
    conp=get_conp(heze._name_)
    heze.work(conp,pageloadtimeout=120,pageLoadStrategy="none",num=1,**args)

#32

def task_shandong2(**args):
    conp=get_conp(shandong2._name_)
    shandong2.work(conp,pageloadtimeout=120)


def task_all():
    bg=time.time()
    try:
        task_anqiu()
        task_binzhou()
        task_dezhou()
        task_dongying()
        task_feicheng()
    except:
        print("part1 error!")

    try:
        task_jiaozhou()
        task_jinan()
        task_laiwu()
        task_leling()
        task_linqing()
    except:
        print("part2 error!")

    try:
        task_linyi()
        task_pingdu()
        task_qingdao()
        task_rizhao()
        task_rongcheng()
    except:
        print("part3 error!")

    try:
        task_rushan()
        task_shandong()
        task_taian()
        task_tengzhou()
        task_weifang()
    except:
        print("part4 error!")

    try:
        task_weihai()
        task_xintai()
        task_yantai()
        task_zaozhuang()
        task_zibo()
    except:
        print("part5 error!")

    try:
        task_jining()
        task_qufu()
        task_yucheng()
        task_zoucheng()
        task_liaocheng()
        task_heze()
        task_shandong2()
    except:
        print("part6 error!")

    ed=time.time()


    cos=int((ed-bg)/60)

    print("共耗时%d min"%cos)


#write_profile('postgres,since2015,127.0.0.1,shandong')



def create_schemas():
    conp=get_conp1('shandong')
    arr=["anqiu","binzhou","dongying","feicheng","jiaozhou",
         "dezhou","jinan","laiwu","leling","linqing",
         "pingdu","qingdao","rizhao","rongcheng","rushan",
        "shandong","taian","tengzhou","weifang","weihai",
        "xintai","yantai","zaozhuang","zibo","linyi",
         "jining", "qufu", "yucheng", "zoucheng", "liaocheng",
         "heze","shandong2"
    ]
    for diqu in arr:
        sql="create schema if not exists %s"%diqu
        db_command(sql,dbtype="postgresql",conp=conp)




