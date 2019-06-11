import time

from zhulong.sichuan import bazhong

from zhulong.sichuan import chengdu

from zhulong.sichuan import chongzhou

from zhulong.sichuan import dazhou

from zhulong.sichuan import deyang

from zhulong.sichuan import dujiangyan

from zhulong.sichuan import guangan

from zhulong.sichuan import guanghan

from zhulong.sichuan import guangyuan

from zhulong.sichuan import jiangyou

from zhulong.sichuan import jianyang

from zhulong.sichuan import leshan

from zhulong.sichuan import longchang

from zhulong.sichuan import luzhou

from zhulong.sichuan import meishan

from zhulong.sichuan import mianyang1

from zhulong.sichuan import mianyang2

from zhulong.sichuan import nanchong

from zhulong.sichuan import neijiang

from zhulong.sichuan import panzhihua

from zhulong.sichuan import pengzhou

from zhulong.sichuan import qionglai

from zhulong.sichuan import shifang

from zhulong.sichuan import sichuan

from zhulong.sichuan import sichuan2

from zhulong.sichuan import suining

from zhulong.sichuan import wanyuan

from zhulong.sichuan import yaan

from zhulong.sichuan import yibin

from lmf.dbv2 import db_command
from os.path import join, dirname

from zhulong.util.conf import get_conp, get_conp1


# 1
def task_bazhong(**args):
    conp = get_conp(bazhong._name_)
    bazhong.work(conp, **args)


# 2
def task_chengdu(**args):
    conp = get_conp(chengdu._name_)
    chengdu.work(conp, **args)


# 3
def task_chongzhou(**args):
    conp = get_conp(chongzhou._name_)
    chongzhou.work(conp, **args)


# 4
def task_dazhou(**args):
    conp = get_conp(dazhou._name_)
    dazhou.work(conp, **args)


# 5
def task_deyang(**args):
    conp = get_conp(deyang._name_)
    deyang.work(conp, **args)


# 6
def task_dujiangyan(**args):
    conp = get_conp(dujiangyan._name_)
    dujiangyan.work(conp, **args)


# 7
def task_guangan(**args):
    conp = get_conp(guangan._name_)
    guangan.work(conp, **args)


# 8
def task_guanghan(**args):
    conp = get_conp(guanghan._name_)
    guanghan.work(conp, **args)


# 9
def task_guangyuan(**args):
    conp = get_conp(guangyuan._name_)
    guangyuan.work(conp, **args)


# 10
def task_jiangyou(**args):
    conp = get_conp(jiangyou._name_)
    jiangyou.work(conp, pageloadtimeout=180, **args)


# 11
def task_jianyang(**args):
    conp = get_conp(jianyang._name_)
    jianyang.work(conp, **args)


# 12
def task_leshan(**args):
    conp = get_conp(leshan._name_)
    leshan.work(conp, **args)


# 13
def task_longchang(**args):
    conp = get_conp(longchang._name_)
    longchang.work(conp, pageloadtimeout=180, **args)


# 14
def task_luzhou(**args):
    conp = get_conp(luzhou._name_)
    luzhou.work(conp, **args)


# 15
def task_meishan(**args):
    conp = get_conp(meishan._name_)
    meishan.work(conp, **args)


# 16
def task_mianyang1(**args):
    conp = get_conp(mianyang1._name_)
    mianyang1.work(conp, pageloadtimeout=180, pageLoadStrategy="none", **args)


def task_mianyang2(**args):
    conp = get_conp(mianyang2._name_)
    mianyang2.work(conp, **args)


# 17
def task_nanchong(**args):
    conp = get_conp(nanchong._name_)
    nanchong.work(conp, **args)


# 18
def task_neijiang(**args):
    conp = get_conp(neijiang._name_)
    neijiang.work(conp, pageloadtimeout=180, pageLoadStrategy="none", **args)


# 19
def task_panzhihua(**args):
    conp = get_conp(panzhihua._name_)
    panzhihua.work(conp, **args)


# 20
def task_pengzhou(**args):
    conp = get_conp(pengzhou._name_)
    pengzhou.work(conp, **args)


# 21
def task_qionglai(**args):
    conp = get_conp(qionglai._name_)
    qionglai.work(conp, **args)


# 22
def task_shifang(**args):
    conp = get_conp(shifang._name_)
    shifang.work(conp, **args)


# 23
def task_sichuan(**args):
    conp = get_conp(sichuan._name_)
    sichuan.work(conp, **args)

# 23
def task_sichuan2(**args):
    conp = get_conp(sichuan2._name_)
    sichuan2.work(conp, **args)

# 24
def task_suining(**args):
    conp = get_conp(suining._name_)
    suining.work(conp, **args)


# 25

def task_wanyuan(**args):
    conp = get_conp(wanyuan._name_)
    wanyuan.work(conp, **args)


# 26
def task_yaan(**args):
    conp = get_conp(yaan._name_)
    yaan.work(conp, **args)


# 27
def task_yibin(**args):
    conp = get_conp(yibin._name_)
    yibin.work(conp, **args)


def task_all():
    bg = time.time()
    try:
        task_bazhong()
        task_chengdu()
        task_chongzhou()
        task_dazhou()
        task_deyang()
    except:
        print("part1 error!")

    try:
        task_dujiangyan()
        task_guangan()
        task_guanghan()
        task_guangyuan()
        task_jiangyou()
    except:
        print("part2 error!")

    try:
        task_jianyang()
        task_leshan()
        task_longchang()
        task_luzhou()
        task_meishan()
    except:
        print("part3 error!")

    try:
        task_mianyang1()
        task_mianyang2()
        task_nanchong()
        task_neijiang()
        task_panzhihua()
        task_pengzhou()
    except:
        print("part4 error!")

    try:
        task_wanyuan()
        task_qionglai()
        task_shifang()
        task_sichuan()
        task_sichuan2()
        task_suining()
    except:
        print("part5 error!")

    try:
        task_yaan()
        task_yibin()
    except:
        print("part6 error!")

    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('sichuan')
    arr = ["bazhong", "chengdu", "chongzhou", "dazhou", "deyang",
           "dujiangyan", "guangan", "guanghan", "guangyuan", "jiangyou",
           "jianyang", "leshan", "longchang", "luzhou", "meishan",
           "mianyang1", "mianyang2", "nanchong", "neijiang", "panzhihua", "pengzhou",
           "qionglai", "shifang", "sichuan","sichuan2", "suining", "wanyuan",
           "yaan", "yibin"
           ]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)
