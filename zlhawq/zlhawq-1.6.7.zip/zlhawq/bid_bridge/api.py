from lmf.dbv2 import db_command ,db_query
from lmf.bigdata import pg2csv
import sys 
import os 
from fabric import Connection
from zlhawq.bid_bridge.core import add_quyu_tmp,restart_quyu_tmp
import traceback
from zlhawq.data import zhulong_diqu_dict,zl_diqu_dict,zl_shenpi_dict
#####对zhulong1 有效,从192.168.4.175 往192.168.4.179 更新
def add_quyu1(quyu):
    add_quyu_tmp(quyu)
def add_quyu1_sheng(sheng):
    quyus=zhulong_diqu_dict[sheng]

    for quyu in quyus:
        add_quyu1(quyu)

def add_quyu1_all():
    for sheng in zhulong_diqu_dict.keys():
        add_quyu1_sheng(sheng)
