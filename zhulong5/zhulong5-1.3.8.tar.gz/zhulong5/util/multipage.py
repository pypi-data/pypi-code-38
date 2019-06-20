from selenium import webdriver
import pandas as pd
import sys
import time
from sqlalchemy import create_engine, types
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
from lmf.dbv2 import db_write, db_query, db_command
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class web:

    def __init__(self):

        self.add_ip()
        self.headless = True
        self.headless = True
        self.pageloadstrategy = 'normal'
        self.pageloadtimeout = 40
        self.url = "http://www.jy.whzbtb.com/V2PRTS/TendererNoticeInfoListInit.do"
        self.result_q = Queue()
        self.tmp_q = Queue()
        self.ip_q = Queue()
        self.__init_tmp_q(10)
        self.sema = Semaphore(1)
        # 本地ip数量设置
        self.__init_localhost_q(num=0)

    def get_driver(self, ip=None):

        chrome_option = webdriver.ChromeOptions()
        if ip is not None: chrome_option.add_argument("--proxy-server=http://%s" % (ip))
        if self.headless:
            chrome_option.add_argument("--headless")
            chrome_option.add_argument("--no-sandbox")

        caps = DesiredCapabilities().CHROME
        caps[
            "pageLoadStrategy"] = self.pageloadstrategy  # complete#caps["pageLoadStrategy"] = "eager" # interactive#caps["pageLoadStrategy"] = "none"
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

    def __init_total(self, f2):
        """获取需要爬取的页面总量，先用本地ip爬三次，若失败代理ip爬三次"""
        num = 1
        m = 5

        while m > 0:
            try:

                ip = self.get_ip()
                # ip="1.28.0.90:20455"
                print("使用代理ip %s" % ip)
                driver = self.get_driver(ip)
                driver.get(self.url)
                self.total = f2(driver)
                print("全局共%d 页面" % self.total)
                return "sccess"
            except Exception as e:
                traceback.print_exc()
                driver.quit()
                m -= 1
                print("用代理ip获取总量,第%d失败" % (3 - m))
        while num > 0:
            try:
                driver = self.get_driver()
                driver.get(self.url)
                self.total = f2(driver)
                print("用本地ip获取总量,全局共%d 页面" % self.total)
                return "sccess"
            except Exception as e:
                traceback.print_exc()
                driver.quit()
                num -= 1
                print("用本地ip获取总量,第%d失败" % (num))
        return "failed"

    def __init_tmp_q(self, total):
        self.tmp_q.queue.clear()
        if type(total) != type([]):
            for i in range(total):
                self.tmp_q.put(i + 1)
        else:
            if total != ['']:
                for i in total:
                    self.tmp_q.put(i)

    def __read_thread(self, f):
        url = self.url
        if self.localhost_q.empty():

            ip = self.get_ip()
            # ip="1.28.0.90:20455"
            print("本次ip %s" % ip)
            if re.match("[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}:[0-9]{1,5}", ip) is None:
                print("ip不合法")
                return False

            try:

                driver = self.get_driver(ip)
                driver.get(url)


            except Exception as e:
                traceback.print_exc()

                driver.quit()
                return False
        else:
            try:
                print("使用本机ip")
                self.localhost_q.get(block=False)
                driver = self.get_driver()
                driver.get(url)
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
                df = f(driver, x)
                self.result_q.put(df)

            except Exception as e:
                traceback.print_exc()
                msg = traceback.format_exc()
                print("第 %d 页面异常" % x)
                if "违反" not in msg:
                    self.tmp_q.put(x)
                driver.quit()
                return False
        driver.quit()
        print("线程正常退出")
        return True

    def read_thread(self, f):
        num = 20
        flag = self.__read_thread(f)
        while not flag and num > 0:
            num -= 1
            print("切换ip,本线程第%d次" % (20 - num))
            print("已经消耗ip %d 个" % self.ip_q.qsize())
            flag = self.__read_thread(f)

    def read_threads(self, conp, tb, f, num=10, total=100):
        bg = time.time()
        ths = []
        dfs = []
        if total == 0:
            print("0页,线程不启动，任务结束")
            return False
        if total < 2: num = 1
        if num / total > 1: num = int(total / 5) + 1 if int(total / 5) + 1 < 4 else num
        if total / num < 10: num = int(total / 10) + 1

        print("开始爬%s,本次共 %d 个页面,共%d 个线程" % (self.url, total, num))
        self.result_q.queue.clear()
        self.__init_tmp_q(total)

        for _ in range(num):
            t = Thread(target=self.read_thread, args=(f,))
            ths.append(t)
        for t in ths:
            t.start()
        for t in ths:
            t.join()
        self.__init_localhost_q(num=3)
        left_page = self.tmp_q.qsize()
        print("剩余 %d 页" % (left_page))
        if left_page > 0:
            self.read_thread(f)
            left_page = self.tmp_q.qsize()

            sql = '''create table if not exists %s.page_tb (time_period text unique not null,page_left text)''' % conp[-1]
            db_command(sql, dbtype='postgresql', conp=conp)

            sql2 = '''update %s.page_tb set page_left ='%s' where time_period='%s' ''' % (conp[-1], list(self.tmp_q.queue), tb.split("_cdc")[0])
            db_command(sql2, dbtype='postgresql', conp=conp)


        else:

            sql2 = '''update %s.page_tb set page_left ='0' where time_period='%s' ''' % (conp[-1], tb.split("_cdc")[0])

            db_command(sql2, dbtype='postgresql', conp=conp)
        print("表 %s 剩余 %d 页, 已存入数据库 。" % (tb, left_page))
        ed = time.time()
        cost = ed - bg
        if cost < 100:
            print("耗时%d --秒" % cost)
        else:
            print("耗时%.4f 分" % (cost / 60))
        print("read_threads结束")

    def getdf_from_result(self):
        if self.result_q.empty():
            return pd.DataFrame(data=[])
        dfs = list(self.result_q.queue)
        df = pd.concat(dfs, ignore_index=False)
        return df

    def getdf(self, url, f1, f2, total, num, tb, conp, current_month, cdc):

        self.url = url

        if current_month:
            # 当前月，获取实时页码，爬取100页
            self.__init_total(f2)
            self.__init_tmp_q(self.total)
            # print('current_month', self.total)
        else:  # 非当前月，查询数据库中历史剩余页面
            try:

                sql = '''select page_left from %s.page_tb where time_period = '%s' ''' % (conp[-1], tb if 'cdc' not in tb else tb.split('_cdc')[0])
                page_tmp = db_query(sql, conp=conp, dbtype='postgresql')
                page_list_temp = page_tmp.values.tolist()
                self.__init_tmp_q(page_list_temp[0][0][1:-1].split(','))

            except:
                # 之前未爬过，那么重新爬取所有页码
                self.__init_total(f2)
                self.__init_tmp_q(self.total)
                total = self.total

        if str(self.tmp_q.qsize()) == '0':
            self.total = 0
        else:
            self.total = self.tmp_q.qsize()


        if num is None: num = 10

        if self.total == 0: return pd.DataFrame()
        self.read_threads(conp=conp, tb=tb, f=f1, num=num, total=total)
        df = self.getdf_from_result()
        return df

    def write(self, **krg):
        url = krg["url"]
        f1 = krg["f1"]
        f2 = krg["f2"]
        tb = krg["tb"]
        col = krg["col"]
        (current_month,) = krg['current_month'],
        cdc = krg['cdc']
        # headless=krg["headless"]
        if "total" not in krg.keys():
            total = None
        else:
            total = krg["total"]

        if "num" not in krg.keys():
            num = None
        else:
            num = krg["num"]
        if "dbtype" not in krg.keys():
            dbtype = "postgresql"
        else:
            dbtype = krg["dbtype"]
        if "conp" not in krg.keys():
            conp = ["postgres", "since2015", "127.0.0.1", "postgres", "public"]
        else:
            conp = krg["conp"]
        if "headless" not in krg.keys():
            self.headless = True
        else:
            self.headless = krg["headless"]

        if "pageloadstrategy" not in krg.keys():
            self.pageloadstrategy = 'normal'
        else:
            self.pageloadstrategy = krg["pageloadstrategy"]

        if "pageloadtimeout" not in krg.keys():
            self.pageloadtimeout = 40
        else:
            self.pageloadtimeout = krg["pageloadtimeout"]

        if total == 0: return False
        print("%s 开始,爬取 %s" % (tb, url))

        df = self.getdf(url, f1, f2, total, num, tb, conp, current_month, cdc)

        if len(df) > 1:
            print(url)
            df.columns = col
        else:
            df = pd.DataFrame(columns=col)
            print("暂无数据,不创建cdc表")
            return False
        print("将数据 df 写入 %s" % tb)
        db_write(df, tb, dbtype=dbtype, conp=conp, datadict='postgresql-text')
        print(" df 写入%s完毕" % tb)
        return True

    ###页数过多时
    def write_large(self, **krg):
        # 初始化页面队列
        # 开启多线程
        # 写入

        url = krg["url"]
        f1 = krg["f1"]
        f2 = krg["f2"]
        tb = krg["tb"]
        col = krg["col"]
        # headless=krg["headless"]
        if "total" not in krg.keys():
            total = None
        else:
            total = krg["total"]

        if "num" not in krg.keys():
            num = None
        else:
            num = krg["num"]
        if "dbtype" not in krg.keys():
            dbtype = "postgresql"
        else:
            dbtype = krg["dbtype"]
        if "conp" not in krg.keys():
            conp = ["postgres", "since2015", "127.0.0.1", "postgres", "public"]
        else:
            conp = krg["conp"]
        if "headless" not in krg.keys():
            self.headless = True
        else:
            self.headless = krg["headless"]

        if "pageloadstrategy" not in krg.keys():
            self.pageloadstrategy = 'normal'
        else:
            self.pageloadstrategy = krg["pageloadstrategy"]

        if "pageloadtimeout" not in krg.keys():
            self.pageloadtimeout = 40
        else:
            self.pageloadtimeout = krg["pageloadtimeout"]

        print("%s 开始,爬取%s" % (tb, url))
        if not total: return False
        df = self.getdf_large(url, f1, f2, total, num)

        if len(df) > 1:
            print(url)
            # print(df)
            df.columns = col
        else:
            df = pd.DataFrame(columns=col)
            print("暂无数据")
        print("将数据 df 写入 %s" % tb)
        db_write(df, tb, dbtype=dbtype, conp=conp, datadict='postgresql-text', if_exists='append')
        print("df 写入 %s 完毕" % tb)

    def read_threads_large(self, f, num=10, total=list(range(100))):
        bg = time.time()
        ths = []
        dfs = []
        total_count = len(total)

        if total_count == 0:
            print("0页,线程不启动，任务结束")
            return False
        if total_count < 2: num = 1
        if num / total_count > 1: num = int(total_count / 5) + 1 if int(total_count / 5) + 1 < 4 else num

        print("开始爬%s,本次共 %d 个页面,共%d 个线程" % (self.url, total_count, num))
        self.result_q.queue.clear()

        # 生成页码queue
        self.tmp_q.queue.clear()
        for i in total:
            self.tmp_q.put(i + 1)

        for _ in range(num):
            t = Thread(target=self.read_thread, args=(f,))
            ths.append(t)
        for t in ths:
            t.start()
        for t in ths:
            t.join()
        self.__init_localhost_q(num=3)
        left_page = self.tmp_q.qsize()
        print("剩余 %d页" % (left_page))
        if left_page > 0:
            self.read_thread(f)
            left_page = self.tmp_q.qsize()
            print("剩余 %d页" % (left_page))
        ed = time.time()
        cost = ed - bg
        if cost < 100:
            print("耗时%d --秒" % cost)
        else:
            print("耗时%.4f 分" % (cost / 60))
        print("read_threads结束")

    def getdf_large(self, url, f1, f2, total, num):
        self.url = url

        ##生成页码queue
        self.tmp_q.queue.clear()
        for i in total:
            self.tmp_q.put(i + 1)

        if not total:
            total = list(range(self.total))
        elif len(total) > self.total:
            total = list(range(self.total))

        if num is None: num = 10
        if total == 0: return pd.DataFrame()
        self.read_threads_large(f=f1, num=num, total=total)
        df = self.getdf_from_result()
        return df

    def get_total(self, f2, url):
        """获取需要爬取的页面总量，先用本地ip爬三次，若失败代理ip爬三次"""
        num = 1
        m = 5

        while m > 0:
            try:

                ip = self.get_ip()
                # ip="1.28.0.90:20455"
                print("使用代理ip %s" % ip)
                driver = self.get_driver(ip)

                driver.get(url)

                self.total = f2(driver)
                driver.quit()
                print("全局共%d 页面" % self.total)
                return self.total
            except Exception as e:
                traceback.print_exc()
                driver.quit()
                m -= 1
                print("用代理ip获取总量,第%d失败" % (3 - m))
        while num > 0:
            try:
                driver = self.get_driver()
                driver.get(url)
                self.total = f2(driver)
                driver.quit()
                print("用本地ip获取总量,全局共%d 页面" % self.total)
                return self.total
            except Exception as e:
                traceback.print_exc()
                driver.quit()
                num -= 1
                print("用本地ip获取总量,第%d失败" % (num))
        return "failed"
