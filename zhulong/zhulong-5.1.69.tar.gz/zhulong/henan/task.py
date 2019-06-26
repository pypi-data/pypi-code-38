import time

from zhulong.henan import anyang
from zhulong.henan import dengfeng
from zhulong.henan import gongyi
from zhulong.henan import hebi
from zhulong.henan import jiaozhuo

from zhulong.henan import jiyuan
from zhulong.henan import jiyuan1
from zhulong.henan import kaifeng
from zhulong.henan import linzhou
from zhulong.henan import luohe

from zhulong.henan import luoyang
from zhulong.henan import mengzhou
from zhulong.henan import nanyang
from zhulong.henan import pingdingshan
from zhulong.henan import puyang



from zhulong.henan import ruzhou
from zhulong.henan import sanmenxia
from zhulong.henan import shangqiu
from zhulong.henan import weihui
from zhulong.henan import wugang


from zhulong.henan import xinmi
from zhulong.henan import xinxiang
from zhulong.henan import xinzheng
from zhulong.henan import xuchang
from zhulong.henan import yanshi

from zhulong.henan import xinyang
from zhulong.henan import yongcheng
from zhulong.henan import zhengzhou
from zhulong.henan import zhoukou
from zhulong.henan import zhumadian

from zhulong.henan import qinyang









from lmf.dbv2 import db_command 
from os.path import join ,dirname 

from zhulong.util.conf import get_conp,get_conp1


#1
def task_anyang(**args):
    conp=get_conp(anyang._name_)
    anyang.work(conp,**args)
#2
def task_dengfeng(**args):
    conp=get_conp(dengfeng._name_)
    dengfeng.work(conp,**args)
#3
def task_gongyi(**args):
    conp=get_conp(gongyi._name_)
    gongyi.work(conp,**args)


#4
def task_hebi(**args):
    conp=get_conp(hebi._name_)
    hebi.work(conp,**args)
#5
def task_jiaozhuo(**args):
    conp=get_conp(jiaozhuo._name_)
    jiaozhuo.work(conp,**args)
#6
def task_jiyuan(**args):
    conp=get_conp(jiyuan._name_)
    jiyuan.work(conp,**args)


#7
def task_jiyuan1(**args):
    conp=get_conp(jiyuan1._name_)
    jiyuan1.work(conp,**args)
#8
def task_kaifeng(**args):
    conp=get_conp(kaifeng._name_)
    kaifeng.work(conp,**args)
#9
def task_linzhou(**args):
    conp=get_conp(linzhou._name_)
    linzhou.work(conp,**args)


#10
def task_luohe(**args):
    conp=get_conp(luohe._name_)
    luohe.work(conp,**args)


#11
def task_luoyang(**args):
    conp=get_conp(luoyang._name_)
    luoyang.work(conp,**args)
#12
def task_mengzhou(**args):
    conp=get_conp(mengzhou._name_)
    mengzhou.work(conp,**args)
#
# #13
def task_nanyang(**args):
    conp=get_conp(nanyang._name_)
    nanyang.work(conp,**args)
#14
def task_pingdingshan(**args):
    conp=get_conp(pingdingshan._name_)
    pingdingshan.work(conp,**args)
#15
def task_puyang(**args):
    conp=get_conp(puyang._name_)
    puyang.work(conp,**args)



#16
def task_ruzhou(**args):
    conp=get_conp(ruzhou._name_)
    ruzhou.work(conp,**args)


#17
def task_sanmenxia(**args):
    conp=get_conp(sanmenxia._name_)
    sanmenxia.work(conp,**args)

#18
def task_shangqiu(**args):
    conp=get_conp(shangqiu._name_)
    shangqiu.work(conp,**args)


#19
def task_weihui(**args):
    conp=get_conp(weihui._name_)
    weihui.work(conp,**args)

#20
def task_wugang(**args):
    conp=get_conp(wugang._name_)
    wugang.work(conp,**args)


#21
def task_xinmi(**args):
    conp=get_conp(xinmi._name_)
    xinmi.work(conp,**args)

#22
def task_xinyang(**args):
    conp=get_conp(xinyang._name_)
    xinyang.work(conp,**args)

#23
def task_xinzheng(**args):
    conp=get_conp(xinzheng._name_)
    xinzheng.work(conp,**args)

#24
def task_xuchang(**args):
    conp=get_conp(xuchang._name_)
    xuchang.work(conp,**args)

#25
def task_yanshi(**args):
    conp=get_conp(yanshi._name_)
    yanshi.work(conp,**args)


#26
def task_yongcheng(**args):
    conp=get_conp(yongcheng._name_)
    yongcheng.work(conp,**args)


#27
def task_zhengzhou(**args):
    conp=get_conp(zhengzhou._name_)
    zhengzhou.work(conp,**args)


#28
def task_zhoukou(**args):
    conp=get_conp(zhoukou._name_)
    zhoukou.work(conp,**args)


#29
def task_zhumadian(**args):
    conp=get_conp(zhumadian._name_)
    zhumadian.work(conp,**args)


#30
def task_xinxiang(**args):
    conp=get_conp(xinxiang._name_)
    xinxiang.work(conp,**args)


#31
def task_qinyang(**args):
    conp=get_conp(qinyang._name_)
    qinyang.work(conp,**args)









def task_all():
    bg=time.time()
    try:
        task_anyang()
        task_dengfeng()
        task_gongyi()
        task_hebi()
        task_jiaozhuo()
    except:
        print("part1 error!")

    try:
        task_jiyuan()
        task_jiyuan1()
        task_kaifeng()
        task_linzhou()
        task_luohe()
    except:
        print("part2 error!")

    try:
        task_luoyang()
        task_zhoukou()
        task_mengzhou()
        #task_xiamen()
        task_nanyang()
        task_pingdingshan()
    except:
        print("part3 error!")


    try:
        task_puyang()
        task_qinyang()
        task_ruzhou()
        #task_xiamen()
        task_sanmenxia()
        task_shangqiu()
    except:
        print("part4 error!")


    try:
        task_weihui()
        task_wugang()
        task_xinmi()
        #task_xiamen()
        task_xinxiang()
        task_xinyang()
    except:
        print("part5 error!")

    try:
        task_xinzheng()
        task_xuchang()
        task_yanshi()
        task_yongcheng()
        task_zhengzhou()
    except:
        print("part6 error!")

    try:
        
        task_zhumadian()

    except:
        print("part7 error!")




    ed=time.time()


    cos=int((ed-bg)/60)

    print("共耗时%d min"%cos)


#write_profile('postgres,since2015,127.0.0.1,shandong')



def create_schemas():
    conp=get_conp1('henan')
    arr=["anyang","dengfeng","gongyi","hebi","jiaozhuo",
         "jiyuan","jiyuan1","kaifeng","linzhou","luohe",
         "luoyang","mengzhou","nanyang","pingdingshan","puyang",
         "qinyang","ruzhou","sanmenxia","shangqiu","weihui",
         "wugang","xinmi","xinyang","xinxiang","xinzheng",
         "xuchang","yanshi","yongcheng","zhengzhou","zhoukou",
        "zhumadian"]
    for diqu in arr:
        sql="create schema if not exists %s"%diqu
        db_command(sql,dbtype="postgresql",conp=conp)




