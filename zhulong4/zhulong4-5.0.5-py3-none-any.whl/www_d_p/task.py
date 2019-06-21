import time

from zhulong4.www_d_p import www_dlswzb_com
from zhulong4.www_d_p import www_dlzb_com
from zhulong4.www_d_p import www_dlzb_com_c1608
from zhulong4.www_d_p import www_dlztb_com
from zhulong4.www_d_p import www_gmgitc_com
from zhulong4.www_d_p import www_mgzbzx_com
from zhulong4.www_d_p import www_ngecc_com
from zhulong4.www_d_p import www_namkwong_com_mo



from lmf.dbv2 import db_command 
from os.path import join ,dirname 

from zhulong4.util.conf import get_conp,get_conp1


#1
def task_www_dlswzb_com(**args):
    conp=get_conp(www_dlswzb_com._name_)
    www_dlswzb_com.work(conp,pageloadtimeout=120,pageLoadStrategy="none",**args)
#2
def task_www_namkwong_com_mo(**args):
    conp=get_conp(www_namkwong_com_mo._name_)
    www_namkwong_com_mo.work(conp,**args)
#3
def task_www_dlzb_com(**args):
    conp=get_conp(www_dlzb_com._name_)
    www_dlzb_com.work(conp,pageloadtimeout=120,pageLoadStrategy="none",**args)
#4
def task_www_dlzb_com_c1608(**args):
    conp=get_conp(www_dlzb_com_c1608._name_)
    www_dlzb_com_c1608.work(conp,**args)
#5
def task_www_dlztb_com(**args):
    conp=get_conp(www_dlztb_com._name_)
    www_dlztb_com.work(conp,**args)
#6
def task_www_gmgitc_com(**args):
    conp=get_conp(www_gmgitc_com._name_)
    www_gmgitc_com.work(conp,**args)
#7
def task_www_mgzbzx_com(**args):
    conp=get_conp(www_mgzbzx_com._name_)
    www_mgzbzx_com.work(conp,pageloadtimeout=120,pageLoadStrategy="none",**args)
#8
def task_www_ngecc_com(**args):
    conp=get_conp(www_ngecc_com._name_)
    www_ngecc_com.work(conp,**args)

# def task_all():
#     bg=time.time()
#     try:
#         task_www_dlswzb_com()
#         task_www_dlzb_com()
#         task_www_dlzb_com_c1608()
#         task_www_dlztb_com()
#     except:
#         print("part1 error!")
#     try:
#         task_www_gmgitc_com()
#         task_www_mgzbzx_com()
#         task_www_ngecc_com()
#         task_www_namkwong_com_mo()

#     except:
#         print("part2 error!")

#     ed=time.time()
#     cos=int((ed-bg)/60)

#     print("共耗时%d min"%cos)


# def create_schemas():
#     conp=get_conp1('qycg')
#     arr=['www_dlswzb_com','www_dlzb_com','www_dlzb_com_c1608','www_dlztb_com',
#          'www_gmgitc_com','www_mgzbzx_com','www_ngecc_com','www_namkwong_com_mo']
#     for diqu in arr:
#         sql="create schema if not exists %s"%diqu
#         db_command(sql,dbtype="postgresql",conp=conp)






