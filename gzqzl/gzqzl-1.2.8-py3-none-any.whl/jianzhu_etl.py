import json

from gzqzl import web,page

# 表名解析器

# tb="gcjs_jiaotong_zhongbiaohx_gg"
from gzqzl.jianzhu_dbv2 import db_command, db_query


def create_gg(conp):
    sql1="""
    drop table if exists %s.gg;
    create table if not exists %s.gg
    (
    td text,
    name text,
    href text,
    person text,
    place  text,
    info  text
    )
    """%(conp[4],conp[4])
    db_command(sql1,dbtype="postgresql",conp=conp)


def insert_tb(tbname, diqu, conp):
    schema = conp[4]

    sql2 = """
    insert into %s.gg
    select td,name,href,person,
    place,info from %s.%s
    """ % (schema, schema, tbname)

    db_command(sql2, dbtype="postgresql", conp=conp)



def removal_data(conp):
    schema = conp[4]
    sql3 = """
        delete from %s.gg where ctid in (
        select ctid from
        (select row_number() over(partition by (name,href) order by ctid) as rn,ctid from %s.gg )as t where t.rn<>1)
    """% (schema, schema)

    db_command(sql3, dbtype="postgresql", conp=conp)


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

    removal_data(conp=conp)


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

    removal_data(conp=conp)

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

    if "gg" in arr:
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
 where  href in (select distinct href from weihai.gg where href not exists(select href from weihai.gg_html ) 


and (not coalesce(info,'{}')::jsonb?'hreftype' or coalesce(info,'{}')::jsonb->>'hreftype'='可抓网页'))

"""


def html_cdc(conp, f, headless=True):
    m = page()
    sql = "select distinct href from %s.gg where href not exists(select href from %s.gg_html ) and (not coalesce(info,'{}')::jsonb?'hreftype' or coalesce(info,'{}')::jsonb->>'hreftype'='可抓网页')" % (
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
    for w in data:
        m = web()
        setting = {
            "url": w[1],
            "f1": w[3],
            "f2": w[4],
            "tb": w[0],
            "col": w[2],
            "conp": conp,
            "num": 10,
            "headless": True
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


def est_work(conp, data, **arg):
    est_tbs(conp, data, **arg)
    est_gg(conp, **arg)


def est_cdc(conp, data, **args):
    data = data.copy()

    for w in data:
        m = web()

        setting = {
            "url": w[1],
            "f1": w[3],
            "f2": w[4],
            "tb": w[0] + "_cdc",
            "col": w[2],
            "conp": conp,
            "num": 4,
            "total": 10,
            "headless": True
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

        m.write(**setting)
        cdc_sql(conp, w[0])
    gg_cdc(conp, diqu)


def jianzhu_est_meta(conp, data, **arg):
    sql = """select table_name from information_schema.tables where table_schema='%s'""" % (conp[4])
    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df["table_name"].values

    if "gg" in arr:
        est_cdc(conp, data, **arg)
    else:
        est_work(conp, data, **arg)


def add_info(f,info):
    def wrap(*arg):
        df=f(*arg)
        if "info" not in df.columns:
            df[df.columns[-1]]=df[df.columns[-1]].map(lambda x:json.dumps({**(json.loads(x)),**(info)},ensure_ascii=False) if x is not None else json.dumps(info,ensure_ascii=False)  )
        else:
            df["info"]=df["info"].map(lambda x:json.dumps({**(json.loads(x)),**(info)},ensure_ascii=False) if x is not None else json.dumps(info,ensure_ascii=False)  )
        return df
    return wrap



# -----------------------------------------------------------------获取企业信息---------------------------------------------------------------------------------------------------

def est_html_work(conp, f,data, **args):
    if "size" in args.keys():
        size = args["size"]
    else:
        size = None

    m = page()
    if size is not None:
        sql = "select href,page from %s.gg_html limit %d" % (conp[4], size)
    else:
        sql = "select href,page from %s.gg_html" % (conp[4])

    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df.values
    if "html_total" in args.keys():
        html_total = args["html_total"]
        arr = arr[:html_total]
    print(arr[:3])
    setting = {"num": 20, "arr": arr, "f": f, "conp": conp, "tb": "jianzhu_gg_html", "col":data,"headless": True}

    if "num" in args.keys():
        setting["num"] = args["num"]
    setting = {**setting, **args}
    m.write(**setting)


def est_html_cdc(conp, f, data,**args):
    m = page()

    if "ft" in args.keys():
        ft = args["ft"]
    else:
        ft = None

    if (ft == None) or (ft == 'f4'):
        sql = """select href,page from %s.gg_html as a where not exists(select 1 from %s.jianzhu_gg_html as b where
         a.href=b.href and (qyzzzg,zcry,gcxm,blxw,lhxw,hmdjl,sxlhcjjl,bgjl) is not null)""" % (conp[4], conp[4])
    else:return False

    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df.values
    if arr == []:
        print("无href更新")
        return None
    if "html_total" in args.keys():
        html_total = args["html_total"]
        arr = arr[:html_total]

    setting = {"num": 5, "arr": arr, "f": f, "conp": conp, "tb": "jianzhu_gg_html", "col":data,"headless": True}
    if len(arr) > 2000 and setting['num'] < 20: setting["num"] = 20
    if "num" in args.keys():
        setting["num"] = args["num"]
    setting = {**setting, **args}

    m.write(**setting)


# 获取企业信息入口
def jianzhu_est_html(conp, f, data, **args):
    sql = """select table_name from information_schema.tables where table_schema='%s'""" % (conp[4])
    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df["table_name"].values

    if "jianzhu_gg_html" in arr:
        est_html_cdc(conp, f, data, **args)
        removal_html_data(conp)
    else:
        est_html_work(conp, f, data, **args)
        removal_html_data(conp)


def gg_existed(conp):
    sql = """select table_name from information_schema.tables where table_schema='%s'""" % (conp[4])
    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df["table_name"].values
    if "gg" in arr:
        return True
    else:
        return False

# 对jianzhu_gg_html数据去重
def removal_html_data(conp):
    schema = conp[4]
    sql3 = """
        delete from %s.jianzhu_gg_html where ctid in (
        select ctid from
        (select row_number() over(partition by href order by ctid) as rn,ctid from %s.jianzhu_gg_html )as t where t.rn<>1)
    """% (schema, schema)

    db_command(sql3, dbtype="postgresql", conp=conp)



# ----------------------------------------------------------获取人员信息-----------------------------------------------------------------------


# 获取人员信息入口
def jianzhu_ryxx_est_html(conp, f, data, **args):
    sql = """select table_name from information_schema.tables where table_schema='%s'""" % (conp[4])
    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df["table_name"].values

    if "jianzhu_ryxx_html" in arr:
        ryxx_html_cdc(conp, f, data, **args)
        # removal_ryxx_html_data(conp)
    else:
        ryxx_html_work(conp, f, data, **args)
        # removal_ryxx_html_data(conp)




def ryxx_html_work(conp, f, data, **args):
    if "flag" in args.keys():
        flag = args["flag"]
    else:flag=None
    if "size" in args.keys():
        size = args["size"]
    else:
        size = None
    m = page()
    if flag:
        sql = """SELECT distinct href,ryxx_href FROM "%s"."jianzhu_zcry_html" where (right(ryxx_href,1)::int)%%%%5=%d""" % (conp[4], flag)
    elif size is not None:
        sql = "select distinct href,ryxx_href from %s.jianzhu_zcry_html limit %d" % (conp[4], size)
    else:
        sql = "select distinct href,ryxx_href from %s.jianzhu_zcry_html" % (conp[4])

    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df.values
    if "html_total" in args.keys():
        html_total = args["html_total"]
        arr = arr[:html_total]
    print(arr[:3])
    setting = {"num": 20, "arr": arr, "f": f, "conp": conp, "tb": "jianzhu_ryxx_html", "col":data, "headless": True}

    if "num" in args.keys():
        setting["num"] = args["num"]
    setting = {**setting, **args}
    m.write(**setting)



def ryxx_html_cdc(conp, f, data, **args):
    if "flag" in args.keys():
        flag = args["flag"]
    else:flag=None
    m = page()
    if "ft" in args.keys():
        ft = args["ft"]
    else:ft = None
    if flag:
        sql = """SELECT distinct href,ryxx_href FROM "%s"."jianzhu_zcry_html" as b where not exists(select 1 from "%s"."jianzhu_ryxx_html" as a where a.ryxx_href=b.ryxx_href ) and (right(ryxx_href,1)::int)%%%%5=%d""" % (conp[4], conp[4],flag)
    else:
        sql = """select distinct href,ryxx_href from %s.jianzhu_zcry_html as a where not exists(select 1 from %s.jianzhu_ryxx_html as b where
         a.ryxx_href=b.ryxx_href and (ryxx_href,ryxx_name,sex,id_type,id_number,zyzcxx,grgcyj,blxw,lhxw,hmdjl,bgjl) is not null)""" % (conp[4], conp[4])

    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df.values
    if arr == []:
        print("无href更新")
        return None
    if "html_total" in args.keys():
        html_total = args["html_total"]
        arr = arr[:html_total]

    setting = {"num": 5, "arr": arr, "f": f, "conp": conp, "tb": "jianzhu_ryxx_html", "col":data, "headless": True}
    if len(arr) > 2000 and setting['num'] < 20: setting["num"] = 20
    if "num" in args.keys():
        setting["num"] = args["num"]
    setting = {**setting, **args}
    m.write(**setting)


# 对jianzhu_ryxx_html数据去重
def removal_ryxx_html_data(conp):
    schema = conp[4]
    sql3 = """
        delete from %s.jianzhu_ryxx_html where ctid in (
        select ctid from
        (select row_number() over(partition by href,ryxx_href,ryxx_name,id_number order by ctid) as rn,ctid from %s.jianzhu_ryxx_html)as t where t.rn<>1)
    """% (schema, schema)
    db_command(sql3, dbtype="postgresql", conp=conp)



# ----------------------------------------------------------获取注册人员信息-----------------------------------------------------------------------


# 获取注册人员信息入口
def jianzhu_zcry_est_html(conp, f, data, **args):
    sql = """select table_name from information_schema.tables where table_schema='%s'""" % (conp[4])
    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df["table_name"].values

    if "jianzhu_zcry_html" in arr:
        zcry_html_cdc(conp, f, data, **args)
        # removal_zcry_html_data(conp)
    else:
        zcry_html_work(conp, f, data, **args)
        # removal_zcry_html_data(conp)




def zcry_html_work(conp, f, data, **args):
    if "size" in args.keys():
        size = args["size"]
    else:
        size = None
    m = page()
    if size is not None:
        sql = "select href,zcry from %s.jianzhu_gg_html where zcry != '暂未查询到已登记入库信息' and zcry != 'None' limit %d" % (
        conp[4], size)
    else:
        sql = "select href,zcry from %s.jianzhu_gg_html where zcry != '暂未查询到已登记入库信息' and zcry != 'None'" % (conp[4])
    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df.values
    if "html_total" in args.keys():
        html_total = args["html_total"]
        arr = arr[:html_total]
    print(arr[:3])

    setting = {"num": 20, "arr": arr, "f": f, "conp": conp, "tb": "jianzhu_zcry_html", "col":data, "headless": True}

    if "num" in args.keys():
        setting["num"] = args["num"]
    setting = {**setting, **args}
    m.write(**setting)



def zcry_html_cdc(conp, f, data, **args):
    m = page()
    if "ft" in args.keys():
        ft = args["ft"]
    else:
        ft = None
    if ft == None:
        sql = """select href,zcry from %s.jianzhu_gg_html as a where a.zcry != '暂未查询到已登记入库信息' and a.zcry != 'None'
                        and not exists(select 1 from %s.jianzhu_zcry_html as b where
         a.href=b.href and (ryxx_name, ryxx_href, id_number, zclb, zch, zczy) is not null)""" % (conp[4], conp[4])
    else:return False
    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df.values
    if arr == []:
        print("无href更新")
        return None
    if "html_total" in args.keys():
        html_total = args["html_total"]
        arr = arr[:html_total]

    setting = {"num": 5, "arr": arr, "f": f, "conp": conp, "tb": "jianzhu_zcry_html", "col":data, "headless": True}
    if len(arr) > 2000 and setting['num'] < 20: setting["num"] = 20
    if "num" in args.keys():
        setting["num"] = args["num"]
    setting = {**setting, **args}
    m.write(**setting)


# 对jianzhu_zcry_html数据去重
def removal_zcry_html_data(conp):
    schema = conp[4]
    sql3 = """
        delete from %s.jianzhu_zcry_html where ctid in (
        select ctid from
        (select row_number() over(partition by href,ryxx_href,ryxx_name,id_number,zclb,zch,zczy order by ctid) as rn,ctid from %s.jianzhu_zcry_html)as t where t.rn<>1)
    """% (schema, schema)
    db_command(sql3, dbtype="postgresql", conp=conp)



# ----------------------------------------------------------获取工程项目基本信息-----------------------------------------------------------------------


# 获取工程项目基本信息入口
def jianzhu_gcxm_est_html(conp, f, data, **args):
    sql = """select table_name from information_schema.tables where table_schema='%s'""" % (conp[4])
    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df["table_name"].values

    if "jianzhu_gcxm_html" in arr:
        gcxm_html_cdc(conp, f, data, **args)
        # removal_gcxm_html_data(conp)
    else:
        gcxm_html_work(conp, f, data, **args)
        # removal_gcxm_html_data(conp)


def gcxm_html_work(conp, f, data, **args):
    if "size" in args.keys():
        size = args["size"]
    else:
        size = None

    m = page()
    if size is not None:
        sql = "select href,gcxm from %s.jianzhu_gg_html where gcxm != '暂未查询到已登记入库信息' and gcxm != 'None' limit %d" % (
        conp[4], size)
    else:
        sql = "select href,gcxm from %s.jianzhu_gg_html where gcxm != '暂未查询到已登记入库信息' and gcxm != 'None'" % (conp[4])

    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df.values
    if "html_total" in args.keys():
        html_total = args["html_total"]
        arr = arr[:html_total]
    print(arr[:3])
    setting = {"num": 20, "arr": arr, "f": f, "conp": conp, "tb": "jianzhu_gcxm_html", "col":data, "headless": True}

    if "num" in args.keys():
        setting["num"] = args["num"]
    setting = {**setting, **args}
    m.write(**setting)



def gcxm_html_cdc(conp, f, data, **args):
    m = page()
    if "ft" in args.keys():
        ft = args["ft"]
    else:
        ft = None
    if ft == None:
        sql = """select href,gcxm from %s.jianzhu_gg_html as a where a.gcxm != '暂未查询到已登记入库信息' and a.gcxm != 'None'
                    and not exists(select 1 from %s.jianzhu_gcxm_html as b where
         a.href=b.href and (xmxx_name, xmxx_href, xm_id,xm_diqu, xm_type, qy_name) is not null)""" % (conp[4], conp[4])
    else:return False
    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df.values
    if arr == []:
        print("无href更新")
        return None
    if "html_total" in args.keys():
        html_total = args["html_total"]
        arr = arr[:html_total]

    setting = {"num": 5, "arr": arr, "f": f, "conp": conp, "tb": "jianzhu_gcxm_html", "col":data, "headless": True}
    if len(arr) > 2000 and setting['num'] < 20: setting["num"] = 20
    if "num" in args.keys():
        setting["num"] = args["num"]
    setting = {**setting, **args}
    m.write(**setting)


# 对jianzhu_gcxm_html数据去重
def removal_gcxm_html_data(conp):
    schema = conp[4]
    sql3 = """
        delete from %s.jianzhu_gcxm_html where ctid in (
        select ctid from
        (select row_number() over(partition by href,xmxx_name,xmxx_href,xm_diqu,xm_type,qy_name order by ctid) as rn,ctid from %s.jianzhu_gcxm_html)as t where t.rn<>1)
    """% (schema, schema)
    db_command(sql3, dbtype="postgresql", conp=conp)



# ----------------------------------------------------------获取项目信息-----------------------------------------------------------------------


# 获取项目信息入口
def jianzhu_xmxx_est_html(conp, f, data, **args):
    sql = """select table_name from information_schema.tables where table_schema='%s'""" % (conp[4])
    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df["table_name"].values

    if "jianzhu_xmxx_html" in arr:
        xmxx_html_cdc(conp, f, data, **args)
        # removal_xmxx_html_data(conp)
    else:
        xmxx_html_work(conp, f, data, **args)
        # removal_xmxx_html_data(conp)




def xmxx_html_work(conp, f, data, **args):
    if "flag" in args.keys():
        flag = args["flag"]
    else:flag=None
    if "size" in args.keys():
        size = args["size"]
    else:
        size = None
    m = page()
    if flag:
        flag = int(flag)
        if flag == 0:
            sql = """SELECT distinct href,xmxx_href FROM "%s"."jianzhu_gcxm_html" where right(xmxx_href,1) in ('0','5')""" % (conp[4])
        elif flag == 1:
            sql = """SELECT distinct href,xmxx_href FROM "%s"."jianzhu_gcxm_html" where right(xmxx_href,1) in ('1','6')""" % (conp[4])
        elif flag == 2:
            sql = """SELECT distinct href,xmxx_href FROM "%s"."jianzhu_gcxm_html" where right(xmxx_href,1) in ('2','7')""" % (conp[4])
        elif flag == 3:
            sql = """SELECT distinct href,xmxx_href FROM "%s"."jianzhu_gcxm_html" where right(xmxx_href,1) in ('3','8')""" % (conp[4])
        elif flag == 4:
            sql = """SELECT distinct href,xmxx_href FROM "%s"."jianzhu_gcxm_html" where right(xmxx_href,1) in ('4','9')""" % (conp[4])

    elif size is not None:
        sql = "select distinct href,xmxx_href from %s.jianzhu_gcxm_html limit %d" % (conp[4], size)
    else:
        sql = "select distinct href,xmxx_href from %s.jianzhu_gcxm_html" % (conp[4])

    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df.values
    if "html_total" in args.keys():
        html_total = args["html_total"]
        arr = arr[:html_total]
    print(arr[:3])
    setting = {"num": 20, "arr": arr, "f": f, "conp": conp, "tb": "jianzhu_xmxx_html", "col":data, "headless": True}

    if "num" in args.keys():
        setting["num"] = args["num"]
    setting = {**setting, **args}
    m.write(**setting)



def xmxx_html_cdc(conp, f, data, **args):
    if "flag" in args.keys():
        flag = args["flag"]
    else:flag=None
    m = page()
    if "ft" in args.keys():
        ft = args["ft"]
    else:ft = None
    if flag:
        flag = int(flag)
        if flag == 0:
            sql = """SELECT distinct href,xmxx_href FROM "%s"."jianzhu_gcxm_html" as b where not exists(select 1 from "%s"."jianzhu_xmxx_html" as a where a.xmxx_href=b.xmxx_href ) and right(xmxx_href,1) in ('0','5')""" % (conp[4], conp[4])
        elif flag == 1:
            sql = """SELECT distinct href,xmxx_href FROM "%s"."jianzhu_gcxm_html" as b where not exists(select 1 from "%s"."jianzhu_xmxx_html" as a where a.xmxx_href=b.xmxx_href ) and right(xmxx_href,1) in ('1','6')""" % (
            conp[4], conp[4])
        elif flag == 2:
            sql = """SELECT distinct href,xmxx_href FROM "%s"."jianzhu_gcxm_html" as b where not exists(select 1 from "%s"."jianzhu_xmxx_html" as a where a.xmxx_href=b.xmxx_href ) and right(xmxx_href,1) in ('2','7')""" % (
            conp[4], conp[4])
        elif flag == 3:
            sql = """SELECT distinct href,xmxx_href FROM "%s"."jianzhu_gcxm_html" as b where not exists(select 1 from "%s"."jianzhu_xmxx_html" as a where a.xmxx_href=b.xmxx_href ) and right(xmxx_href,1) in ('3','8')""" % (
            conp[4], conp[4])
        elif flag == 4:
            sql = """SELECT distinct href,xmxx_href FROM "%s"."jianzhu_gcxm_html" as b where not exists(select 1 from "%s"."jianzhu_xmxx_html" as a where a.xmxx_href=b.xmxx_href ) and right(xmxx_href,1) in ('4','9')""" % (
            conp[4], conp[4])
    else:
        sql = """select distinct href,xmxx_href from %s.jianzhu_gcxm_html as a where not exists(select 1 from %s.jianzhu_xmxx_html as b where
         a.xmxx_href=b.xmxx_href and (href,xmxx_name,xmxx_href,xmxx_page) is not null)""" % (conp[4], conp[4])

    df = db_query(sql, dbtype="postgresql", conp=conp)
    arr = df.values
    if arr == []:
        print("无href更新")
        return None
    if "html_total" in args.keys():
        html_total = args["html_total"]
        arr = arr[:html_total]

    setting = {"num": 5, "arr": arr, "f": f, "conp": conp, "tb": "jianzhu_xmxx_html", "col":data, "headless": True}

    if len(arr) > 2000 and setting['num'] < 20: setting["num"] = 20
    if "num" in args.keys():
        setting["num"] = args["num"]
    setting = {**setting, **args}
    m.write(**setting)


# 对jianzhu_xmxx_html数据去重
def removal_xmxx_html_data(conp):
    schema = conp[4]
    sql3 = """
        delete from %s.jianzhu_xmxx_html where ctid in (
        select ctid from
        (select row_number() over(partition by href,xmxx_name, xmxx_href order by ctid) as rn,ctid from %s.jianzhu_xmxx_html)as t where t.rn<>1)
    """% (schema, schema)
    db_command(sql3, dbtype="postgresql", conp=conp)