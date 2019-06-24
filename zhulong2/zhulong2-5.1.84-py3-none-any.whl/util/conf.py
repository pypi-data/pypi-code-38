from lmf.dbv2 import db_command, db_write, db_query
from os.path import join, dirname
import pandas as pd


def get_conp(name, database=None):
    path1 = join(dirname(__file__), "cfg_db")
    if database is None:
        df = db_query("select * from cfg where schema='%s' " % name, dbtype='sqlite', conp=path1)
    else:
        df = db_query("select * from cfg where schema='%s' and database='%s' " % (name, database), dbtype='sqlite',
                      conp=path1)
    conp = df.values.tolist()[0]
    return conp


def get_conp1(name):
    path1 = join(dirname(__file__), "cfg_db")

    df = db_query("select * from cfg where database='%s' and schema='public' " % name, dbtype='sqlite', conp=path1)
    conp = df.values.tolist()[0]
    return conp


def command(sql):
    path1 = join(dirname(__file__), "cfg_db")
    db_command(sql, dbtype="sqlite", conp=path1)


def query(sql):
    path1 = join(dirname(__file__), "cfg_db")
    df = db_query(sql, dbtype='sqlite', conp=path1)
    return df


def update(user=None, password=None, host=None):
    if host is not None:
        sql = "update cfg set host='%s' " % host
        command(sql)
    if user is not None:
        sql = "update cfg set user='%s' " % user
        command(sql)
    if password is not None:
        sql = "update cfg set password='%s' " % password
        command(sql)


def add_conp(conp):
    sql = "insert into cfg values('%s','%s','%s','%s','%s')" % (conp[0], conp[1], conp[2], conp[3], conp[4])
    command(sql)


data1 = {
        "beijing": ["beijing"],

        'gansu': ["shenghui", "jinchang"],

        'guangdong': ['shenghui', "dongguan", "guangzhou", 'shenzhen',"shantou","zhongshan"],

        'guangxi': ["baise", "fangchenggang", "shenghui", "guigang", "guilin", "liuzhou", "nanning", "qinzhou",
                    "wuzhou"],

        'guizhou': ["shenghui","tongren"],

        'hainan': ["haikou", "shenghui", "sanya", "wenchang"],

        'ningxia': ["shenghui","yinchuan"],

        'qinghai': ["shenghui"],

        'shanxi': ["shenghui","hanzhong","shangluo","xian"],

        'sichuan': ["shenghui", "mianyang"],

        'tianjin': ["tianjin"],

        'xinjiang': ["akesu", "alashankou", "shenghui", "shenghui2", "changji", "hetian", "wulumuqi", "kashi",
                     "kelamayi", "tacheng", "tulufan", "yining", "changji2"],

        'xizang': ["shenghui","shannan"],

        'yunnan': ["shenghui", "yuxi"],
        # lch
        'fujian': ['nanping', 'sanming', 'sanming1',"fuzhou","longyan","nanping1","ningde","putian","quanzhou","xiamen","zhangzhou"],

        'henan': ['anyang', 'hebi', 'henan', 'jiaozuo', 'kaifeng', 'luohe', 'luoyang', 'nanyang', 'pingdingshan',
                  'puyang', 'sanmenxia', 'shangqiu', 'xinxiang', 'xinyang', 'xuchang', 'zhengzhou', 'zhoukou',
                  'zhumadian'],

        'hubei': ['ezhou', 'huanggang', 'hubei', 'jingmen', 'shiyan', 'wuhan', 'wuhan2'],

        'jiangxi': ['jian', 'jiangxi', 'nanchang', 'pingxiang'],

        'hunan': ['changde', 'changsha', 'chenzhou', 'hengyang', 'hunan', 'xiangtan', 'yiyang', 'yueyang',
                  'zhangjiajie', 'zhuzhou','changsha2','loudi'],

        'shandong': ['dezhou', 'dongying', 'laiwu', 'liaocheng', 'linyi', 'qingdao', 'rizhao', 'shandong', 'weihai',
                     'yantai'],

        'chongqing': ["chongqing"],

        # lab
        'anhui': ['anqing', 'huainan', 'shenghui', 'luan', 'wuhu'],
        #
        'hebei': ["shenghui"],
        #
        'heilongjiang': ["shenghui", "yichun"],

        #
        'jiangsu': ['shenghui', 'changzhou', 'huaian', 'lianyungang', 'nanjing', 'nantong', 'suzhou',
                    'suqian', 'taizhou', 'wuxi', 'xuzhou', 'yangzhou','xuzhou2','yancheng','zhenjiang'],
        #
        'jilin': ['shenghui', 'changchun', 'jilin'],
        #
        'liaoning': ['dalian', 'chaoyang', 'shenyang', 'wafangdian','changchun'],
        #
        'neimenggu': ['huhehaote', 'shenghui', 'baotou', 'eerduosi', 'tongliao','bayannaoer'],

        'shanxi1': ['shenghui', 'yuncheng', 'taiyuan','changzhi'],
        #
        'zhejiang': ['ningbo', 'shenghui', 'hangzhou', 'wenzhou','quzhou']

    }


def get_df():
    data = []
    for w in data1.keys():
        tmp1 = data1[w]
        for w1 in tmp1:
            tmp = ["postgres", "since2015", "192.168.4.175", 'zfcg', w + '_' + w1]
            data.append(tmp)

    df = pd.DataFrame(data=data, columns=["user", 'password', "host", "database", "schema"])
    return df



def create_all_schemas():
    conp = get_conp1('zfcg')
    for w in data1.keys():
        tmp1=data1[w]
        for w1 in tmp1:
            sql = "create schema if not exists %s" % (w+'_'+w1)
            db_command(sql, dbtype="postgresql", conp=conp)



def update_schemas(schema_list=[] ,drop_html=False):
    '''
        :param schema_list: 一个包含多个schema的列表; list 格式
        :param drop_html: False 不删除gg_html;True 删除gg_html;just 只删除gg_html
        :return:
    '''
    conp = get_conp1('zfcg')
    sql1 = '''select schemaname,tablename from pg_tables;'''
    tables = db_query(sql1, dbtype='postgresql', conp=conp)
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


# 生成cfg_db
# df=get_df()
# db_write(df,'cfg',dbtype='sqlite',conp=join(dirname(__file__),"cfg_db"))
# add_conp(["postgres","since2015","192.168.4.175",'zfcg','public'])

# 查看cfg_db
# df=query("select * from cfg")
# print(df.values)
