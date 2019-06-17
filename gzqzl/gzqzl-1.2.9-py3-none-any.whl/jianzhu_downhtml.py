import pandas

import MySQLdb
import cx_Oracle
import pymssql
from sqlalchemy.dialects.postgresql import TEXT
from selenium import webdriver
import pandas as pd
import sys
import time
from sqlalchemy import create_engine, types
import psycopg2
import re
from bs4 import BeautifulSoup
from queue import Queue
from threading import Thread
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
import traceback
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import NoSuchElementException
from threading import Semaphore
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities



_pool={
    'mssql':[['DmyyReader','Sjbd*0708','10.204.168.114\MSSQLSERVER2','basedb','dbo']]

    ,

    'postgresql':[['postgres','since2015','localhost','sist','sist20180204']
    ]
    ,

    'oracle':[['lmf','since2015','localhost','ORCL']]

    ,
    'mysql':[['root','since2015','localhost','test']]
}


class page:
    def __init__(self):
        self.add_ip()
        self.headless = True
        self.pageloadstrategy = 'normal'
        self.pageloadtimeout = 20
        self.tmp_q = Queue()
        self.ip_q = Queue()

        self.sema = Semaphore(1)
        self.__init_localhost_q()

    def get_driver(self, ip=None):

        chrome_option = webdriver.ChromeOptions()
        if ip is not None: chrome_option.add_argument("--proxy-server=http://%s" % (ip))
        if self.headless:
            chrome_option.add_argument("--headless")
            chrome_option.add_argument("--no-sandbox")

        caps = DesiredCapabilities().CHROME
        caps["pageLoadStrategy"] = self.pageloadstrategy  # complete#caps["pageLoadStrategy"] = "eager" # interactive#caps["pageLoadStrategy"] = "none"
        args = {"desired_capabilities": caps, "chrome_options": chrome_option}

        driver = webdriver.Chrome(**args)
        driver.maximize_window()

        driver.set_page_load_timeout(self.pageloadtimeout)
        return driver

    def add_ip(self):
        try:
            i = 3
            r = requests.get("http://www.trackip.net/")
            txt = r.text
            ip = txt[txt.find('title') + 6:txt.find('/title') - 1]
            while re.match("[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}:[0-9]{1,5}", ip) is None:
                time.sleep(0.5)
                r = requests.get("http://www.trackip.net/")
                txt = r.text
                ip = txt[txt.find('title') + 6:txt.find('/title') - 1]
                i -= 1
                if i < 0: break

            i = 3
            while i > 0:
                x = """http://http.zhiliandaili.cn/Users-whiteIpListNew.html?appid=3105&appkey=982479357306065df6b3c2f47ec124fc"""
                r = requests.get(x).json()
                if "data" in r.keys():
                    ips = r["data"]
                    print(ips)
                    break
                    # print(ips)
                else:
                    time.sleep(1)
                    i -= 1
            if ips == None:
                return False
            if ip in ips:
                print("%s已经在白名单中" % ip)
                return True
            i = 3

            while i > 0:
                x = """http://http.zhiliandaili.cn/Users-whiteIpAddNew.html?appid=3105&appkey=982479357306065df6b3c2f47ec124fc&whiteip=%s""" % ip
                r = requests.get(x).json()
                print(r)
                if "存在" in r["msg"]:
                    print("ip已经在白名单中")
                    break
                if "最多数量" in r["msg"]:
                    time.sleep(1)
                    x = """http://http.zhiliandaili.cn/Users-whiteIpAddNew.html?appid=3105&appkey=982479357306065df6b3c2f47ec124fc&whiteip=%s&index=5""" % ip
                    r = requests.get(x).json()

                if "成功" in r["msg"]:
                    print("添加ip%s" % ip)
                    break
                i -= 1
                time.sleep(1)

        except:
            traceback.print_exc()

    def get_ip(self):
        self.sema.acquire()
        try:
            url = """http://ip.11jsq.com/index.php/api/entry?method=proxyServer.generate_api_url&packid=0&fa=0&fetch_key=&qty=1&time=1&pro=&city=&port=1&format=txt&ss=1&css=&dt=1&specialTxt=3&specialJson="""
            r = requests.get(url)
            time.sleep(1)
            self.ip_q.put(r.text)
            ip = r.text
        except:
            ip = "ip失败"
        finally:
            self.sema.release()
        return ip

    def __init_localhost_q(self, num=2):
        self.localhost_q = Queue()
        for i in range(num): self.localhost_q.put(i)

    def __init_tmp_q(self, arr):
        self.tmp_q.queue.clear()
        for i in arr:
            self.tmp_q.put(i)

    def __read_thread(self, f):
        conp = self.conp
        # if self.localhost_q.empty():
        if (conp[5] == "jianzhu_zcry_html") or (conp[5] == "jianzhu_gcxm_html"):
            try:
                proxies = {}
                print("使用本机ip")
                # self.localhost_q.get(block=False)
                driver=self.get_driver()
            except Exception as e:
                traceback.print_exc()
                driver.quit()
                return False
        else:
            ip = self.get_ip()
            # ip="1.28.0.90:20455"
            print("本次ip %s" % ip)
            if re.match("[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}:[0-9]{1,5}", ip) is None:
                print("ip不合法")
                return False
            try:
                driver = self.get_driver(ip)
                proxies = {
                    "http": "http://%s" % (ip), }
            except Exception as e:
                traceback.print_exc()
                driver.quit()
                return False

        while not self.tmp_q.empty():
            try:
                x = self.tmp_q.get(block=False)
            except:
                traceback.print_exc()
                continue
            if x is None: continue
            try:
                if proxies:df = f(driver, x, proxies)
                else:df = f(driver, x)
                self.db_write(conp, df)
                time.sleep(0.1)
                size = self.tmp_q.qsize()
                if size % 100 == 0: print("还剩 %d 页" % size)
            except Exception as e:
                traceback.print_exc()
                print("第 %s 页面异常" % x[0])
                msg = traceback.format_exc()
                if "违反" in msg: continue
                if "invalid URL" in msg: continue
                self.tmp_q.put(x)
                driver.quit()
                return False
        driver.quit()
        print("线程正常退出")
        return True

    def read_thread(self, f):
        num =total=100
        flag = self.__read_thread(f)
        while not flag and num > 0:
            num -= 1
            print("切换ip,本线程第%d次" % (total - num))
            print("已经消耗ip %d 个" % self.ip_q.qsize())
            flag = self.__read_thread(f)

    def read_threads(self, f, arr, num=20):
        bg = time.time()
        ths = []
        dfs = []
        # print(arr[:3])
        total = len(arr)
        if total <= 5: num = 1
        if total != 0:
            if num / total > 1:
                num = int(total / 5) + 1 if int(total / 5) + 1 < 4 else num

        print("本次共 %d 个页面,共%d 个线程" % (total, num))

        self.__init_tmp_q(arr)
        for _ in range(num):
            t = Thread(target=self.read_thread, args=(f,))
            ths.append(t)
        for t in ths:
            t.start()
        for t in ths:
            t.join()
        self.__init_localhost_q()
        left_page = self.tmp_q.qsize()
        print("剩余 %d页" % (left_page))
        if left_page > 0:
            self.read_thread(f)
            left_page = self.tmp_q.qsize()
            print("剩余 %d页" % (left_page))
        ed = time.time()
        cost = ed - bg
        if cost < 100:
            print("耗时%d 秒" % cost)
        else:
            print("耗时%.4f 分" % (cost / 60))

    def db_write(self, conp, df):
        dbtype = "postgresql"
        if dbtype == 'postgresql':
            con = psycopg2.connect(user=conp[0], password=conp[1], host=conp[2], port="5432", database=conp[3])
        elif dbtype == 'mssql':
            con = pymssql.connect(user=conp[0], password=conp[1], host=conp[2], database=conp[3])
        elif dbtype == 'oracle':
            con = cx_Oracle.connect("%s/%s@%s/%s" % (conp[0], conp[1], conp[2], conp[3]))
        else:
            con = MySQLdb.connect(user=conp[0], passwd=conp[1], host=conp[2], db=conp[3])
        # if int(df[0]) == 1:
        #     sql = """insert into %s.%s values($lmf$%s$lmf$,$lmf$%s$lmf$,$lmf$%s$lmf$)""" % (conp[4], conp[5], df[1], df[2], df[3])
        # elif int(df[0]) == 2:
        #     sql = """update %s.%s set zcry=$lmf$%s$lmf$ where href='%s'""" % (conp[4], conp[5], df[1], df[2])
        # elif int(df[0]) >= 3:
        #     sql = """update %s.%s set gcxm=$lmf$%s$lmf$,blxw=$lmf$%s$lmf$,lhxw=$lmf$%s$lmf$,
        #     hmdjl=$lmf$%s$lmf$,sxlhcjjl=$lmf$%s$lmf$,bgjl=$lmf$%s$lmf$ where href='%s'
        #     """ % (conp[4], conp[5], df[1], df[2], df[3], df[4], df[5], df[6], df[7])
        if conp[5] == 'jianzhu_gg_html':
            if df == 0:
                print("数据为空,任务结束")
                return False
            sql = """insert into %s.%s (href,page,qyzzzg,zcry,gcxm,blxw,lhxw,hmdjl,sxlhcjjl,bgjl) values ($lmf$%s$lmf$,$lmf$%s$lmf$,$lmf$%s$lmf$,$lmf$%s$lmf$,$lmf$%s$lmf$,$lmf$%s$lmf$,$lmf$%s$lmf$,$lmf$%s$lmf$,$lmf$%s$lmf$,$lmf$%s$lmf$)
            """ % (conp[4], conp[5], df[0], df[1], df[2], df[3], df[4], df[5], df[6], df[7], df[8], df[9])
            cur = con.cursor()
            cur.execute(sql)
            con.commit()
            cur.close()
            con.close()

        elif isinstance(df, pd.DataFrame):
            if df.empty:
                # print("数据为空,任务结束")
                return False
            col = self.col
            tb = conp[5]
            if len(df) >= 1:
                # print(df)
                df.columns = col
            else:
                df = pd.DataFrame(columns=col)
                print("暂无数据")
            # print("将数据df 写入 %s" % tb)
            self.ryxx_db_write(df, tb, dbtype=dbtype, conp=conp,datadict='postgresql-text')
            # print("df写入%s完毕" % tb)
            # sql = """insert into %s.%s values($lmf$%s$lmf$,$lmf$%s$lmf$,$lmf$%s$lmf$,$lmf$%s$lmf$,$lmf$%s$lmf$,$lmf$%s$lmf$,$lmf$%s$lmf$,
            # $lmf$%s$lmf$,$lmf$%s$lmf$,$lmf$%s$lmf$,$lmf$%s$lmf$)""" % (conp[4],conp[5],df[1],df[2],df[3],df[4],df[5],df[6],df[7],df[8],df[9],df[10],df[11])


    def ryxx_db_write(self, df, tb_name, dbtype='mssql', pool=0, conp=None, datadict=None, if_exists='append'):
        """ conp[4] 影响表写入的schema"""
        if conp is None: conp = _pool[dbtype][pool]
        if dbtype == 'mssql':
            con = create_engine("mssql+pymssql://%s:%s@%s/%s" % (conp[0], conp[1], conp[2], conp[3]), encoding='utf-8')
        elif dbtype == 'postgresql':
            con = create_engine("postgresql://%s:%s@%s/%s" % (conp[0], conp[1], conp[2], conp[3]), encoding='utf-8')
        elif dbtype == 'oracle':
            con = create_engine('oracle://%s:%s@%s/%s' % (conp[0], conp[1], conp[2], conp[3]), encoding='utf-8')
        elif dbtype == 'sqlite':
            con = create_engine('sqlite:///%s' % conp)

        else:
            con = create_engine('mysql://%s:%s@%s/%s?charset=utf8' % (conp[0], conp[1], conp[2], conp[3]), encoding='utf-8')
        def sqlcol(dfparam, text=None):
            dtypedict = {}
            for i, j in zip(dfparam.columns, dfparam.dtypes):

                if "object" in str(j):
                    if text == "postgresql-text":
                        dtypedict.update({i: TEXT()})
                    else:
                        try:
                            x = int(df[i].str.len().max() / 40) + 1
                        except:
                            x = 50
                        dtypedict.update({i: types.VARCHAR(length=x * 80)})

                if "datetime" in str(j):
                    dtypedict.update({i: types.DateTime()})

                if "float" in str(j):
                    dtypedict.update({i: types.Float(precision=3, asdecimal=True)})

                if "int" in str(j):
                    dtypedict.update({i: types.INT()})

            return dtypedict

        if datadict is None: datadict = sqlcol(df)
        if datadict == 'postgresql-text': datadict = sqlcol(df, 'postgresql-text')
        if dbtype == 'sqlite':
            df.to_sql(tb_name, con, if_exists=if_exists, index=False, dtype=datadict)
        else:
            df.to_sql(tb_name, con, if_exists=if_exists, index=False, schema=conp[4], dtype=datadict)


    def db_write_many(self, conp, data):

        dbtype = "postgresql"
        if dbtype == 'postgresql':
            con = psycopg2.connect(user=conp[0], password=conp[1], host=conp[2], port="5432", database=conp[3])
        elif dbtype == 'mssql':
            con = pymssql.connect(user=conp[0], password=conp[1], host=conp[2], database=conp[3])
        elif dbtype == 'oracle':
            con = cx_Oracle.connect("%s/%s@%s/%s" % (conp[0], conp[1], conp[2], conp[3]))
        else:
            con = MySQLdb.connect(user=conp[0], passwd=conp[1], host=conp[2], db=conp[3])
        sql = """insert into %s.%s values(href,page)""" % (conp[4], conp[5])
        cur = con.cursor()
        cur.executemany(sql, data)
        con.commit()
        cur.close()
        con.close()

    def db_command(self, sql, conp):

        """db_command 仅仅到数据库"""
        dbtype = "postgresql"
        if dbtype == 'postgresql':
            con = psycopg2.connect(user=conp[0], password=conp[1], host=conp[2], port="5432", database=conp[3])
        elif dbtype == 'mssql':
            con = pymssql.connect(user=conp[0], password=conp[1], host=conp[2], database=conp[3])
        elif dbtype == 'oracle':
            con = cx_Oracle.connect("%s/%s@%s/%s" % (conp[0], conp[1], conp[2], conp[3]))
        else:
            con = MySQLdb.connect(user=conp[0], passwd=conp[1], host=conp[2], db=conp[3])
        cur = con.cursor()
        cur.execute(sql)
        con.commit()
        cur.close()
        con.close()

    def write(self, **arg):
        tb = arg['tb']
        conp = arg["conp"]

        f = arg["f"]
        num = arg["num"]
        arr = arg["arr"]
        col = arg["col"]
        if "headless" not in arg.keys():
            self.headless = True
        else:
            self.headless = arg["headless"]

        if "pageloadstrategy" not in arg.keys():
            self.pageloadstrategy = "normal"
        else:
            self.pageloadstrategy = arg["pageloadstrategy"]

        if "pageloadtimeout" not in arg.keys():
            self.pageloadtimeout = 20
        else:
            self.pageloadtimeout = arg["pageloadtimeout"]

        if tb == "jianzhu_gcxm_html":
            sql = """create table if not exists %s.%s(href text,gcxm text,xmxx_name text,
            xmxx_href text,xm_id text,xm_diqu text,xm_type text,qy_name text)""" % (conp[4], tb)

        elif tb == "jianzhu_xmxx_html":
            sql = """create table if not exists %s.%s(href text,xmxx_name text,
            xmxx_href text,xmxx_page text)""" % (conp[4], tb)

        elif tb == "jianzhu_zcry_html":
            sql = """create table if not exists %s.%s(href text,zcry text,ryxx_name text,
            ryxx_href text,id_number text,zclb text,zch text,zczy text)""" % (conp[4], tb)

        elif tb == 'jianzhu_ryxx_html':
            sql = """create table if not exists %s.%s(href text,ryxx_href text,ryxx_name text,sex text,id_type text,id_number text,zyzcxx text,grgcyj text,
                        blxw text,lhxw text,hmdjl text,bgjl text)""" % (conp[4], tb)

        elif tb == 'jianzhu_gg_html':
            sql = """create table if not exists %s.%s(href text,page text,qyzzzg text,zcry text,gcxm text,blxw text,
            lhxw text,hmdjl text,sxlhcjjl text,bgjl text,primary key(href))""" % (conp[4], tb)

        self.db_command(sql, conp)
        print("创建表if不存在")
        conp.append(tb)
        print(conp)
        self.col = col
        self.conp = conp
        self.read_threads(f=f, num=num, arr=arr)
        return self.tmp_q.qsize()



