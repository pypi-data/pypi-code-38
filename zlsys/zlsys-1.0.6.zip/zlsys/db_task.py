from zlsys.src import src_update,src_update_dates
from zlsys.t_gg import t_gg_update
from datetime import datetime,timedelta
settings={
"曲靖市":[['曲靖市','zfcg','yunnan_qujingshi','云南曲靖市','2019-06-22'],
        ['曲靖市','gcjs','yunnan_qujingshi','云南曲靖市','2019-06-22']]

}

conp_=['postgres','since2015','192.168.4.175','zlsys']

def task(city,tag=None):
    sts=settings[city]
    for st in sts:
        conp=[*conp_,st[2]]
        if tag is None:
            bdate=st[4]
        else:
            bdate=datetime.strftime(datetime.now()+timedelta(days=-3),'%Y-%m-%d')
        src_update_dates(st[0],st[1],conp,bdate)
        
        t_gg_update(conp,'zlsys_%s'%st[2],'云南省曲靖市')