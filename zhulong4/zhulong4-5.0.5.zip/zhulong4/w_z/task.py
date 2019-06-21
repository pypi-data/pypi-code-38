import time

from zhulong4.w_z import wzcgzs_95306_cn
from zhulong4.w_z import ysky_dlzb_com
from zhulong4.w_z import zb_crlintex_com
from zhulong4.w_z import zgdxjt_dlzb_com
from zhulong4.w_z import zgdzxx_dlzb_com
from zhulong4.w_z import zghkgy_dlzb_com
from zhulong4.w_z import zghkyl_dlzb_com
from zhulong4.w_z import zgyy_dlzb_com
from zhulong4.w_z import zljt_dlzb_com


from lmf.dbv2 import db_command 


from zhulong4.util.conf import get_conp,get_conp1

#1
def task_ysky_dlzb_com(**args):
    conp=get_conp(ysky_dlzb_com._name_)
    ysky_dlzb_com.work(conp,**args)
#2
def task_zb_crlintex_com(**args):
    conp=get_conp(zb_crlintex_com._name_)
    zb_crlintex_com.work(conp,**args)
#3
def task_zgdxjt_dlzb_com(**args):
    conp=get_conp(zgdxjt_dlzb_com._name_)
    zgdxjt_dlzb_com.work(conp,pageloadtimeout=120,pageLoadStrategy="none",**args)
#4
def task_zgdzxx_dlzb_com(**args):
    conp=get_conp(zgdzxx_dlzb_com._name_)
    zgdzxx_dlzb_com.work(conp,**args)
#5
def task_zghkgy_dlzb_com(**args):
    conp=get_conp(zghkgy_dlzb_com._name_)
    zghkgy_dlzb_com.work(conp,**args)
#6
def task_zghkyl_dlzb_com(**args):
    conp=get_conp(zghkyl_dlzb_com._name_)
    zghkyl_dlzb_com.work(conp,**args)
#7
def task_zgyy_dlzb_com(**args):
    conp=get_conp(zgyy_dlzb_com._name_)
    zgyy_dlzb_com.work(conp,**args)
#8
def task_zljt_dlzb_com(**args):
    conp=get_conp(zljt_dlzb_com._name_)
    zljt_dlzb_com.work(conp,**args)

def task_wzcgzs_95306_cn(**args):
    conp=get_conp(wzcgzs_95306_cn._name_)
    wzcgzs_95306_cn.work(conp,**args)


# def task_all():
#     bg=time.time()

#     try:
#         task_ysky_dlzb_com()
#         task_zb_crlintex_com()
#         task_zgdxjt_dlzb_com()
#         task_zgdzxx_dlzb_com()
#         task_zghkgy_dlzb_com()
#     except:
#         print("part4 error!")
#     try:
#         task_zghkyl_dlzb_com()
#         task_zgyy_dlzb_com()
#         task_zljt_dlzb_com()
#         task_wzcgzs_95306_cn()
#     except:
#         print("part5 error!")

#     ed=time.time()
#     cos=int((ed-bg)/60)

#     print("共耗时%d min"%cos)


# def create_schemas():
#     conp=get_conp1('qycg')
#     arr=['ysky_dlzb_com','zb_crlintex_com','zgdxjt_dlzb_com','zgdzxx_dlzb_com','zghkgy_dlzb_com',
#          'zghkyl_dlzb_com','zgyy_dlzb_com','zljt_dlzb_com','wzcgzs_95306_cn']
#     for diqu in arr:
#         sql="create schema if not exists %s"%diqu
#         db_command(sql,dbtype="postgresql",conp=conp)




