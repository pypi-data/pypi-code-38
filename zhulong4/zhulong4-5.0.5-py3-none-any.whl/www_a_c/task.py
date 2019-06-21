from lmf.dbv2 import db_command
from zhulong4.www_a_c import www_bidding_csg_cn
from zhulong4.www_a_c import www_cdt_eb_com
from zhulong4.www_a_c import www_cgdcbidding_com
from zhulong4.www_a_c import www_chdtp_com
from zhulong4.www_a_c import www_china_tender_com_cn
from zhulong4.www_a_c import www_chinabidding_com
from zhulong4.www_a_c import www_cnbmtendering_com
from zhulong4.www_a_c import www_cnpcbidding_com
from zhulong4.www_a_c import www_crpsz_com
from zhulong4.www_a_c import www_chinabidding_com_total

from os.path import join, dirname


import time

from zhulong4.util.conf import get_conp,get_conp1


# 1
def task_www_bidding_csg_cn(**args):
    conp = get_conp(www_bidding_csg_cn._name_)
    www_bidding_csg_cn.work(conp, **args)


# 2
def task_www_cdt_eb_com(**args):
    conp = get_conp(www_cdt_eb_com._name_)
    www_cdt_eb_com.work(conp,num=20, **args)


# 3
def task_www_cgdcbidding_com(**args):
    conp = get_conp(www_cgdcbidding_com._name_)
    www_cgdcbidding_com.work(conp ,**args)


# 4
def task_www_chdtp_com(**args):
    conp = get_conp(www_chdtp_com._name_)
    www_chdtp_com.work(conp, **args)


# 5
def task_www_china_tender_com_cn(**args):
    conp = get_conp(www_china_tender_com_cn._name_)
    www_china_tender_com_cn.work(conp, **args)


# 6-1
def task_www_chinabidding_com(**args):
    conp = get_conp(www_chinabidding_com._name_)
    www_chinabidding_com.work(conp ,cdc_total=20, **args)


# 6-2  #####只爬取第一次就可以关闭,由6-1做增量更新
def task_www_chinabidding_com_total(**args):
    conp = get_conp(www_chinabidding_com_total._name_)
    www_chinabidding_com_total.work(conp , **args)


#7
def task_www_cnbmtendering_com(**args):
    conp = get_conp(www_cnbmtendering_com._name_)
    www_cnbmtendering_com.work(conp,pageLoadStrategy='none',pageloadtimeout=80, **args)

#8
def task_www_cnpcbidding_com(**args):
    conp = get_conp(www_cnpcbidding_com._name_)
    www_cnpcbidding_com.work(conp , **args)

def task_www_crpsz_com(**args):
    conp = get_conp(www_crpsz_com._name_)
    www_crpsz_com.work(conp , **args)


# def task_all():
#     bg = time.time()
#     try:
#         task_www_bidding_csg_cn()
#         task_www_cdt_eb_com()
#         task_www_cgdcbidding_com()
#         task_www_chdtp_com()
#         task_www_china_tender_com_cn()
#     except:
#         print("part1 error!")

#     try:
#         task_www_chinabidding_com()
#         task_www_cnbmtendering_com()
#         task_www_cnpcbidding_com()
#         task_www_crpsz_com()
#     except:
#         print("part2 error!")




#     ed = time.time()

#     cos = int((ed - bg) / 60)

#     print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


# def create_schemas():
#     conp = get_conp1('qycg')

#     arr = [ "www_bidding_csg_cn",
#             "www_cdt_eb_com",
#             "www_cgdcbidding_com",
#             "www_chdtp_com",
#             "www_china_tender_com_cn",
#             "www_chinabidding_com",
#             "www_cnbmtendering_com",
#             "www_cnpcbidding_com",
#             "www_crpsz_com",
#             "www_chinabidding_com_total"]
#     for diqu in arr:
#         sql = "create schema if not exists %s" % diqu
#         db_command(sql, dbtype="postgresql", conp=conp)




