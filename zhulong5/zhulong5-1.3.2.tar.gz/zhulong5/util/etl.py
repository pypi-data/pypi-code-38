import re
from datetime import datetime

from lmf.dbv2 import db_command, db_query
import json
from zhulong5.util.multipage import web
from dateutil.relativedelta import relativedelta
from zhulong5.util.downhtml import page
import time


# 表名解析器

# tb="gcjs_jiaotong_zhongbiaohx_gg"

def ext_tb(tbname):
    tb_arr = tbname.split("_")

    a = {}
    # jytype_set={'gcjs','zfcg'}
    # ggtype_set={'zhaobiao','zhongbiao','zhongbiaohx','biangen','liubiao','qita',"kongzhijia","yucai"}
    jytype_dict = {"gcjs": "工程建设", "zfcg": "政府采购", "ylcg": "医疗采购", "yiliao": "医疗采购", "jqita": "其它类型", "qsydw": "企事业单位",
                   "qsy": "企事业单位", "yycg": "医疗采购"
                   }

    ggtype_dict = {"zhaobiao": "招标公告", "zhongbiao": "中标公告", "zhongbiaohx": "中标候选公告", "liubiao": "流标公告",
                   "biangen": "变更公告", "qita": "其他公告", "kongzhijia": "控制价公告", "yucai": "预采公告", "yanshou": "验收公告",
                   "biangeng": "变更公告", "hetong": "合同公告", "gqita": "其它类型", "yvcai": "预采公告", 'bian': "变更公告"
                   }
    ggtype_set = set(ggtype_dict)
    jytype_set = set(jytype_dict)

    xmztype_set = {"fangwu", "jiaotong", "shuili", "shizheng", "dianli"}
    for w in tb_arr:
        if w in jytype_set:
            a["jytype"] = jytype_dict[w]
        if w in ggtype_set:
            a["ggtype"] = ggtype_dict[w]
    if "ggtype" not in a.keys(): a["ggtype"] = None
    if "jytype" not in a.keys(): a["jytype"] = None
    return a


def create_gg(conp):
    sql1 = """
    drop table if exists %s.gg;
    create table if not exists %s.gg
    (
    name text,
    ggstart_time text,
    href text,
    xiangmu_code text,
    shenpishixiang text,
    shenpibumen text,
    statu  text,
    diqu text,
    info  text 

    )
    """ % (conp[4], conp[4])

    db_command(sql1, dbtype="postgresql", conp=conp)
    print('删除并创建新的gg表')


def insert_tb(tbname, diqu, conp):
    data = ext_tb(tbname)

    schema = conp[4]

    sql2 = """
    insert into %s.gg select  * from %s.%s
    """ % (schema, schema, tbname)

    db_command(sql2, dbtype="postgresql", conp=conp)


def gg_distinc(conp, **arg):
    sql = """
    delete from %s.gg
    where ctid in (select ctid from (select row_number() over(partition by name,href,ggstart_time order by ctid) as rn , ctid from %s.gg) t 
    where t.rn <>1);
    """ % (conp[4], conp[4])
    db_command(sql, dbtype='postgresql', conp=conp)
    print("gg 表去重完毕。")


# 第一次形成gg表
def gg(conp, diqu, i=-1):
    create_gg(conp)
    sql = """
    select table_name from information_schema.tables where table_schema='%s' and table_name ~'_gg$' order by table_name
    """ % conp[4]

    df = db_query(sql, conp=conp, dbtype="postgresql")
    data = df['table_name'].tolist()
    if i == -1:
        data = data
    else:
        data = data[i:i + 1]
    for tbname in data:
        insert_tb(tbname, diqu=diqu, conp=conp)
    gg_distinc(conp)


# 后续更新公告表

def gg_cdc(conp, diqu, i=-1):
    # create_gg(conp)
    sql = """
    select table_name from information_schema.tables where table_schema='%s' and table_name ~'_gg_cdc$' order by table_name
    """ % conp[4]

    df = db_query(sql, conp=conp, dbtype="postgresql")
    data = df['table_name'].tolist()
    if i == -1:
        data = data
    else:
        data = data[i:i + 1]
    for tbname in data:
        insert_tb(tbname, diqu=diqu, conp=conp)
    gg_distinc(conp)


# 一次爬入所有
def work(conp, data, diqu, i=-1, headless=True):
    data = data.copy()
    if i == -1:
        data = data
    else:
        data = data[i:i + 1]
    for w in data:
        setting = {
            "url": w[1],
            "f1": w[3],
            "f2": w[4],
            "tb": w[0],
            "col": w[2],
            "conp": conp,
            "num": 10,
            "headless": headless
        }
        m = web()
        m.write(**setting)
    gg(conp, diqu)


def cdc_sql(conp, tb):
    schema = conp[4]
    sql = """insert into %s.%s
    select * from %s.%s_cdc 

    except 

    select * from %s.%s
    """ % (schema, tb, schema, tb, schema, tb)
    db_command(sql, dbtype="postgresql", conp=conp)


def cdc(conp, data, diqu, i=-1, headless=True):
    data = data.copy()
    if i == -1:
        data = data
    else:
        data = data[i:i + 1]
    for w in data:
        setting = {
            "url": w[1],
            "f1": w[3],
            "f2": w[4],
            "tb": w[0] + "_cdc",
            "col": w[2],
            "conp": conp,
            "num": 4,
            "total": 10,
            "headless": headless
        }
        m = web()
        m.write(**setting)
        cdc_sql(conp, w[0])

    gg_cdc(conp, diqu)


def est_tables_cdc(conp, data, headless=True):
    data = data.copy()

    for w in data:
        setting = {
            "url": w[1],
            "f1": w[3],
            "f2": w[4],
            "tb": w[0] + "_cdc",
            "col": w[2],
            "conp": conp,
            "num": 4,
            "total": 10,
            "headless": headless
        }
        m = web()
        m.write(**setting)
        cdc_sql(conp, w[0])


def gg_meta(conp, data, diqu, i=-1, headless=True):
    sql = """select table_name from information_schema.tables where table_schema='%s'""" % (conp[4])
    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df["table_name"].values

    if "gg" in arr or 'quanguoxiangmu' in arr[0] or 'quanguoxiangmu' in arr[1]:
        cdc(conp, data, diqu, i, headless)
    else:
        work(conp, data, diqu, i, headless)


#####################################################get_html##########################################


def html_work(conp, f, size=None, headless=True):
    m = page()
    if size is not None:
        sql = "select distinct href from %s.gg where not coalesce(info,'{}')::jsonb?'hreftype' or coalesce(info,'{}')::jsonb->>'hreftype'='可抓网页' limit %d" % (
            conp[4], size)
    else:
        sql = "select distinct href from %s.gg where not coalesce(info,'{}')::jsonb?'hreftype' or coalesce(info,'{}')::jsonb->>'hreftype'='可抓网页' " % (
            conp[4])

    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df["href"].values
    print(arr[:3])
    setting = {"num": 20, "arr": arr, "f": f, "conp": conp, "tb": "gg_html", "headless": headless}
    m.write(**setting)


"""
update  "weihai"."gg"

set info=coalesce(info,'{}')::jsonb ||'{"hreftype":"不可抓网页"}'
 where  href in (select distinct href from weihai.gg where href not in(select href from weihai.gg_html ) 


and (not coalesce(info,'{}')::jsonb?'hreftype' or coalesce(info,'{}')::jsonb->>'hreftype'='可抓网页'))

"""


def html_cdc(conp, f, headless=True):
    m = page()
    sql = "select distinct href from %s.gg where href not in(select href from %s.gg_html ) and (not coalesce(info,'{}')::jsonb?'hreftype' or coalesce(info,'{}')::jsonb->>'hreftype'='可抓网页')" % (
        conp[4], conp[4])

    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df["href"].values
    if arr == []:
        print("无href更新")
        return None

    setting = {"num": 5, "arr": arr, "f": f, "conp": conp, "tb": "gg_html", "headless": headless}
    m.write(**setting)


def gg_html(conp, f, headless=True):
    sql = """select table_name from information_schema.tables where table_schema='%s'""" % (conp[4])
    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df["table_name"].values

    if "gg_html" in arr:
        html_cdc(conp, f, headless=headless)
    else:
        html_work(conp, f, headless=headless)


def est_tables(conp, data, headless=True):
    data = data.copy()
    for w in data:
        setting = {
            "url": w[1],
            "f1": w[3],
            "f2": w[4],
            "tb": w[0],
            "col": w[2],
            "conp": conp,
            "num": 10,
            "headless": headless
        }
        m = web()
        m.write(**setting)


#########y优化一些接口
def est_tbs(conp, data, **args):
    data = data.copy()

    sql = """select table_name from information_schema.tables where table_schema='%s'""" % (conp[4])
    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df["table_name"].values

    sql2 = """
    select table_name from information_schema.tables where table_schema='%s' and table_name ~'^[^t].*gg$' order by table_name desc limit 1
    """ % conp[4]

    df2 = db_query(sql2, conp=conp, dbtype="postgresql")

    if df2['table_name'].tolist() != []:
        latest_gg_table_name_g = df2['table_name'].tolist()[0]
    else:
        latest_gg_table_name_g = 'quanguoxiangmu_2002_01_01_2003_01_01_gg'

    old_year, old_month = re.findall('quanguoxiangmu\_(\d+)\_(\d+)\_\d+\_\d+\_\d+\_\d+\_gg', latest_gg_table_name_g)[0]

    now_year, now_month = datetime.strftime(datetime.now(), '%Y'), datetime.strftime(datetime.now(), '%m')

    if int(old_year) >= 2016:
        count = (int(now_year) - int(old_year)) * 12 + (int(now_month) - int(old_month))
    else:
        count = (2016 - int(old_year)) + (int(now_year) - 2016) * 12 + (int(now_month) - int(old_month))

    if count == 0: count = 1

    sql = '''create table if not exists %s.page_tb (time_period text unique not null,page_left text)''' % conp[-1]
    db_command(sql, dbtype='postgresql', conp=conp)

    for w in data:

        sql3 = """select time_period from %s.page_tb """ % conp[4]
        time_period_tmp = db_query(sql3, dbtype='postgresql', conp=conp)

        if w[0] not in time_period_tmp['time_period'].tolist():
            sql1 = """insert into %s.page_tb (time_period) values ('%s')""" % (conp[-1], w[0])
            # print(sql1)
            db_command(sql1, dbtype='postgresql', conp=conp)

    for w in data[-count:]:

        old_year, old_month = re.findall('quanguoxiangmu\_(\d+)\_(\d+)\_\d+\_\d+\_\d+\_\d+\_gg', w[0])[0]
        now_year, now_month = datetime.strftime(datetime.now(), '%Y'), datetime.strftime(datetime.now(), '%m')
        if int(old_year) >= 2016:
            count = (int(now_year) - int(old_year)) * 12 + (int(now_month) - int(old_month))
        else:
            count = (2016 - int(old_year)) + (int(now_year) - 2016) * 12 + (int(now_month) - int(old_month))

        if count == 0:
            current_month = True
        else:
            current_month = False

        m = web()
        setting = {
            "url": w[1],
            "f1": w[3],
            "f2": w[4],
            "tb": w[0],
            "col": w[2],
            "conp": conp,
            "num": 10,
            "headless": True,
            "current_month": current_month,
            "cdc": False
        }
        if "num" in args.keys():
            setting["num"] = args["num"]
        if "total" in args.keys():
            setting["total"] = args["total"]
        if "headless" in args.keys():
            setting["headless"] = args["headless"]
        setting = {**setting, **args}
        m.write(**setting)


def est_gg(conp, **arg):
    if "diqu" in arg.keys():
        diqu = arg["diqu"]
    else:
        diqu = "未知"
    create_gg(conp)

    sql = """
    select table_name from information_schema.tables where table_schema='%s' and table_name ~'_gg$' order by table_name
    """ % conp[4]

    df = db_query(sql, conp=conp, dbtype="postgresql")
    data = df['table_name'].tolist()

    for tbname in data:
        insert_tb(tbname, diqu=diqu, conp=conp)
        print('%s 写入gg , 成功。' % tbname)
    print('所有_gg表写入gg成功。')

    gg_distinc(conp)


def est_work(conp, data, **arg):
    est_tbs(conp, data, **arg)
    est_gg(conp, **arg)


def est_cdc(conp, data, **args):
    '''
    '''
    data = data.copy()
    sql = """select table_name from information_schema.tables where table_schema='%s'""" % (conp[4])
    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df["table_name"].values

    # ctb_name = "quanguoxiangmu_"+datetime.strftime(datetime.now(),'%Y_%m_01')+'_'+datetime.strftime(datetime.now()+relativedelta(months=1),'%Y_%m_01')

    for w in data:

        old_year, old_month = re.findall('quanguoxiangmu\_(\d+)\_(\d+)\_\d+\_\d+\_\d+\_\d+\_gg', w[0])[0]
        now_year, now_month = datetime.strftime(datetime.now(), '%Y'), datetime.strftime(datetime.now(), '%m')
        if int(old_year) >= 2016:
            count = (int(now_year) - int(old_year)) * 12 + (int(now_month) - int(old_month))
        else:
            count = (2016 - int(old_year)) + (int(now_year) - 2016) * 12 + (int(now_month) - int(old_month))

        if count == 0:
            current_month = True
        else:
            current_month = False

        if w[0] not in arr:
            sql3 = """
            CREATE TABLE %s.%s (
            "name" varchar(160) COLLATE "default",
            "ggstart_time" varchar(80) COLLATE "default",
            "href" varchar(400) COLLATE "default",
            "xiangmu_code" varchar(80) COLLATE "default",
            "shenpishixiang" varchar(80) COLLATE "default",
            "shenpibumen" varchar(80) COLLATE "default",
            "status" varchar(80) COLLATE "default",
            "info" varchar(4000) COLLATE "default"
            )
            WITH (OIDS=FALSE)
            ;""" % (conp[4], w[0])
            db_command(sql3, dbtype='postgresql', conp=conp)
        m = web()

        setting = {
            "url": w[1],
            "f1": w[3],
            "f2": w[4],
            "tb": w[0] + '_cdc',
            "col": w[2],
            "conp": conp,
            "num": 10,
            "total": 100,
            "headless": True,
            "current_month": current_month,
            "cdc": True
        }
        if "num" in args.keys():
            setting["num"] = args["num"]
        if "cdc_total" in args.keys():
            setting["total"] = args["cdc_total"]

        setting = {**setting, **args}
        if "diqu" in args.keys():
            diqu = args["diqu"]
        else:
            diqu = "未知"

        flag = m.write(**setting)
        if flag:
            cdc_sql(conp, w[0])
    gg_cdc(conp, diqu)


def est_meta(conp, data, **arg):
    '''判断cdc还是全量'''
    sql = """select table_name from information_schema.tables where table_schema='%s'""" % (conp[4])
    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df["table_name"].values
    # ctb_name = "quanguoxiangmu_"+datetime.strftime(datetime.now(),'%Y_%m_01')+'_'+datetime.strftime(datetime.now()+relativedelta(months=1),'%Y_%m_01')

    if "gg" in arr:
        est_cdc(conp, data, **arg)

    else:
        est_work(conp, data, **arg)


def add_info(f, info):
    def wrap(*arg):
        df = f(*arg)
        if "info" not in df.columns:
            df[df.columns[-1]] = df[df.columns[-1]].map(
                lambda x: json.dumps({**(json.loads(x)), **(info)}, ensure_ascii=False) if x is not None else json.dumps(info, ensure_ascii=False))
        else:
            df["info"] = df["info"].map(
                lambda x: json.dumps({**(json.loads(x)), **(info)}, ensure_ascii=False) if x is not None else json.dumps(info, ensure_ascii=False))
        return df

    return wrap


def est_html_work(conp, f, **args):
    m = page()

    if "limit" in args.keys():
        limit = args['limit']
    else:
        limit = 1000
    if "turn" in args.keys():
        turn = args['turn']
    else:
        turn = 10

    print('page 总共爬取 %s 轮，每轮 %s 页' % (turn, limit))
    for i in range(turn):

        sql = "select href from %s.gg where href not in(select href from %s.gg_html ) limit %s " % (conp[4], conp[4], limit)

        df = db_query(sql, dbtype="postgresql", conp=conp)
        arr = df["href"].values

        print('第 %s 轮取 %s 条href数据进行page爬取。' % (i + 1, limit))

        if "html_total" in args.keys():
            html_total = args["html_total"]
            arr = arr[:html_total]
        print(arr[:3])
        setting = {"num": 20, "arr": arr, "f": f, "conp": conp, "tb": "gg_html", "headless": True}

        if "num" in args.keys():
            setting["num"] = args["num"]
        setting = {**setting, **args}
        m.write(**setting)


def est_html_cdc(conp, f, **args):
    m = page()

    if "limit" in args.keys():
        limit = args['limit']
    else:
        limit = 1000
    if "turn" in args.keys():
        turn = args['turn']
    else:
        turn = 10

    sql = "create table if not exists %s.gg_html(href text,page text,primary key(href))" % (conp[4])
    db_command(sql, dbtype='postgresql', conp=conp)
    print('如果 gg_html 表不存在，则创建。Page 爬取开始 共 %s 轮，每轮 %s 页' % (turn, limit))
    bg = time.time()

    for i in range(turn):

        sql = "select href from %s.gg where href not in(select href from %s.gg_html ) limit %s " % (conp[4], conp[4], limit)
        df = db_query(sql, dbtype="postgresql", conp=conp)
        print('第 %s 轮取 %s 条 href 数据进行 page 爬取。' % (i + 1, limit))

        arr = df["href"].values
        if arr == []:
            print("无href更新")
            return None
        if "html_total" in args.keys():
            html_total = args["html_total"]
            arr = arr[:html_total]

        setting = {"num": 5, "arr": arr, "f": f, "conp": conp, "tb": "gg_html", "headless": True}
        if "num" in args.keys():
            setting["num"] = args["num"]
        setting = {**setting, **args}
        if len(arr) > 2000 and setting['num'] < 20: setting["num"] = 20

        m.write(**setting)

    ed = time.time()
    cost = ed - bg
    if cost < 100:
        print(" %s 轮总耗时%d 秒" % (turn, cost))
    else:
        print(" %s 轮总耗时%.4f 分" % (turn, cost / 60))


def gg_existed(conp):
    sql = """select table_name from information_schema.tables where table_schema='%s'""" % (conp[4])
    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df["table_name"].values
    if "gg" in arr:
        return True
    else:
        return False
