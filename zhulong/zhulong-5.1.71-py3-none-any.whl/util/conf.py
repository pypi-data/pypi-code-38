from lmf.dbv2 import db_command, db_write, db_query
import pandas as pd
from os.path import join, dirname
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

zhulong_diqu_dict = {
    'beijing':['beijing'],
    'shandong': ['anqiu', 'binzhou', 'dezhou', 'dongying', 'feicheng', 'heze', 'jiaozhou', 'jinan', 'jining', 'laiwu',
                 'leling', 'liaocheng', 'linqing', 'linyi', 'pingdu', 'qingdao', 'qufu', 'rizhao', 'rongcheng',
                 'rushan', 'shandong', 'taian', 'tengzhou', 'weifang', 'weihai', 'xintai', 'yantai', 'yucheng',
                 'zaozhuang', 'zibo', 'zoucheng', 'public', 'shandong2'],
    'hubei': ['dangyang', 'enshi', 'huanggang', 'huangshi', 'jingmen', 'lichuan', 'shiyan', 'suizhou', 'wuhan',
              'xiangyang', 'yichang', 'yidu', 'xiaogan', 'public'],
    'hainan': ['danzhou', 'dongfang', 'haikou', 'hainan', 'qionghai', 'sansha', 'sanya', 'public'],
    'jiangsu': ['changshu', 'changzhou', 'danyang', 'dongtai', 'huaian', 'jiangsu', 'jiangyin', 'kunshan',
                'lianyungang', 'nanjing', 'nantong', 'suqian', 'suzhou', 'taizhou', 'wuxi', 'xinyi', 'xuzhou',
                'yancheng', 'yangzhou', 'yizheng', 'zhangjiagang', 'zhenjiang', 'public'],
    'jilin': ['baicheng', 'baishan', 'changchun', 'jilin', 'jilinshi', 'liaoyuan', 'siping', 'songyuan', 'tonghua', 'public'],
    'guangdong': ['guangzhou', 'heyuan', 'huizhou', 'jiangmen', 'jieyang', 'lianzhou', 'meizhou', 'nanxiong',
                  'shaoguan', 'shenzhen', 'sihui', 'yingde', 'yunfu', 'zhanjiang', 'zhaoqing', 'zhongshan', 'zhuhai'
        , "dongguan", "qingyuan", "chaozhou", "shantou", "shanwei", "foshan", "yangjiang", "maoming", "guangdong", 'public'],
    'neimenggu': ['baotou', 'bayannaoer', 'chifeng', 'eeduosi', 'huhehaote', 'hulunbeier', 'manzhouli', 'neimenggu',
                  'tongliao', 'wuhai', 'wulanchabu', 'xilinguolemeng', 'xinganmeng', 'alashan', 'public'],
    'fujian': ['fujian', 'fuqing', 'fuzhou', 'jianou', 'longyan', 'nanan', 'nanping', 'ningde', 'putian', 'quanzhou',
               'sanming', 'shaowu', 'wuyishan', 'xiamen', 'yongan', 'zhangzhou', 'public', 'fujian2'],
    'qinghai': ['qinghai', 'xining', 'public'],
    'chongqing': ['yongchuan', 'chongqing', 'public'],
    'shanxi': ['chenzhou', 'shanxi', 'weinan', 'xian', 'xianyang', 'yanan', 'public', 'ankang', 'xianyang2'],
    'xinjiang': ['beitun', 'kezhou', 'wulumuqi', 'xinjiang', 'akesu', 'public', 'aletai'],
    'ningxia': ['guyuan', 'ningxia', 'yinchuan', 'public'],
    'jiangxi': ['dexing', 'fengcheng', 'fuzhou', 'ganzhou', 'gaoan', 'jian', 'jiangxi', 'jingdezhen', 'jingdezhen2', 'jinggangshan',
                'lushan', 'nanchang', 'ruichang', 'ruijin', 'shangrao', 'xinyu', 'yichun', 'yingtan', 'zhangshu', 'public'],
    'henan': ['anyang', 'dengfeng', 'gongyi', 'hebi', 'jiaozhuo', 'jiyuan', 'jiyuan1', 'kaifeng', 'linzhou', 'luohe',
              'luoyang', 'mengzhou', 'nanyang', 'pingdingshan', 'puyang', 'qinyang', 'ruzhou', 'sanmenxia', 'shangqiu',
              'weihui', 'wugang', 'xinmi', 'xinxiang', 'xinyang', 'xinzheng', 'xuchang', 'yanshi', 'yongcheng',
              'zhengzhou', 'zhoukou', 'zhumadian', 'public'],
    'shanxi1': ['shanxi', 'shanxi2', 'public'],
    'xizang': ['lasa', 'rikaze', 'xizang', 'public'],
    'sichuan': ['bazhong', 'chengdu', 'chongzhou', 'dazhou', 'deyang', 'dujiangyan', 'guangan', 'guanghan',
                'guangyuan', 'jiangyou', 'jianyang', 'leshan', 'longchang', 'luzhou', 'meishan', 'mianyang',
                'mianyang1', 'mianyang2', 'nanchong', 'neijiang', 'panzhihua', 'pengzhou', 'qionglai', 'shifang',
                'sichuan', 'sichuan2', 'suining', 'wanyuan', 'yaan', 'yibin', 'public', 'zigong', 'ziyang'],
    'guangxi': ['baise', 'beihai', 'chongzuo', 'fangchenggang', 'guangxi', 'guigang', 'guilin', 'hechi', 'hezhou',
                'laibin', 'liuzhou', 'nanning', 'qinzhou', 'wuzhou', 'public'],
    'hunan': ['changde', 'changsha', 'chenzhou', 'hengyang', 'huaihua', 'liling', 'liuyang', 'loudi', 'hunan', 'shaoyang',
              'xiangtan', 'yiyang', 'yongzhou', 'yuanjiang', 'yueyang', 'zhangjiajie', 'zhuzhou', 'xiangxi', 'public'],
    'zhejiang': ['cixi', 'dongyang', 'hangzhou', 'huzhou', 'jiaxing', 'jinhua', 'linhai', 'lishui', 'longquan',
                 'ningbo', 'pinghu', 'quzhou', 'ruian', 'shaoxing', 'shengzhou', 'taizhou', 'tongxiang', 'wenling',
                 'wenzhou', 'yiwu', 'yueqing', 'yuhuan', 'zhejiang', 'zhoushan', 'zhuji', 'public'],
    'yunnan': ['baoshan', 'chuxiong', 'dali', 'kunming', 'lijiang', 'lincang', 'puer', 'tengchong', 'wenshan',
               'yunnan', 'yuxi', 'zhaotong', 'public', "xishuangbanna", "dehong", "honghe", "yunnan2", ],
    'heilongjiang': ['daqing', 'haerbin_gcjs', 'haerbin_zfcg', 'hegang', 'heilongjiang', 'qiqihaer', 'yichun', 'public'],
    'liaoning': ['anshan', 'beizhen', 'benxi', 'chaoyang', 'dalian', 'dandong', 'donggang', 'fushun', 'fuxin',
                 'haicheng', 'huludao', 'jinzhou', 'liaoning', 'liaoyang', 'panjin', 'shenyang', 'tieling', 'yingkou', 'public'],
    'anhui': ['anqing', 'bengbu', 'bozhou', 'chaohu', 'chizhou', 'chuzhou', 'fuyang', 'hefei', 'huaibei', 'huainan',
              'huangshan', 'luan', 'maanshan', 'suzhou', 'tongling', 'wuhu', 'xuancheng', 'public'],
    'guizhou': ["anshun", "bijie", "guiyang", "liupanshui", "shenghui", "tongren", "shenghui2", "zunyi",
                "qiandong", "qianxi", "qiannan", 'public'],
    'gansu': ["baiyin", "dingxi", "gansu", "jiayuguan", "jiuquan", "lanzhou", "longnan", "pingliang", "qingyang", "tianshui", "wuwei",
              "zhangye", 'public'],
    'hebei': ["hebei", 'public']

}

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


def get_df():
    data1 = zhulong_diqu_dict

    data = []
    print('total', len(data1.values()))
    i = 0
    for w in data1.keys():
        tmp1 = data1[w]
        for w1 in tmp1:
            tmp = ["postgres", "since2015", "192.168.4.175", w, w1]
            print(tmp)
            i += 1
            data.append(tmp)
    print(i)
    df = pd.DataFrame(data=data, columns=["user", 'password', "host", "database", "schema"])
    return df


def update_schemas(database=None, schema_list=[], drop_html=False):
    """

    :param database: 数据库名
    :param schema_list: 一个包含多个schema的列表; list 格式
    :param drop_html: False 不删除gg_html;True 删除 gg_html;just 只删除gg_html
    :return:
    """

    conp = get_conp1(database)

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


def create_all_schemas():
    conp = get_conp1('anhui')
    for w in zhulong_diqu_dict.keys():
        conp[3] = w
        conn = psycopg2.connect(database=conp[0], port='5432', host=conp[2], user=conp[0], password=conp[1])
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='%s'" % conp[3])
        res = cursor.fetchone()
        if not res:
            cursor.execute("create database %s" % conp[3])

        tmp1 = zhulong_diqu_dict[w]
        for w1 in tmp1:
            conp[4] = w1
            db_command("create schema if not exists %s" % (conp[4]), dbtype="postgresql", conp=conp)

# df=get_df()
# print(len(df),df)
# db_write(df,'cfg',dbtype='sqlite',conp=join(dirname(__file__),"cfg_db"))
# #
#
# # add_conp(["postgres","since2015","192.168.4.175",'jiangxi','yichun'])
# # # #
# df = query("select * from cfg")
# print(len(df.values))
# print(df.values)
# 335
# create_all_schemas()
