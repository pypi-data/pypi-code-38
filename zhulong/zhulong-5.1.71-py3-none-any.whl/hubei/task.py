from zhulong.hubei import enshi
from zhulong.hubei import huanggang
from zhulong.hubei import huangshi
from zhulong.hubei import jingmen

from zhulong.hubei import shiyan
from zhulong.hubei import suizhou
from zhulong.hubei import xiangyang
from zhulong.hubei import yichang

from zhulong.hubei import lichuan
from zhulong.hubei import yidu 
from zhulong.hubei import dangyang
from zhulong.hubei import wuhan
from zhulong.hubei import xiaogan


from lmf.dbv2 import db_command 


from os.path import join ,dirname 

import time 

from zhulong.util.conf import get_conp,get_conp1

#1
def task_enshi(**args):
    conp=get_conp(enshi._name_)
    enshi.work(conp,**args)

#2
def task_huanggang(**args):
    conp=get_conp(huanggang._name_)
    huanggang.work(conp,**args)

#3
def task_huangshi(**args):
    conp=get_conp(huangshi._name_)
    huangshi.work(conp,**args)

#4
def task_jingmen(**args):
    conp=get_conp(jingmen._name_)
    jingmen.work(conp,**args)

#5
def task_shiyan(**args):
    conp=get_conp(shiyan._name_)
    shiyan.work(conp,**args)

#6
def task_suizhou(**args):
    conp=get_conp(suizhou._name_)
    suizhou.work(conp,**args)

#7
def task_xiangyang(**args):
    conp=get_conp(xiangyang._name_)
    xiangyang.work(conp,**args)

#8
def task_yichang(**args):
    conp=get_conp(yichang._name_)
    yichang.work(conp,**args)

#9
def task_lichuan(**args):
    conp=get_conp(lichuan._name_)
    lichuan.work(conp,**args)

#10
def task_yidu(**args):
    conp=get_conp(yidu._name_)
    yidu.work(conp,**args)

#11
def task_dangyang(**args):
    conp=get_conp(dangyang._name_)
    dangyang.work(conp,**args)

# #11
def task_wuhan(**args):
    conp=get_conp(wuhan._name_)
    wuhan.work(conp, **args)

# #12
def task_xiaogan(**args):
    conp=get_conp(xiaogan._name_)
    xiaogan.work(conp, **args)







def task_all():

    task_enshi()
    task_huanggang()
    task_huangshi()
    task_jingmen()

    task_shiyan()
    task_suizhou()
    task_xiangyang()
    task_yichang()

    task_lichuan()
    task_yidu()
    task_dangyang()
    task_xiaogan()






def create_schemas():
    conp=get_conp1('hubei')
    arr=["enshi","huanggang","huangshi","jingmen","shiyan","suizhou"
        ,"xiangyang","yichang","lichuan","yidu","dangyang","wuhan","xiaogan"
    ]
    for diqu in arr:
        sql="create schema if not exists %s"%diqu
        db_command(sql,dbtype="postgresql",conp=conp)

    
