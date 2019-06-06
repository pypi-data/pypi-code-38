from lmf.dbv2 import db_command, db_write, db_query
import pandas as pd

from os.path import join, dirname


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
    data1 = {
        'shandong': ['anqiu', 'binzhou', 'dezhou', 'dongying', 'feicheng', 'heze', 'jiaozhou', 'jinan', 'jining', 'laiwu',
                     'leling', 'liaocheng', 'linqing', 'linyi', 'pingdu', 'qingdao', 'qufu', 'rizhao', 'rongcheng',
                     'rushan', 'shandong', 'taian', 'tengzhou', 'weifang', 'weihai', 'xintai', 'yantai', 'yucheng',
                     'zaozhuang', 'zibo', 'zoucheng'],
        'hubei': ['dangyang', 'enshi', 'huanggang', 'huangshi', 'jingmen', 'lichuan', 'shiyan', 'suizhou', 'wuhan',
                  'xiangyang', 'yichang', 'yidu', 'xiaogan'],
        'hainan': ['danzhou', 'dongfang', 'haikou', 'hainan', 'qionghai', 'sansha', 'sanya'],
        'jiangsu': ['changshu', 'changzhou', 'danyang', 'dongtai', 'huaian', 'jiangsu', 'jiangyin', 'kunshan',
                    'lianyungang', 'nanjing', 'nantong', 'suqian', 'suzhou', 'taizhou', 'wuxi', 'xinyi', 'xuzhou',
                    'yancheng', 'yangzhou', 'yizheng', 'zhangjiagang', 'zhenjiang'],
        'jilin': ['baicheng', 'baishan', 'changchun', 'jilin', 'jilinshi', 'liaoyuan', 'siping', 'songyuan', 'tonghua'],
        'guangdong': ['guangzhou', 'heyuan', 'huizhou', 'jiangmen', 'jieyang', 'lianzhou', 'meizhou', 'nanxiong',
                      'shaoguan', 'shenzhen', 'sihui', 'yingde', 'yunfu', 'zhanjiang', 'zhaoqing', 'zhongshan', 'zhuhai'
            , "dongguan", "qingyuan", "chaozhou", "shantou", "shanwei", "foshan", "yangjiang", "maoming", "guangdong"],
        'neimenggu': ['baotou', 'bayannaoer', 'chifeng', 'eeduosi', 'huhehaote', 'hulunbeier', 'manzhouli', 'neimenggu',
                      'tongliao', 'wuhai', 'wulanchabu', 'xilinguolemeng', 'xinganmeng', 'alashan'],
        'fujian': ['fujian', 'fuqing', 'fuzhou', 'jianou', 'longyan', 'nanan', 'nanping', 'ningde', 'putian', 'quanzhou',
                   'sanming', 'shaowu', 'wuyishan', 'xiamen', 'yongan', 'zhangzhou'], 'qinghai': ['qinghai', 'xining'],
        'chongqing': ['yongchuan','chongqing'],
        'shanxi': ['chenzhou', 'shanxi', 'weinan', 'xian', 'xianyang', 'yanan'],
        'xinjiang': ['beitun', 'kezhou', 'wulumuqi', 'xinjiang', 'akesu'],
        'ningxia': ['guyuan', 'ningxia', 'yinchuan'],
        'jiangxi': ['dexing', 'fengcheng', 'fuzhou', 'ganzhou', 'gaoan', 'jian', 'jiangxi', 'jingdezhen', 'jingdezhen2', 'jinggangshan',
                    'lushan', 'nanchang', 'ruichang', 'ruijin', 'shangrao', 'xinyu', 'yichun', 'yingtan', 'zhangshu'],
        'henan': ['anyang', 'dengfeng', 'gongyi', 'hebi', 'jiaozhuo', 'jiyuan', 'jiyuan1', 'kaifeng', 'linzhou', 'luohe',
                  'luoyang', 'mengzhou', 'nanyang', 'pingdingshan', 'puyang', 'qinyang', 'ruzhou', 'sanmenxia', 'shangqiu',
                  'weihui', 'wugang', 'xinmi', 'xinxiang', 'xinyang', 'xinzheng', 'xuchang', 'yanshi', 'yongcheng',
                  'zhengzhou', 'zhoukou', 'zhumadian'],
        'shanxi1': ['shanxi', 'shanxi2'],
        'xizang': ['lasa', 'rikaze', 'xizang'],
        'sichuan': ['bazhong', 'chengdu', 'chongzhou', 'dazhou', 'deyang', 'dujiangyan', 'guangan', 'guanghan',
                    'guangyuan', 'jiangyou', 'jianyang', 'leshan', 'longchang', 'luzhou', 'meishan', 'mianyang',
                    'mianyang1', 'mianyang2', 'nanchong', 'neijiang', 'panzhihua', 'pengzhou', 'qionglai', 'shifang',
                    'sichuan', 'sichuan2', 'suining', 'wanyuan', 'yaan', 'yibin'],
        'guangxi': ['baise', 'beihai', 'chongzuo', 'fangchenggang', 'guangxi', 'guigang', 'guilin', 'hechi', 'hezhou',
                    'laibin', 'liuzhou', 'nanning', 'qinzhou', 'wuzhou'],
        'hunan': ['changde', 'changsha', 'chenzhou', 'hengyang', 'huaihua', 'liling', 'liuyang', 'loudi', 'hunan', 'shaoyang',
                  'xiangtan', 'yiyang', 'yongzhou', 'yuanjiang', 'yueyang', 'zhangjiajie', 'zhuzhou'],
        'zhejiang': ['cixi', 'dongyang', 'hangzhou', 'huzhou', 'jiaxing', 'jinhua', 'linhai', 'lishui', 'longquan',
                     'ningbo', 'pinghu', 'quzhou', 'ruian', 'shaoxing', 'shengzhou', 'taizhou', 'tongxiang', 'wenling',
                     'wenzhou', 'yiwu', 'yueqing', 'yuhuan', 'zhejiang', 'zhoushan', 'zhuji'],
        'yunnan': ['baoshan', 'chuxiong', 'dali', 'kunming', 'lijiang', 'lincang', 'puer', 'tengchong', 'wenshan',
                   'yunnan', 'yuxi', 'zhaotong'],
        'heilongjiang': ['daqing', 'haerbin_gcjs', 'haerbin_zfcg', 'hegang', 'heilongjiang', 'qiqihaer', 'yichun'],
        'liaoning': ['anshan', 'beizhen', 'benxi', 'chaoyang', 'dalian', 'dandong', 'donggang', 'fushun', 'fuxin',
                     'haicheng', 'huludao', 'jinzhou', 'liaoning', 'liaoyang', 'panjin', 'shenyang', 'tieling', 'yingkou'],
        'anhui': ['anqing', 'bengbu', 'bozhou', 'chaohu', 'chizhou', 'chuzhou', 'fuyang', 'hefei', 'huaibei', 'huainan',
                  'huangshan', 'luan', 'maanshan', 'suzhou', 'tongling', 'wuhu', 'xuancheng'],
        'guizhou': ["anshun", "bijie", "guiyang", "liupanshui", "shenghui", "tongren", "shenghui2", "zunyi", ],
        'gansu': ["baiyin", "dingxi", "gansu", "jiayuguan", "jiuquan", "lanzhou", "longnan", "pingliang", "qingyang", "tianshui", "wuwei",
                  "zhangye", ]

    }
    data = []
    print('total', len(data1.values()))
    i = 0
    for w in data1.keys():
        tmp1 = data1[w]
        for w1 in tmp1:
            tmp = ["postgres", "since2015", "127.0.0.1", w, w1]
            print(tmp)
            i += 1
            data.append(tmp)
    print(i)
    df = pd.DataFrame(data=data, columns=["user", 'password', "host", "database", "schema"])
    return df


def get_df1():
    data = []

    for w in data1.keys():
        tmp1 = data1[w]
        for w1 in tmp1:
            tmp = ["postgres", "since2015", "192.168.4.175", w, w1]

            data.append(tmp)

    df = pd.DataFrame(data=data, columns=["user", 'password', "host", "database", "schema"])
    return df

# gcjs
# def create_all_schemas():
#     conp = get_conp1('gcjs')
#     for w in data1.keys():
#         tmp1=data1[w]
#         for w1 in tmp1:
#             sql = "create schema if not exists %s" % (w+'_'+w1)
#             db_command(sql, dbtype="postgresql", conp=conp)


#
# df=get_df()
# print(len(df),df)
# db_write(df,'cfg',dbtype='sqlite',conp=join(dirname(__file__),"cfg_db"))
# # #
#
# # add_conp(["postgres","since2015","192.168.4.175",'jiangxi','yichun'])
# # # #
# df = query("select * from cfg")
# print(len(df.values))
# print(df.values)
# 335
