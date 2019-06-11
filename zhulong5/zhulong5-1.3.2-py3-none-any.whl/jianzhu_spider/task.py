import time
from zhulong5.jianzhu_spider import jianzhu

from zhulong5.jianzhu_spider import jianzhu_qyxx
from zhulong5.jianzhu_spider import jianzhu_ryxx
from zhulong5.jianzhu_spider import jianzhu_zcry
from zhulong5.jianzhu_spider import jianzhu_gcxm
from zhulong5.jianzhu_spider import jianzhu_xmxx

from lmf.dbv2 import db_command

from zhulong5.util.conf import get_conp

#  ----------------------------------------建筑网站基础信息-----------------------------------------------------------------

# 建筑网站爬取全量数据的顺序
# def task_jz_all(**args):
#     bg = time.time()
#     # 1
#     try:
#         conp = get_conp(jianzhu._name_)
#         jianzhu.work(conp, pageloadtimeout=120, num=50, **args)
#     except:
#         print("work1 error!")
#     # 2
#     try:
#         conp = get_conp(jianzhu2._name_)
#         jianzhu2.work(conp, pageloadtimeout=120, num=50, **args)
#     except:
#         print("work2 error!")
#     # 3
#     try:
#         conp = get_conp(jianzhu3._name_)
#         jianzhu3.work(conp, pageloadtimeout=120, num=150, **args)
#     except:
#         print("work3 error!")
#     # 4
#     try:
#         conp = get_conp(jianzhu4._name_)
#         jianzhu4.work(conp, pageloadtimeout=120, num=150, **args)
#     except:
#         print("work4 error!")
#
#     ed = time.time()
#     cos = int((ed - bg) / 60)
#     print("共耗时%d min" % cos)




# ----------------------------------------建筑网站基础信息增量更新---------------------------------------------------------------

# 建筑增量更新，生成cdc文件
def task_jz_cdc(**args):
    conp = get_conp(jianzhu._name_)
    jianzhu.work(conp, cdc_total=None, pageloadtimeout=120, **args)

# -----------------------------------------建筑网站企业信息-------------------------------------------------------------

def task_qyxx(**args):
    conp = get_conp(jianzhu_qyxx._name_)
    jianzhu_qyxx.work(conp, pageloadtimeout=120,num=100, **args)

# ------------------------------------------建筑网站注册人员基本信息-------------------------------------------------------

def task_ryxx(**args):
    conp = get_conp(jianzhu_ryxx._name_)
    jianzhu_ryxx.work(conp, pageloadtimeout=120,num=100, **args)


# -------------------------------------------建筑网站注册人员详细信息-------------------------------------------------------

def task_zcry(**args):
    conp = get_conp(jianzhu_zcry._name_)
    jianzhu_zcry.work(conp, pageloadtimeout=120, **args)



# ------------------------------------------建筑网站工程项目基本信息-------------------------------------------------------

def task_gcxm(**args):
    conp = get_conp(jianzhu_gcxm._name_)
    jianzhu_gcxm.work(conp, pageloadtimeout=120, **args)


# -------------------------------------------建筑网站工程项目详细信息-------------------------------------------------------

def task_xmxx(**args):
    conp = get_conp(jianzhu_xmxx._name_)
    jianzhu_xmxx.work(conp, pageloadtimeout=120, **args)


##



# 更新信息
def task_all():
    bg = time.time()
    # 1 建筑网站基础信息增量更新
    # try:
    #     task_jz_all()
    # except:
    #     print("work1 error!")
    # 2 建筑网站企业信息
    try:
        task_qyxx()
    except:
        print("work2 error!")
    # 3 建筑网站注册人员基本信息
    try:
        task_zcry()
    except:
        print("work3 error!")
    # 4 建筑网站注册人员详细信息
    try:
        task_ryxx()
    except:
        print("work4 error!")

    # 5 建筑网站注册人员基本信息
    try:
        task_gcxm()
    except:
        print("work5 error!")
    # 6 建筑网站注册人员详细信息
    try:
        task_xmxx()
    except:
        print("work6 error!")

    ed = time.time()
    cos = int((ed - bg) / 60)
    print("共耗时%d min" % cos)


# ---------------------------------------------程序入口--------------------------------------------------------

# if __name__ == '__main__':
#
#     conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "jianzhu"]
#     # task_all(conp=conp) # 已经有基础数据了，故请注意不要打开，因为该网站爬全量是非常困难而且耗时的
#
#     task_cdc(conp=conp)  # 为建筑企业基础信息的增量更新
#
#     task_xx_all(conp=conp) # 已有基础备份为企业注册人员基本信息以及注册人员详细信息的增量更新，数据来源于企业基础数据生成的gg表


def create_schemas():
    conp=get_conp('jianzhu')
    arr=['jianzhu']
    for diqu in arr:
        sql="create schema if not exists %s"%diqu
        db_command(sql,dbtype="postgresql",conp=conp)