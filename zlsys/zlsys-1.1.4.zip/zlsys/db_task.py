from zlsys.src import src_update,src_update_dates
from zlsys.t_gg import t_gg_update,est_func
from datetime import datetime,timedelta
from lmf.dbv2 import db_command


conp_=['postgres','since2015','192.168.4.175','zlsys']

settings={
    "zlsys_yunnan_qujingshi":[['曲靖市','zfcg','yunnan_qujingshi','云南曲靖市','2019-06-25'],
            ['曲靖市','gcjs','yunnan_qujingshi','云南曲靖市','2019-06-25']]
    ,
    "zlsys_yunnan_dalizhou":[['大理州','zfcg','yunnan_dalizhou','云南大理州','2019-06-25'],
            ['大理州','gcjs','yunnan_dalizhou','云南大理州','2019-06-25']]
    ,

    "zlsys_yunnan_lincangshi":[['临沧市','zfcg','yunnan_lincangshi','云南临沧市','2019-06-25'],
            ['临沧市','gcjs','yunnan_lincangshi','云南临沧市','2019-06-25']]
    ,

    "zlsys_yunnan_wenshanzhou":[['文山州','zfcg','yunnan_wenshanzhou','云南文山州','2019-06-25'],
            ['文山州','gcjs','yunnan_wenshanzhou','云南文山州','2019-06-25']]
    ,
    "zlsys_yunnan_yuxishi":[['玉溪市','zfcg','yunnan_yuxishi','云南玉溪市','2019-06-25'],
            ['玉溪市','gcjs','yunnan_yuxishi','云南玉溪市','2019-06-25']]
    ,
    "zlsys_yunnan_xishuangbanna":[['西双版纳州','zfcg','yunnan_xishuangbanna','云南西双版纳州','2019-06-25'],
            ['西双版纳州','gcjs','yunnan_xishuangbanna','云南西双版纳州','2019-06-25']]
    ,
    "zlsys_yunnan_zhaotongshi":[['昭通市','zfcg','yunnan_zhaotongshi','云南昭通市','2019-06-25'],
            ['昭通市','gcjs','yunnan_zhaotongshi','云南昭通市','2019-06-25']]

    ,
    "zlsys_yunnan_dehongzhou":[['德宏州','zfcg','yunnan_dehongzhou','云南德宏州','2019-06-25'],
            ['德宏州','gcjs','yunnan_dehongzhou','云南德宏州','2019-06-25']]
    ,
    "zlsys_yunnan_diqingzhou":[['迪庆州','zfcg','yunnan_diqingzhou','云南迪庆州','2019-06-25'],
            ['迪庆州','gcjs','yunnan_diqingzhou','云南迪庆州','2019-06-25']]

    ,
    "zlsys_yunnan_puershi":[['普洱市','zfcg','yunnan_puershi','云南普洱市','2019-06-25'],
            ['普洱市','gcjs','yunnan_puershi','云南普洱市','2019-06-25']]

    ,
    "zlsys_yunnan_baoshanshi":[['保山市','zfcg','yunnan_baoshanshi','云南保山市','2019-06-25'],
            ['保山市','gcjs','yunnan_baoshanshi','云南保山市','2019-06-25']]

    ,
    "zlsys_yunnan_lijiangshi":[['丽江市','zfcg','yunnan_lijiangshi','云南丽江市','2019-06-25'],
            ['丽江市','gcjs','yunnan_lijiangshi','云南丽江市','2019-06-25']],

    "zlsys_yunnan_yunnansheng":[['云南省','zfcg','yunnan_yunnansheng','云南省本级','2019-06-25'],
            ['云南省','gcjs','yunnan_yunnansheng','云南省本级','2019-06-25']],


    "zlsys_sichuan_suiningshi":[['遂宁市','zfcg','sichuan_suiningshi','四川遂宁市','2019-06-24'],
            ['遂宁市','gcjs','sichuan_suiningshi','四川遂宁市','2019-06-24']],


    "zlsys_sichuan_yibinshi":[['宜宾市','zfcg','sichuan_yibinshi','四川宜宾市','2019-06-26'],
            ['宜宾市','gcjs','sichuan_yibinshi','四川宜宾市','2019-06-26']],


    "zlsys_yunnan_tengchongshi":[['腾冲市','zfcg','yunnan_tengchongshi','云南腾冲市','2019-06-24'],
            ['腾冲市','gcjs','yunnan_tengchongshi','云南腾冲市','2019-06-24']],

    "zlsys_sichuan_yaanshi":[['雅安市','zfcg','sichuan_yaanshi','四川雅安市','2019-06-24'],
            ['雅安市','gcjs','sichuan_yaanshi','四川雅安市','2019-06-24']],






}



def task(city,tag=None):
    sts=settings[city]
    for st in sts:
        conp=[*conp_,st[2]]

        if tag is None:
            bdate=st[4]
        else:
            bdate=datetime.strftime(datetime.now()+timedelta(days=-3),'%Y-%m-%d')

        src_update_dates(st[0],st[1],conp,bdate)
        print("t_gg_update")
        t_gg_update(conp,'zlsys_%s'%st[2],st[3])

def restart_quyu(quyu):
    db,schema=quyu.split("_")[0],'_'.join(quyu.split("_")[1:])
    conp=[*conp_,schema]
    sql="drop schema if exists %s cascade;create schema if not exists %s"%(schema,schema)

    db_command(sql,dbtype="postgresql",conp=[*conp_,'public'])
    task(quyu)

def create_func():
    est_func(conp_)


def restart_all():
    for quyu in settings.keys():

        restart_quyu(quyu)
# restart_quyu('zlsys_yunnan_diqingzhou')