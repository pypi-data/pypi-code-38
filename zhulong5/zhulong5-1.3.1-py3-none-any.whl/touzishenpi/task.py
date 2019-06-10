import time

from zhulong5.touzishenpi import touzishenpi



from lmf.dbv2 import db_command


from zhulong5.util.conf import get_conp

#1
def task_touzishenpi(**args):
    """
    针对：html爬取
        增加 limit 参数（减轻数据库查询压力，加快速度）：每轮爬取 page 的限制。默认 1000
        增加 turn 参数（减轻数据库查询压力，加快速度）：page 爬取的轮数。默认10
        以上两个数据可以根据机器性能进行更改。
    :param conp:
    :param arg:
    :return:
    """
    conp=get_conp(touzishenpi._name_)
    touzishenpi.work(conp,**args)



def task_all():
    bg=time.time()
    try:
        task_touzishenpi()
    except:
        print("part1 error!")

    ed=time.time()
    cos=int((ed-bg)/60)

    print("共耗时%d min"%cos)


def create_schemas():
    conp=get_conp('touzishenpi')
    arr=['touzishenpi']
    for diqu in arr:
        sql="create schema if not exists %s"%diqu
        db_command(sql,dbtype="postgresql",conp=conp)




