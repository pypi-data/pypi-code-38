from lmf.dbv2 import db_command
import time
from zhulong4.a_b import b2bcoal_crp_net_cn
from zhulong4.a_b import b2b_10086_cn
from zhulong4.a_b import baowu_ouyeelbuy_com
from zhulong4.a_b import bidding_ceiec_com_cn
from zhulong4.a_b import bid_ansteel_cn
from zhulong4.a_b import bidding_crmsc_com_cn
from zhulong4.a_b import bid_powerchina_cn
from zhulong4.a_b import buy_cnooc_com_cn

from zhulong4.util.conf import get_conp, get_conp1


# 1
def task_b2bcoal_crp_net_cn(**args):
    conp = get_conp(b2bcoal_crp_net_cn._name_)
    b2bcoal_crp_net_cn.work(conp,  pageloadtimeout=40, **args)


# 2
def task_b2b_10086_cn(**args):
    conp = get_conp(b2b_10086_cn._name_)
    b2b_10086_cn.work(conp, num=30, **args)


# 3
def task_baowu_ouyeelbuy_com(**args):
    conp = get_conp(baowu_ouyeelbuy_com._name_)
    baowu_ouyeelbuy_com.work(conp, num=20, pageloadtimeout=50, **args)


# 4
def task_bidding_ceiec_com_cn(**args):
    conp = get_conp(bidding_ceiec_com_cn._name_)
    bidding_ceiec_com_cn.work(conp, **args)


# 5
def task_bid_ansteel_cn(**args):
    conp = get_conp(bid_ansteel_cn._name_)
    bid_ansteel_cn.work(conp, **args)


# 6
def task_bidding_crmsc_com_cn(**args):
    conp = get_conp(bidding_crmsc_com_cn._name_)
    bidding_crmsc_com_cn.work(conp, **args)


# 7
def task_bid_powerchina_cn(**args):
    conp = get_conp(bid_powerchina_cn._name_)
    bid_powerchina_cn.work(conp, num=30, pageloadtimeout=40, **args)


# 8
def task_buy_cnooc_com_cn(**args):
    conp = get_conp(buy_cnooc_com_cn._name_)
    buy_cnooc_com_cn.work(conp, num=10, pageloadstrategy='none', pageloadtimeout=40, **args)


# def task_all():
#     bg = time.time()
#     try:
#         task_b2bcoal_crp_net_cn()
#         task_b2b_10086_cn()
#         task_baowu_ouyeelbuy_com()
#         task_bidding_ceiec_com_cn()
#     except:
#         print("part 1 error!")

#     try:
#         task_bid_ansteel_cn()
#         task_bidding_crmsc_com_cn()
#         task_bid_powerchina_cn()
#         task_buy_cnooc_com_cn()
#     except:
#         print("part 2 error!")

#     ed = time.time()

#     cos = int((ed - bg) / 60)

#     print("共耗时%d min" % cos)


# def create_schemas():
#     conp = get_conp1('qycg')
#     arr = [
#         'b2bcoal_crp_net_cn', 'b2b_10086_cn', 'baowu_ouyeelbuy_com',
#         'bidding_ceiec_com_cn', 'bid_ansteel_cn', 'bidding_crmsc_com_cn',
#         'bid_powerchina_cn', 'buy_cnooc_com_cn'
#     ]
#     for diqu in arr:
#         sql = "create schema if not exists %s" % diqu
#         db_command(sql, dbtype="postgresql", conp=conp)
