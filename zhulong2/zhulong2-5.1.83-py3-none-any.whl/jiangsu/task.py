from zhulong2.jiangsu import shenghui
from zhulong2.jiangsu import changzhou
from zhulong2.jiangsu import huaian
from zhulong2.jiangsu import lianyungang
from zhulong2.jiangsu import nanjing
from zhulong2.jiangsu import nantong
from zhulong2.jiangsu import suqian
from zhulong2.jiangsu import suzhou

from zhulong2.jiangsu import taizhou
from zhulong2.jiangsu import wuxi
from zhulong2.jiangsu import xuzhou
from zhulong2.jiangsu import yangzhou
from zhulong2.jiangsu import xuzhou2
from zhulong2.jiangsu import yancheng
from zhulong2.jiangsu import zhenjiang




from lmf.dbv2 import db_command


from os.path import join ,dirname 

import time 

from zhulong2.util.conf import get_conp,get_conp1

#6
#1
def task_shenghui(**args):
    conp=get_conp(shenghui._name_)
    shenghui.work(conp,**args)
#2
def task_changzhou(**args):
    conp=get_conp(changzhou._name_)
    changzhou.work(conp,**args)
#3
def task_huaian(**args):
    conp=get_conp(huaian._name_)
    huaian.work(conp,**args)
#4
def task_lianyungang(**args):
    conp=get_conp(lianyungang._name_)
    lianyungang.work(conp,**args)
#5
def task_nanjing(**args):
    conp=get_conp(nanjing._name_)
    nanjing.work(conp,**args)


#6
def task_nantong(**args):
    conp=get_conp(nantong._name_)
    nantong.work(conp,**args)
#7
def task_suqian(**args):
    conp=get_conp(suqian._name_)
    suqian.work(conp,**args)
#8
def task_suzhou(**args):
    conp=get_conp(suzhou._name_)
    suzhou.work(conp,**args)
#9
def task_taizhou(**args):
    conp=get_conp(taizhou._name_)
    taizhou.work(conp,**args)
#10
def task_wuxi(**args):
    conp=get_conp(wuxi._name_)
    wuxi.work(conp,**args)


#11
def task_xuzhou(**args):
    conp=get_conp(xuzhou._name_)
    xuzhou.work(conp,**args)
#12
def task_yangzhou(**args):
    conp=get_conp(yangzhou._name_)
    yangzhou.work(conp,**args)


#13
def task_xuzhou2(**args):
    conp=get_conp(xuzhou2._name_)
    xuzhou2.work(conp,**args)


#14
def task_yancheng(**args):
    conp=get_conp(yancheng._name_)
    yancheng.work(conp,**args)
#15
def task_zhenjiang(**args):
    conp=get_conp(zhenjiang._name_)
    zhenjiang.work(conp,**args)





def task_all():
    bg = time.time()
    try:

        task_shenghui()
        task_changzhou()
        task_huaian()
        task_lianyungang()
        task_nanjing()
        task_nantong()
        task_suqian()
        task_suzhou()
        task_taizhou()
        task_xuzhou2()
        task_xuzhou()
        task_zhenjiang()
        task_wuxi()
        task_yancheng()
        task_yangzhou()


    except:
        print("part jiangsu error!")

    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)

def create_schemas():
    conp = get_conp1('zfcg')
    arr = [
        'jiangsu_shenghui',
        'jiangsu_changzhou',
        'jiangsu_huaian',
        'jiangsu_lianyungang',
        'jiangsu_nanjing',
        'jiangsu_nantong',
        'jiangsu_suzhou',
        'jiangsu_suqian',
        'jiangsu_taizhou',
        'jiangsu_wuxi',
        'jiangsu_xuzhou',
        'jiangsu_yangzhou',
        'jiangsu_yancheng',
        'jiangsu_xuzhou2',
        'jiangsu_zhenjiang',
    ]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)
    
