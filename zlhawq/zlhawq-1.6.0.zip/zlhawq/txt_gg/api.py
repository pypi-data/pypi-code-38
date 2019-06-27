from zlhawq.txt_gg.core import add_quyu,restart_quyu
from zlhawq.data import zhulong_diqu_dict,zl_diqu_dict
import time

#anqing 46000 解析花了660秒  1000万数据要40个小时解析完毕
def add_quyu_fast(quyu):
    conp=["gpadmin","since2015","192.168.4.179","base_db","mine"]

    add_quyu(quyu,conp)

def restart_quyu_fast(quyu):
    conp=["gpadmin","since2015","192.168.4.179","base_db","mine"]

    restart_quyu(quyu,conp)



def add_quyus_sheng(sheng):
    if sheng in['gcjs','zfcg','qycg']:
        quyus=zl_diqu_dict[sheng]
    else:
        quyus=zhulong_diqu_dict[sheng]
    length_quyu=len(quyus)
    print("现在开始解析%s 大区"%sheng)
    bg=time.time()
    for quyu in quyus:
        print("解析%s,还剩%d个"%(quyu,length_quyu))
        add_quyu_fast(quyu)
        length_quyu-=1
        ed=time.time()
        cost=int(ed-bg)
        print("耗时--%d秒"%cost)
        bg=time.time()


def add_quyus_all():
    arr=zhulong_diqu_dict.keys()
    arr.sort()
    for w in arr:
        add_quyus_sheng(w)
    for w in ['gcjs','zfcg','qycg']:
        add_quyus_sheng(w)