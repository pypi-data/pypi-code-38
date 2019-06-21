from lmf.dbv2 import db_command
import time
from zhulong4.e_f import ebid_aecc_mall_com
from zhulong4.e_f import ec1_mcc_com_cn
from zhulong4.e_f import ecp_sgcc_com_cn
from zhulong4.e_f import ec_ccccltd_cn
from zhulong4.e_f import ec_ceec_net_cn
from zhulong4.e_f import ec_chalieco_com
from zhulong4.e_f import epp_ctg_com_cn
from zhulong4.e_f import eps_sdic_com_cn
from zhulong4.e_f import etp_fawiec_com
from zhulong4.e_f import ecp_cgnpc_com_cn

from zhulong4.util.conf import get_conp, get_conp1


# 1
def task_ebid_aecc_mall_com(**args):
    conp = get_conp(ebid_aecc_mall_com._name_)
    ebid_aecc_mall_com.work(conp, **args)


# 2
def task_ec1_mcc_com_cn(**args):
    conp = get_conp(ec1_mcc_com_cn._name_)
    ec1_mcc_com_cn.work(conp, num=15, pageloadtimeout=40, **args)


# 3
def task_ecp_sgcc_com_cn(**args):
    conp = get_conp(ecp_sgcc_com_cn._name_)
    ecp_sgcc_com_cn.work(conp, **args)


# 4
def task_ec_ccccltd_cn(**args):
    conp = get_conp(ec_ccccltd_cn._name_)
    ec_ccccltd_cn.work(conp, num=15, pageloadtimeout=60, **args)


# 5
def task_ec_ceec_net_cn(**args):
    conp = get_conp(ec_ceec_net_cn._name_)
    ec_ceec_net_cn.work(conp, **args)


# 6
def task_ec_chalieco_com(**args):
    conp = get_conp(ec_chalieco_com._name_)
    ec_chalieco_com.work(conp, **args)


# 7
def task_epp_ctg_com_cn(**args):
    conp = get_conp(epp_ctg_com_cn._name_)
    epp_ctg_com_cn.work(conp, **args)


# 8
def task_eps_sdic_com_cn(**args):
    conp = get_conp(eps_sdic_com_cn._name_)
    eps_sdic_com_cn.work(conp, **args)


# 9
def task_etp_fawiec_com(**args):
    conp = get_conp(etp_fawiec_com._name_)
    etp_fawiec_com.work(conp, **args)


# 10
def task_ecp_cgnpc_com_cn(**args):
    conp = get_conp(ecp_cgnpc_com_cn._name_)
    ecp_cgnpc_com_cn.work(conp, **args)


# def task_all():
#     bg = time.time()
#     try:
#         task_ebid_aecc_mall_com()
#         task_ec1_mcc_com_cn()
#         task_ecp_sgcc_com_cn()
#         task_ec_ccccltd_cn()
#         task_ecp_cgnpc_com_cn()
#     except:
#         print("part 1 error!")

#     try:
#         task_ec_ceec_net_cn()
#         task_ec_chalieco_com()
#         task_epp_ctg_com_cn()
#         task_eps_sdic_com_cn()
#         task_etp_fawiec_com()
#     except:
#         print("part 2 error!")

#     ed = time.time()

#     cos = int((ed - bg) / 60)

#     print("共耗时%d min" % cos)


# def create_schemas():
#     conp = get_conp1('qycg')
#     arr = [
#         'ebid_aecc_mall_com', 'ec1_mcc_com_cn', 'ecp_sgcc_com_cn',
#         'ec_ccccltd_cn', 'ec_ceec_net_cn', 'ec_chalieco_com',
#         'epp_ctg_com_cn', 'eps_sdic_com_cn', 'etp_fawiec_com'
#     ]
#     for diqu in arr:
#         sql = "create schema if not exists %s" % diqu
#         db_command(sql, dbtype="postgresql", conp=conp)
