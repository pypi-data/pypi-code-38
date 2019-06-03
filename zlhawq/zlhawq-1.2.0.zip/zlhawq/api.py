from lmf.dbv2 import db_command ,db_query
from lmf.bigdata import pg2csv
import sys 
import os 
from fabric import Connection
from zlhawq.core import add_quyu_tmp,restart_quyu_tmp
import traceback

#####对zhulong1 有效,从192.168.4.175 往192.168.4.179 更新
def add_quyu_db1_local(quyu,tag='all'):
    arr=quyu.split("_")
    s1,s2=arr[0],'_'.join(arr[1:])

    conp_pg=["postgres","since2015","192.168.4.175",s1,s2]
    conp_hawq=["gpadmin","since2015","192.168.4.179","base_db","v3"]
    dir='/data/lmf'
    addr='192.168.4.187:8111'
    add_quyu_tmp(quyu,conp_pg,conp_hawq,dir,addr,tag=tag)

def restart_quyu_db1_local(quyu):
    arr=quyu.split("_")
    s1,s2=arr[0],'_'.join(arr[1:])
    tag='all'
    conp_pg=["postgres","since2015","192.168.4.175",s1,s2]
    conp_hawq=["gpadmin","since2015","192.168.4.179","base_db","v3"]
    dir='/data/lmf'
    addr='192.168.4.187:8111'
    restart_quyu_tmp(quyu,conp_pg,conp_hawq,dir,addr,tag=tag)


def add_quyu_db1_remote(quyu,tag='all'):
    conp_remote=["root@192.168.4.187","rootHDPHAWQDatanode5@zhulong"]
    c=Connection(conp_remote[0],connect_kwargs={"password":conp_remote[1]})
    try:
        c.run("""/opt/python35/bin/python3 -c "from zlhawq.api import add_quyu_db1_local;add_quyu_db1_local('%s','%s') " """%(quyu,tag),pty=True,encoding='utf8')
    except:
        traceback.print_exc()
    finally:
        c.close()

def restart_quyu_db1_remote(quyu):
    conp_remote=["root@192.168.4.187","rootHDPHAWQDatanode5@zhulong"]
    c=Connection(conp_remote[0],connect_kwargs={"password":conp_remote[1]})
    try:
        c.run("""/opt/python35/bin/python3 -c "from zlhawq.api import restart_quyu_db1_local;restart_quyu_db1_local('%s') " """%(quyu),pty=True,encoding='utf8')
    except:
        traceback.print_exc()
    finally:
        c.close()

add_quyu1=add_quyu_db1_remote
#-------------------------------------------------------------------------------------------
#####对zhulong2-gcjs  zhulong3-zfcg  zhulong4-qycg 有效，从192.168.4.182 往192.168.4.179 更新

def add_quyu_db2_local(quyu,tag='all'):
    arr=quyu.split("_")
    s1,s2=arr[0],'_'.join(arr[1:])

    conp_pg=["postgres","since2015","192.168.4.182",s1,s2]
    conp_hawq=["gpadmin","since2015","192.168.4.179","base_db","v3"]
    dir='/data/lmf'
    addr='192.168.4.187:8111'
    add_quyu_tmp(quyu,conp_pg,conp_hawq,dir,addr,tag=tag)

def restart_quyu_db2_local(quyu):
    arr=quyu.split("_")
    s1,s2=arr[0],'_'.join(arr[1:])
    tag='all'
    conp_pg=["postgres","since2015","192.168.4.182",s1,s2]
    conp_hawq=["gpadmin","since2015","192.168.4.179","base_db","v3"]
    dir='/data/lmf'
    addr='192.168.4.187:8111'
    restart_quyu_tmp(quyu,conp_pg,conp_hawq,dir,addr,tag=tag)



def add_quyu_db2_remote(quyu,tag='all'):
    conp_remote=["root@192.168.4.187","rootHDPHAWQDatanode5@zhulong"]
    c=Connection(conp_remote[0],connect_kwargs={"password":conp_remote[1]})
    try:
        c.run("""/opt/python35/bin/python3 -c "from zlhawq.api import add_quyu_db2_local;add_quyu_db2_local('%s','%s') " """%(quyu,tag),pty=True,encoding='utf8')
    except:
        traceback.print_exc()
    finally:
        c.close()

def restart_quyu_db2_remote(quyu):
    conp_remote=["root@192.168.4.187","rootHDPHAWQDatanode5@zhulong"]
    c=Connection(conp_remote[0],connect_kwargs={"password":conp_remote[1]})
    try:
        c.run("""/opt/python35/bin/python3 -c "from zlhawq.api import restart_quyu_db2_local;restart_quyu_db2_local('%s') " """%(quyu),pty=True,encoding='utf8')
    except:
        traceback.print_exc()
    finally:
        c.close()


add_quyu2=add_quyu_db2_remote
#-------------------------------------------------------------------------------------