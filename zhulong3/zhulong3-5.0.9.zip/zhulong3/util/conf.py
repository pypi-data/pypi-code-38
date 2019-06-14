from lmf.dbv2 import db_command ,db_write,db_query 

from os.path import join ,dirname

import pandas as pd



def get_conp(name,database=None):
    path1=join(dirname(__file__),"cfg_db")
    if database is None:
        df=db_query("select * from cfg where schema='%s' "%name,dbtype='sqlite',conp=path1)
    else:
        df=db_query("select * from cfg where schema='%s' and database='%s' "%(name,database),dbtype='sqlite',conp=path1)
    conp=df.values.tolist()[0]
    return conp

def get_conp1(name):
    path1=join(dirname(__file__),"cfg_db")

    df=db_query("select * from cfg where database='%s' and schema='public' "%name,dbtype='sqlite',conp=path1)
    conp=df.values.tolist()[0]
    return conp





def command(sql):
    path1=join(dirname(__file__),"cfg_db")
    db_command(sql,dbtype="sqlite",conp=path1)

def query(sql):
    path1=join(dirname(__file__),"cfg_db")
    df=db_query(sql,dbtype='sqlite',conp=path1)
    return df 

def update(user=None,password=None,host=None):

    if host is not None:
        sql="update cfg set host='%s' "%host
        command(sql)
    if user is not None:
        sql="update cfg set user='%s' "%user
        command(sql)
    if password is not None:
        sql="update cfg set password='%s' "%password
        command(sql)

def add_conp(conp):
    sql="insert into cfg values('%s','%s','%s','%s','%s')"%(conp[0],conp[1],conp[2],conp[3],conp[4])
    command(sql)


data1 = {
    "jiangxi": ["jiujiang", "nanchang", "pingxiang", "shangrao"],

    "hunan": ['changsha1', 'changsha2', 'huaihua', 'loudi', 'shaoyang', 'shenghui', 'wugang', 'yueyang'],

    "fujian": ["fuqing", "fuzhou", 'quanzhou', 'sanming', 'zhangzhou'],

    'guangdong': ["shantou", 'shaoguan', 'shenghui', 'shenzhen', "yangjiang", "yunfu", "zhongshan","dongguan"],

    'henan': ["kaifeng", 'pingdingshan', 'puyang', 'sanmenxia', 'zhengzhou'],

    'shandong': ["dongying", 'heze', 'jinan', 'linyi', 'rizhao', 'shenghui', 'zaozhuang'],

    'anhui': ['huainan', 'xuancheng'],

    'hebei': ["shenghui", "langfang", "shijiazhuang", "tangshan", "xingtai"],

    'heilongjiang': ["shenghui", "haerbin", "qqhaer"],

    'jiangsu': ["shenghui", "changzhou", "nanjing", "nantong", "yangzhou"],

    'jilin': ["shenghui", "changchun", "jilin", "siping", "tonghua"],

    'liaoning': ["shenghui", "dalian", "shenyang"],

    'neimenggu': ["shenghui"],

    'gansu': ["shenghui"],

    'guangxi': ["baise", "beihai", "fangchenggang", "shenghui", "qinzhou"],

    'guizhou': ["shenghui"],

    'ningxia': ["shenghui"],

    'shanxi': ["ankang", "baoji", "hanzhong", "xian", "xianyang", "yanan", "yulin"],

    'sichuan': ["bazhong", "chengdu", "mianyang", "shenghui", "zigong"],

    'xinjiang': ["yining", "shenghui", "wulumuqi", "tacheng", "kashi", "hami", "changji", "bole", "atushi", "akesu"],

    'shanxi1': ["datong", "linfen", "taiyuan", "xinzhou", "xinzhou2","changzhi"],

    'zhejiang': ["hangzhou", "zhoushan", "shenghui", "huzhou","jinhua"],

    'zhixiashi': ["beijing","tianjin", "shanghai", "chongqing",],
}

def get_df():

    data=[]

    for w in data1.keys():
        tmp1=data1[w]
        for w1 in tmp1:
            tmp=["postgres","since2015","192.168.4.175",'gcjs',w+'_'+w1]

            data.append(tmp)

    df=pd.DataFrame(data=data,columns=["user",'password',"host","database","schema"])
    return df



def create_all_schemas():
    conp = get_conp1('gcjs')
    for w in data1.keys():
        tmp1=data1[w]
        for w1 in tmp1:
            sql = "create schema if not exists %s" % (w+'_'+w1)
            db_command(sql, dbtype="postgresql", conp=conp)




# df=get_df()
# db_write(df,'cfg',dbtype='sqlite',conp=join(dirname(__file__),"cfg_db"))
# #
#
# add_conp(["postgres","since2015","192.168.4.175",'gcjs','public'])
# # # # #
# df=query("select * from cfg")
# print(df.values)


