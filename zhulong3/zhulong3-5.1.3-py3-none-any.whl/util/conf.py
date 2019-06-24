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

    'shanxi': ["ankang", "baoji", "hanzhong", "xian", "xianyang", "yanan", "yulin","shenghui"],

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
            # tmp=["postgres","zhulong.com.cn","192.168.169.47",'gcjs',w+'_'+w1]

            data.append(tmp)

    df=pd.DataFrame(data=data,columns=["user",'password',"host","database","schema"])
    return df



def create_all_schemas():
    """
    一次性 创建所有模式
    :return:
    """
    conp = get_conp1('gcjs')
    for w in data1.keys():
        tmp1=data1[w]
        for w1 in tmp1:
            sql = "create schema if not exists %s" % (w+'_'+w1)
            db_command(sql, dbtype="postgresql", conp=conp)


def update_schemas(schema_list=[],drop_html=False):
    '''
        删除 爬虫数据库中 对应模式下的表
        :param schema_list: 一个包含多个schema的列表; list 格式
        :param drop_html: False 不删除gg_html;True 删除 gg_html;just 只删除gg_html
        :return:
    '''

    conp=get_conp1('gcjs')


    sql1='''select schemaname,tablename from pg_tables;'''
    tables=db_query(sql1,dbtype='postgresql',conp=conp)

    for table in tables.values:

        if drop_html == 'just':
            if (table[0] in schema_list) and ('gg_html' in table[1]):
                sql2 = '''drop table "%s"."%s" ''' % (table[0], table[1])
                db_command(sql2, dbtype="postgresql", conp=conp)
                print('已删除 %s.%s 表' % (table[0], table[1]))

        elif not drop_html:

            if (table[0] in schema_list) and ('gg_html' not in table[1]):
                sql2 = '''drop table "%s"."%s" ''' % (table[0], table[1])
                db_command(sql2, dbtype="postgresql", conp=conp)
                print('已删除 %s.%s 表' % (table[0], table[1]))

        else:
            if table[0] in schema_list:
                sql2 = '''drop table "%s"."%s" ''' % (table[0], table[1])
                db_command(sql2, dbtype="postgresql", conp=conp)
                print('已删除 %s.%s 表' % (table[0], table[1]))

    return 'over'


def create_cfg():
    """
    创建 cfg_db 数据库文件
    :return:
    """

    df=get_df()
    db_write(df,'cfg',dbtype='sqlite',conp=join(dirname(__file__),"cfg_db"))

    add_conp(["postgres","since2015","192.168.4.175",'gcjs','public'])
    # add_conp(["postgres","zhulong.com.cn","192.168.4.175",'gcjs','public'])
    # # # #
    df=query("select * from cfg")
    print(df.values)




def update_hawq(quyu,conp=None,mode='all'):
    """
    删除 hawq 中 对应分区
    :param quyu: 分区名
    :param conp: 连接参数
    :param mode: 选项 -- all: 删除 gg 和 gg_html 中分区, gg : 只删除gg中分区,html : 只删除 html 中分区
    :return:
    """
    from lmfhawq.zl import drop_partition_gghtml
    from lmfhawq.zl import drop_partition_gg

    if not conp:
        conp_list=[["postgres","zhulong.com.cn","192.168.169.57",'base_db','v'],
                   ["postgres","zhulong.com.cn","192.168.169.57",'base_db','src']]

    elif isinstance(conp[0],str):
        conp_list=[conp,]
    elif isinstance(conp[0],list):
        conp_list=conp
    else:
        raise TypeError('参数错误')

    for conp in conp_list:

        if mode=='all':
            drop_partition_gg(quyu,conp)
            drop_partition_gghtml(quyu,conp)
        elif mode == 'gg':
            drop_partition_gg(quyu,conp)
        elif mode == 'html':
            drop_partition_gghtml(quyu,conp)

