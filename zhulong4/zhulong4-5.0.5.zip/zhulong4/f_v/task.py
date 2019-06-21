from lmf.dbv2 import db_command
from zhulong4.f_v import fwgs_sinograin_com_cn
from zhulong4.f_v import gs_coscoshipping_com
from zhulong4.f_v import jzcg_cfhi_com
from zhulong4.f_v import srm_crland_com_cn
from zhulong4.f_v import syhggs_dlzb_com
from zhulong4.f_v import sytrq_dlzb_com
from zhulong4.f_v import thzb_crsc_cn
from zhulong4.f_v import uat_ec_chng_com_cn



from os.path import join, dirname


import time

from zhulong4.util.conf import get_conp,get_conp1


# 1
def task_fwgs_sinograin_com_cn(**args):
    conp = get_conp(fwgs_sinograin_com_cn._name_)
    fwgs_sinograin_com_cn.work(conp, **args)


# 2
def task_gs_coscoshipping_com(**args):
    conp = get_conp(gs_coscoshipping_com._name_)
    gs_coscoshipping_com.work(conp, **args)


# 3
def task_jzcg_cfhi_com(**args):
    conp = get_conp(jzcg_cfhi_com._name_)
    jzcg_cfhi_com.work(conp,**args)


# 4
def task_srm_crland_com_cn(**args):
    conp = get_conp(srm_crland_com_cn._name_)
    srm_crland_com_cn.work(conp, **args)


# 5
def task_syhggs_dlzb_com(**args):
    conp = get_conp(syhggs_dlzb_com._name_)
    syhggs_dlzb_com.work(conp, **args)


# 6
def task_sytrq_dlzb_com(**args):
    conp = get_conp(sytrq_dlzb_com._name_)
    sytrq_dlzb_com.work(conp, **args)

#7
def task_thzb_crsc_cn(**args):
    conp = get_conp(thzb_crsc_cn._name_)
    thzb_crsc_cn.work(conp, **args)

#8
def task_uat_ec_chng_com_cn(**args):
    conp = get_conp(uat_ec_chng_com_cn._name_)
    uat_ec_chng_com_cn.work(conp, **args)




# def task_all():
#     bg = time.time()
#     try:
#         task_fwgs_sinograin_com_cn()
#         task_gs_coscoshipping_com()
#         task_jzcg_cfhi_com()
#         task_srm_crland_com_cn()
#     except:
#         print("part1 error!")

#     try:
#         task_uat_ec_chng_com_cn()
#         task_thzb_crsc_cn()
#         task_syhggs_dlzb_com()
#         task_sytrq_dlzb_com()
#     except:
#         print("part2 error!")




#     ed = time.time()

#     cos = int((ed - bg) / 60)

#     print("共耗时%d min" % cos)


# # write_profile('postgres,since2015,127.0.0.1,shandong')


# def create_schemas():
#     conp = get_conp1('qycg')

#     arr = [ "fwgs_sinograin_com_cn",
#             "gs_coscoshipping_com",
#             "jzcg_cfhi_com",
#             "srm_crland_com_cn",
#             "syhggs_dlzb_com",
#             "sytrq_dlzb_com",
#             "thzb_crsc_cn",
#             "uat_ec_chng_com_cn"]
#     for diqu in arr:
#         sql = "create schema if not exists %s" % diqu
#         db_command(sql, dbtype="postgresql", conp=conp)




