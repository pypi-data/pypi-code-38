import time

from zhulong.hainan import danzhou

from zhulong.hainan import dongfang

from zhulong.hainan import haikou

from zhulong.hainan import hainan

from zhulong.hainan import qionghai

from zhulong.hainan import sansha

from zhulong.hainan import sanya

from lmf.dbv2 import db_command 
from os.path import join ,dirname 

from zhulong.util.conf import get_conp,get_conp1

#1
def task_danzhou(**args):
    conp=get_conp(danzhou._name_)
    danzhou.work(conp,**args)
#2
def task_dongfang(**args):
    conp=get_conp(dongfang._name_)
    dongfang.work(conp,**args)
#3
def task_haikou(**args):
    conp=get_conp(haikou._name_)
    haikou.work(conp,pageloadtimeout=60,**args)


#4
def task_hainan(**args):
    conp=get_conp(hainan._name_)
    hainan.work(conp,**args)
#5
def task_qionghai(**args):
    conp=get_conp(qionghai._name_)
    qionghai.work(conp,**args)
#6
def task_sansha(**args):
    conp=get_conp(sansha._name_)
    sansha.work(conp,**args)


#7
def task_sanya(**args):
    conp=get_conp(sanya._name_)
    sanya.work(conp,**args)

def task_all():
    bg=time.time()
    try:
        task_danzhou()
        task_dongfang()
        task_haikou()
        task_hainan()
        task_qionghai()
    except:
        print("part1 error!")

    try:
        task_sansha()
        task_sanya()
    except:
        print("part2 error!")


    ed=time.time()


    cos=int((ed-bg)/60)

    print("共耗时%d min"%cos)




def create_schemas():
    conp=get_conp1('hainan')
    arr=["danzhou","dongfang","haikou","hainan","qionghai",
         "sansha","sanya"]
    for diqu in arr:
        sql="create schema if not exists %s"%diqu
        db_command(sql,dbtype="postgresql",conp=conp)




