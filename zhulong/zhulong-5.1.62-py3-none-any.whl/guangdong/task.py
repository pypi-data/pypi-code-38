from zhulong.guangdong import heyuan
from zhulong.guangdong import huizhou
from zhulong.guangdong import jiangmen
from zhulong.guangdong import jieyang
from zhulong.guangdong import meizhou

from zhulong.guangdong import zhanjiang
from zhulong.guangdong import yunfu
from zhulong.guangdong import zhaoqing
from zhulong.guangdong import zhongshan
from zhulong.guangdong import zhuhai

from zhulong.guangdong import yingde
from zhulong.guangdong import lianzhou
from zhulong.guangdong import shaoguan
from zhulong.guangdong import nanxiong
from zhulong.guangdong import sihui

from zhulong.guangdong import guangzhou
from zhulong.guangdong import shenzhen

##新增
from zhulong.guangdong import dongguan
from zhulong.guangdong import qingyuan
from zhulong.guangdong import chaozhou
from zhulong.guangdong import shantou
from zhulong.guangdong import shanwei
from zhulong.guangdong import foshan
from zhulong.guangdong import yangjiang
from zhulong.guangdong import maoming
from zhulong.guangdong import guangdong



from lmf.dbv2 import db_command


from os.path import join ,dirname 
from zhulong.util.conf import get_conp,get_conp1

import time 

#1
def task_heyuan(**args):
    conp=get_conp(heyuan._name_)
    heyuan.work(conp,**args)


#2
def task_huizhou(**args):
    conp=get_conp(huizhou._name_)
    huizhou.work(conp,**args)


#3
def task_jiangmen(**args):
    conp=get_conp(jiangmen._name_)
    jiangmen.work(conp,**args)

#4
def task_jieyang(**args):
    conp=get_conp(jieyang._name_)
    jieyang.work(conp,**args)


#5
def task_meizhou(**args):
    conp=get_conp(meizhou._name_)
    meizhou.work(conp,**args)


#6
def task_yunfu(**args):
    conp=get_conp(yunfu._name_)
    yunfu.work(conp,**args)


#7
def task_zhanjiang(**args):
    conp=get_conp(zhanjiang._name_)
    zhanjiang.work(conp,**args)


#8
def task_zhaoqing(**args):
    conp=get_conp(zhaoqing._name_)
    zhaoqing.work(conp,**args)



#9
def task_zhuhai(**args):
    conp=get_conp(zhuhai._name_)
    zhuhai.work(conp,**args)


#10
def task_zhongshan(**args):
    conp=get_conp(zhongshan._name_)
    zhongshan.work(conp,**args)


#11
def task_yingde(**args):
    conp=get_conp(yingde._name_)
    yingde.work(conp,**args)


#12
def task_lianzhou(**args):
    conp=get_conp(lianzhou._name_)
    lianzhou.work(conp,**args)


#13
def task_shaoguan(**args):
    conp=get_conp(shaoguan._name_)
    shaoguan.work(conp,**args)


#14
def task_nanxiong(**args):
    conp=get_conp(nanxiong._name_)
    nanxiong.work(conp,**args)


#15
def task_sihui(**args):
    conp=get_conp(sihui._name_)
    sihui.work(conp,**args)


#16
def task_guangzhou(**args):
    conp=get_conp(guangzhou._name_)
    guangzhou.work(conp,**args)

#16
def task_shenzhen(**args):
    conp=get_conp(shenzhen._name_)
    shenzhen.work(conp,**args)

def task_dongguan(**args):
    conp=get_conp(dongguan._name_)
    dongguan.work(conp,**args)

def task_qingyuan(**args):
    conp=get_conp(qingyuan._name_)
    qingyuan.work(conp,**args)

def task_chaozhou(**args):
    conp=get_conp(chaozhou._name_)
    chaozhou.work(conp,**args)

def task_shantou(**args):
    conp=get_conp(shantou._name_)
    shantou.work(conp,**args)

def task_shanwei(**args):
    conp=get_conp(shanwei._name_)
    shanwei.work(conp,**args)

def task_foshan(**args):
    conp=get_conp(foshan._name_)
    foshan.work(conp,**args)

def task_yangjiang(**args):
    conp=get_conp(yangjiang._name_)
    yangjiang.work(conp,**args)


def task_maoming(**args):
    conp=get_conp(maoming._name_)
    maoming.work(conp,**args)

def task_guangdong(**args):
    conp=get_conp(guangdong._name_)
    guangdong.work(conp,**args)




def task_all():

    task_heyuan()
    task_huizhou()
    task_jiangmen()
    task_jieyang()
    task_meizhou()


    task_yunfu()
    task_zhanjiang()
    task_zhaoqing()
    task_zhongshan()
    task_zhuhai()

    task_yingde()
    task_lianzhou()
    task_shaoguan()
    task_nanxiong()
    task_sihui()

    task_guangzhou()
    task_dongguan()
    task_chaozhou()
    task_qingyuan()
    task_shantou()
    task_shanwei()
    task_foshan()
    task_yangjiang()
    task_guangdong()





def create_schemas():
    conp=get_conp1('guangdong')
    arr=["heyuan","huizhou","jiangmen","jieyang","meizhou","yunfu"
        ,"zhanjiang","zhaoqing","zhongshan","zhuhai"
        ,"yingde", "lianzhou", "shaoguan", "nanxiong", "sihui","guangzhou","shenzhen"
        ,"dongguan","qingyuan","chaozhou","shantou","shanwei", "foshan", "yangjiang", "maoming","guangdong" ##新增
    ]
    for diqu in arr:
        sql="create schema if not exists %s"%diqu
        db_command(sql,dbtype="postgresql",conp=conp)




