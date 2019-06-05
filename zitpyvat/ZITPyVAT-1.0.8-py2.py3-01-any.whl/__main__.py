# -*- coding: utf-8 -*-
# @Time    : 2018/8/3 10:28
# @Author  : Liu Gang
# @Site    : 
# @File    : __main__.py
# @Software: PyCharm
from py_sa_opr import SA_DRV_VER
from ratb5 import RATB5_VER
from SignalGenerator import SG_DRV_VER
from Socket_Func import SOCKET_VER
from vatbase import VAT_BASE_VER
from db_opr import DB_OPR_VER

str_show = "\n**************\n" \
           + "Socket Ver:%s\n" % SOCKET_VER \
           + "VatBase Ver:%s\n" % VAT_BASE_VER \
           + "RATB5 Ver:%s\n" % RATB5_VER \
           + "SA_Drv Ver:%s\n" % SA_DRV_VER \
           + "SG_Drv Ver:%s\n" % SG_DRV_VER \
           + "DB_OPR Ver:%s\n" % DB_OPR_VER \
           + "**************\n"

print(str_show)
