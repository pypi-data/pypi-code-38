import time

from zhulong2.guangdong import dongguan
from zhulong2.guangdong import guangzhou
from zhulong2.guangdong import shenghui
from zhulong2.guangdong import shenzhen
# 新增
from zhulong2.guangdong import shantou
from zhulong2.guangdong import zhongshan

from lmf.dbv2 import db_command

from zhulong2.util.conf import get_conp,get_conp1

#1
def task_dongguan(**args):
    conp=get_conp(dongguan._name_)
    dongguan.work(conp,**args)

#2
def task_shenghui(**args):
    conp=get_conp(shenghui._name_)
    shenghui.work(conp,pageloadtimeout=120,interval_page=100,**args)

#3
def task_guangzhou(**args):
    conp=get_conp(guangzhou._name_)
    guangzhou.work(conp,**args)

#4
def task_shenzhen(**args):
    conp=get_conp(shenzhen._name_)
    shenzhen.work(conp,**args)

#5
def task_shantou(**args):
    conp=get_conp(shantou._name_)
    shantou.work(conp,**args)

#6
def task_zhongshan(**args):
    conp=get_conp(zhongshan._name_)
    zhongshan.work(conp,**args)

def task_all():
    bg=time.time()
    try:
        task_dongguan()
        task_guangzhou()
        task_shenghui()
        task_shenzhen()
        task_shantou()
        task_zhongshan()
    except:
        print("part1 error!")

    ed=time.time()
    cos=int((ed-bg)/60)
    print("共耗时%d min"%cos)


def create_schemas():
    conp=get_conp1('zfcg')
    arr=["guangdong_shenghui","guangdong_dongguan","guangdong_guangzhou",
         "guangdong_shenzhen","guangdong_shantou","guangdong_zhongshan"]
    for diqu in arr:
        sql="create schema if not exists %s"%diqu
        db_command(sql,dbtype="postgresql",conp=conp)




