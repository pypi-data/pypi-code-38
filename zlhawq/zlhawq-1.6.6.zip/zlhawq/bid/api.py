from lmf.dbv2 import db_command ,db_query
from lmf.bigdata import pg2csv
import sys 
import os 
from fabric import Connection
from zlhawq.bid.core import add_quyu_tmp_pc,restart_quyu_tmp_pc
import traceback
from zlhawq.data import zhulong_diqu_dict,zl_diqu_dict,zl_shenpi_dict
#####对zhulong1 有效,从192.168.4.175 往192.168.4.179 更新
def add_quyu_pc_local(quyu,tag='all'):

    add_quyu_tmp_pc(quyu,tag)

def restart_quyu_pc_local(quyu):

    restart_quyu_tmp_pc(quyu)


def add_quyu_pc_remote(quyu,tag='all'):
    conp_remote=["root@192.168.4.187","rootHDPHAWQDatanode5@zhulong"]
    c=Connection(conp_remote[0],connect_kwargs={"password":conp_remote[1]})
    try:
        c.run("""/opt/python35/bin/python3 -c "from zlhawq.bid.api import add_quyu_pc_local;add_quyu_pc_local('%s','%s') " """%(quyu,tag),pty=True,encoding='utf8')
    except:
        traceback.print_exc()
    finally:
        c.close()

def restart_quyu_pc_remote(quyu):
    conp_remote=["root@192.168.4.187","rootHDPHAWQDatanode5@zhulong"]
    c=Connection(conp_remote[0],connect_kwargs={"password":conp_remote[1]})
    try:
        c.run("""/opt/python35/bin/python3 -c "from zlhawq.bid.api import restart_quyu_pc_local;restart_quyu_pc_local('%s') " """%(quyu),pty=True,encoding='utf8')
    except:
        traceback.print_exc()
    finally:
        c.close()

add_quyu1=add_quyu_pc_remote

def add_quyu1_sheng(sheng,tag='all'):
    quyus=zhulong_diqu_dict[sheng]

    for quyu in quyus:
        add_quyu1(quyu,tag)

def add_quyu1_all():
    for sheng in zhulong_diqu_dict.keys():
        add_quyu1_sheng(sheng)
#-------------------------------------------------------------------------------------------
