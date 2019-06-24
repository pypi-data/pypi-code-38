from zlsys.src import src_update,src_update_dates

settings={
"曲靖市":[('曲靖市','zfcg','yunnan_qujingshi','云南曲靖市','2019-06-22')]}

conp_=['postgres','since2015','192.168.4.175','zlsys']

def task(city):
    sts=settings[city]
    conp=[*conp,st[2]]
    for st in sts:
        src_update_dates(st[0],st[1],conp,'2019-06-22')
        
        t_gg_update(conp,'zlsys_%s'%st[2],'云南省曲靖市')