from . import gcjs,ggzy,zfcg,qycg
import os


def write_all(dirname,**krg):
    if not os.path.exists(os.path.join(dirname,'ggzy')):
        os.mkdir(os.path.join(dirname,'ggzy'))
    ggzy.write_dags(os.path.join(dirname,'ggzy'),**krg)

    if not os.path.exists(os.path.join(dirname,'zfcg')):
        os.mkdir(os.path.join(dirname,'zfcg'))
    zfcg.write_dags(os.path.join(dirname,'zfcg'),**krg)


    if not os.path.exists(os.path.join(dirname,'gcjs')):
        os.mkdir(os.path.join(dirname,'gcjs'))
    gcjs.write_dags(os.path.join(dirname,'gcjs'),**krg)

    if not os.path.exists(os.path.join(dirname,'qycg')):
        os.mkdir(os.path.join(dirname,'qycg'))
    qycg.write_dags(os.path.join(dirname,'qycg'),**krg)
