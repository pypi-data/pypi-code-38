import time

from zhulong2.tianjin import tianjin


from lmf.dbv2 import db_command

from zhulong2.util.conf import get_conp,get_conp1

#1
def task_tianjin(**args):
    conp=get_conp(tianjin._name_)
    tianjin.work(conp,**args)



def task_all():
    bg=time.time()
    try:
        task_tianjin()
    except:
        print("part1 error!")


    ed=time.time()
    cos=int((ed-bg)/60)
    print("共耗时%d min"%cos)


def create_schemas():
    conp=get_conp1('zfcg')
    arr=["tianjin_tianjin"]
    for diqu in arr:
        sql="create schema if not exists %s"%diqu
        db_command(sql,dbtype="postgresql",conp=conp)




