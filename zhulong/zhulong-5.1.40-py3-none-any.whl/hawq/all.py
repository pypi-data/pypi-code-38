from zhulong.util.data import zhulong_diqu_dict

from lmfhawq.zl import add_quyu_fast,add_quyu_fast_remote


import socket
import time 

def add_sheng(sheng,tag='all'):
    ip=socket.gethostbyname(socket.gethostname())
    anhui=zhulong_diqu_dict[sheng]

    for quyu in anhui:
        quyu=sheng+"_"+quyu
        print(quyu,ip)
        if ip=='192.168.4.187':
            add_quyu_fast(quyu,tag)
        else:
            add_quyu_fast_remote(quyu,tag)
        #time.sleep(4)

def add_shi(quyu,tag='all'):
    ip=socket.gethostbyname(socket.gethostname())
    print(quyu,ip)
    if ip=='192.168.4.187':
        add_quyu_fast(quyu,tag)
    else:
        add_quyu_fast_remote(quyu,tag)
    #time.sleep(4)