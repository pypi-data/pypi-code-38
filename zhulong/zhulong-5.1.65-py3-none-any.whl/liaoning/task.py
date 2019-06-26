from lmf.dbv2 import db_command
import time
from zhulong.liaoning import anshan

from zhulong.liaoning import beizhen

from zhulong.liaoning import benxi

from zhulong.liaoning import chaoyang

from zhulong.liaoning import dalian

from zhulong.liaoning import dandong

from zhulong.liaoning import donggang

from zhulong.liaoning import fushun

from zhulong.liaoning import fuxin

from zhulong.liaoning import haicheng

from zhulong.liaoning import huludao

from zhulong.liaoning import jinzhou

from zhulong.liaoning import liaoning

from zhulong.liaoning import liaoyang

from zhulong.liaoning import panjin
from zhulong.liaoning import shenyang
from zhulong.liaoning import tieling
from zhulong.liaoning import yingkou

from os.path import join, dirname


from zhulong.util.conf import get_conp,get_conp1


# 1
def task_anshan(**args):
    conp = get_conp(anshan._name_)
    anshan.work(conp, **args)


# 2
def task_beizhen(**args):
    conp = get_conp(beizhen._name_)
    beizhen.work(conp, **args)


# 3
def task_dandong(**args):
    conp = get_conp(dandong._name_)
    dandong.work(conp, **args)


# 4
def task_benxi(**args):
    conp = get_conp(benxi._name_)
    benxi.work(conp, **args)


# 5
def task_chaoyang(**args):
    conp = get_conp(chaoyang._name_)
    chaoyang.work(conp, **args)


# 6
def task_dalian(**args):
    conp = get_conp(dalian._name_)
    dalian.work(conp, **args)


# 7
def task_donggang(**args):
    conp = get_conp(donggang._name_)
    donggang.work(conp, **args)


# 8
def task_fushun(**args):
    conp = get_conp(fushun._name_)
    fushun.work(conp, **args)


# 9
def task_fuxin(**args):
    conp = get_conp(fuxin._name_)
    fuxin.work(conp, **args)


# 10
def task_haicheng(**args):
    conp = get_conp(haicheng._name_)
    haicheng.work(conp, **args)


# 11
def task_yingkou(**args):
    conp = get_conp(yingkou._name_)
    yingkou.work(conp, **args)


# 12
def task_huludao(**args):
    conp = get_conp(huludao._name_)
    huludao.work(conp, **args)


# 13
def task_jinzhou(**args):
    conp = get_conp(jinzhou._name_)
    jinzhou.work(conp, **args)


# 14
def task_liaoning(**args):
    conp = get_conp(liaoning._name_)
    liaoning.work(conp, **args)


# 15
def task_liaoyang(**args):
    conp = get_conp(liaoyang._name_)
    liaoyang.work(conp, **args)


# 16
def task_panjin(**args):
    conp = get_conp(panjin._name_)
    panjin.work(conp, **args)


# 17
def task_shenyang(**args):
    conp = get_conp(shenyang._name_)
    shenyang.work(conp, **args)


# 18
def task_tieling(**args):
    conp = get_conp(tieling._name_)
    tieling.work(conp, **args)


def task_all():
    bg = time.time()
    try:
        task_anshan()
        task_beizhen()
        task_dandong()
        task_benxi()
        task_chaoyang()
    except:
        print("part1 error!")

    try:
        task_dalian()
        task_donggang()
        task_fushun()
        task_fuxin()
        task_haicheng()
    except:
        print("part2 error!")

    try:
        task_yingkou()
        task_huludao()
        task_jinzhou()
        task_liaoning()
        task_liaoyang()
    except:
        print("part3 error!")

    try:
        task_panjin()
        task_shenyang()
        task_tieling()
    except:
        print("part4 error!")

    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)


# write_profile('postgres,since2015,127.0.0.1,shandong')


def create_schemas():
    conp = get_conp1('liaoning')
    arr = [
        "anshan", "beizhen", "benxi", "chaoyang", "dalian",
        "dandong", "donggang", "fushun", "fuxin", "haicheng",
        "huludao", "jinzhou", "liaoning", "liaoyang", "panjin",
        "shenyang", "tieling", "yingkou",
    ]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)
