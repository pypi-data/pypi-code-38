import time

from zhulong4.www_q_z import www_qhbidding_com
from zhulong4.www_q_z import www_sinochemitc_com
from zhulong4.www_q_z import www_sztc_com
from zhulong4.www_q_z import www_wiscobidding_com_cn
from zhulong4.www_q_z import www_ykjtzb_com
from zhulong4.www_q_z import www_zeec_cn
from zhulong4.www_q_z import www_zmzb_com





from lmf.dbv2 import db_command 
from os.path import join ,dirname 

from zhulong4.util.conf import get_conp,get_conp1

#1
def task_www_qhbidding_com(**args):
    conp=get_conp(www_qhbidding_com._name_)
    www_qhbidding_com.work(conp,**args)

#2
def task_www_sinochemitc_com(**args):
    conp=get_conp(www_sinochemitc_com._name_)
    www_sinochemitc_com.work(conp,**args)

#3
def task_www_sztc_com(**args):
    conp=get_conp(www_sztc_com._name_)
    www_sztc_com.work(conp,pageloadtimeout=120,pageLoadStrategy="none",**args)

#4
def task_www_wiscobidding_com_cn(**args):
    conp=get_conp(www_wiscobidding_com_cn._name_)
    www_wiscobidding_com_cn.work(conp,**args)

#5
def task_www_ykjtzb_com(**args):
    conp=get_conp(www_ykjtzb_com._name_)
    www_ykjtzb_com.work(conp,**args)

#6
def task_www_zeec_cn(**args):
    conp=get_conp(www_zeec_cn._name_)
    www_zeec_cn.work(conp,**args)

#7
def task_www_zmzb_com(**args):
    conp=get_conp(www_zmzb_com._name_)
    www_zmzb_com.work(conp,pageloadtimeout=120,pageLoadStrategy="none",**args)



# def task_all():
#     bg=time.time()

#     try:
#         task_www_zmzb_com()
#         task_www_qhbidding_com()
#         task_www_sinochemitc_com()
#     except:
#         print("part1 error!")
#     try:
#         task_www_sztc_com()
#         task_www_wiscobidding_com_cn()
#         task_www_ykjtzb_com()
#         task_www_zeec_cn()

#     except:
#         print("part2 error!")

#     ed=time.time()
#     cos=int((ed-bg)/60)

#     print("共耗时%d min"%cos)



# def create_schemas():
#     conp=get_conp1('qycg')
#     arr=['www_qhbidding_com','www_sinochemitc_com','www_sztc_com',
#          'www_wiscobidding_com_cn','www_ykjtzb_com','www_zeec_cn','www_zmzb_com']
#     for diqu in arr:
#         sql="create schema if not exists %s"%diqu
#         db_command(sql,dbtype="postgresql",conp=conp)




