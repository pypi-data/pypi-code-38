from lmf.dbv2 import db_command
import time
from zhulong4.c_d import caigou_ceair_com
from zhulong4.c_d import csbidding_csair_com
from zhulong4.c_d import dfqcgs_dlzb_com
from zhulong4.c_d import dzzb_ciesco_com_cn


from zhulong4.util.conf import get_conp, get_conp1


# 1
def task_caigou_ceair_com(**args):
    conp = get_conp(caigou_ceair_com._name_)
    caigou_ceair_com.work(conp, pageloadstrategy="none", pageloadtimeout=40, **args)


# 2
def task_csbidding_csair_com(**args):
    conp = get_conp(csbidding_csair_com._name_)
    csbidding_csair_com.work(conp, **args)


# 3
def task_dfqcgs_dlzb_com(**args):
    conp = get_conp(dfqcgs_dlzb_com._name_)
    dfqcgs_dlzb_com.work(conp, **args)


# 4
def task_dzzb_ciesco_com_cn(**args):
    conp = get_conp(dzzb_ciesco_com_cn._name_)
    dzzb_ciesco_com_cn.work(conp,  pageloadtimeout=60, **args)



# def task_all():
#     bg = time.time()
#     try:
#         task_caigou_ceair_com()
#         task_csbidding_csair_com()
#         task_dfqcgs_dlzb_com()
#         task_dzzb_ciesco_com_cn()
#     except:
#         print("part 1 error!")


#     ed = time.time()

#     cos = int((ed - bg) / 60)

#     print("共耗时%d min" % cos)


# def create_schemas():
#     conp = get_conp1('qycg')
#     arr = [
#         'caigou_ceair_com', 'csbidding_csair_com', 'dfqcgs_dlzb_com',
#         'dzzb_ciesco_com_cn',
#     ]
#     for diqu in arr:
#         sql = "create schema if not exists %s" % diqu
#         db_command(sql, dbtype="postgresql", conp=conp)
