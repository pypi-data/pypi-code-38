from zhulong2.zhejiang import shenghui
from zhulong2.zhejiang import hangzhou
from zhulong2.zhejiang import ningbo
from zhulong2.zhejiang import wenzhou
from zhulong2.zhejiang import quzhou


from lmf.dbv2 import db_command
from os.path import join ,dirname
import time
from zhulong2.util.conf import get_conp,get_conp1

#6
def task_shenghui(**args):
    conp=get_conp(shenghui._name_)
    shenghui.work(conp,**args)
#10
def task_hangzhou(**args):
    conp=get_conp(hangzhou._name_)
    hangzhou.work(conp,**args)

def task_ningbo(**args):
    conp=get_conp(ningbo._name_)
    ningbo.work(conp,**args)

def task_wenzhou(**args):
    conp=get_conp(wenzhou._name_)
    wenzhou.work(conp,**args)

def task_quzhou(**args):
    conp=get_conp(quzhou._name_)
    quzhou.work(conp,**args)





def task_all():
    bg = time.time()
    try:

        task_shenghui()
        task_hangzhou()
        task_ningbo()
        task_quzhou()
        task_wenzhou()

    except:
        print("part zhejiang error!")

    ed = time.time()

    cos = int((ed - bg) / 60)

    print("共耗时%d min" % cos)

def create_schemas():
    conp = get_conp1('zfcg')
    arr = [
        'zhejiang_ningbo',
        'zhejiang_shenghui',
        'zhejiang_hangzhou',
        'zhejiang_wenzhou',
        'zhejiang_quzhou',
    ]
    for diqu in arr:
        sql = "create schema if not exists %s" % diqu
        db_command(sql, dbtype="postgresql", conp=conp)
    
