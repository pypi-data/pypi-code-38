from zhulong.db.cdc import update_sheng 


#更新全部省

def update_all():

    tasks=['yunnan','anhui','zhejiang','shandong','fujian','guangdong',"hunan","hubei","guangxi","hainan"
    ,"jiangsu","jiangxi","jilin","liaoning","neimenggu","ningxia","qinghai","shanxi1","sichuan","xizang"
    ,"chongqing"
    ]



    for sheng in tasks:
        conp1=["postgres",'since2015',"192.168.4.175","base",'public'] #
        conp2=["postgres",'since2015',"192.168.4.175",sheng,'public']
        update_sheng(conp1,conp2)



#导表到业务库


