import random

import pandas as pd
import re

import requests
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

import time

from zhulong2.util.etl import est_html, est_meta, add_info, est_meta_large

_name_ = "gansu_shenghui"


def gkzb(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, '(//td[@class="curt"])[1]')
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if str != '公开招标':
            # 点击
            driver.execute_script("classTypeCheck('c1280501');")
            locator = (By.XPATH, '(//td[@class="curt"])[1][not(contains(string(), "%s"))]' % str)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            locator = (By.XPATH, "//input[@name='button']")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        return f(*krg)

    return wrap


def yqzb(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, '(//td[@class="curt"])[1]')
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if str != '邀请招标':
            # 点击
            driver.execute_script("classTypeCheck('c1280502');")
            locator = (By.XPATH, '(//td[@class="curt"])[1][not(contains(string(), "%s"))]' % str)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            locator = (By.XPATH, "//input[@name='button']")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        return f(*krg)

    return wrap


def xjzb(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, '(//td[@class="curt"])[1]')
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if str != '询价公告':
            # 点击
            driver.execute_script("classTypeCheck('c1280101');")
            locator = (By.XPATH, '(//td[@class="curt"])[1][not(contains(string(), "%s"))]' % str)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            locator = (By.XPATH, "//input[@name='button']")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        return f(*krg)

    return wrap


def tpzb(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, '(//td[@class="curt"])[1]')
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if str != '竞争性谈判':
            # 点击
            driver.execute_script("classTypeCheck('c1280103');")
            locator = (By.XPATH, '(//td[@class="curt"])[1][not(contains(string(), "%s"))]' % str)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            locator = (By.XPATH, "//input[@name='button']")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        return f(*krg)

    return wrap


def cszb(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, '(//td[@class="curt"])[1]')
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if str != '竞争性磋商':
            # 点击
            driver.execute_script("classTypeCheck('c1280104');")
            locator = (By.XPATH, '(//td[@class="curt"])[1][not(contains(string(), "%s"))]' % str)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            locator = (By.XPATH, "//input[@name='button']")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        return f(*krg)

    return wrap


def dylyzb(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, '(//td[@class="curt"])[1]')
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if str != '单一来源':
            # 点击
            driver.execute_script("classTypeCheck('c1280102');")
            locator = (By.XPATH, '(//td[@class="curt"])[1][not(contains(string(), "%s"))]' % str)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            locator = (By.XPATH, "//input[@name='button']")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        return f(*krg)

    return wrap


def dylygszb(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, '(//td[@class="curt"])[1]')
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if str != '单一来源公示':
            # 点击
            driver.execute_script("classTypeCheck('c1280105');")
            locator = (By.XPATH, '(//td[@class="curt"])[1][not(contains(string(), "%s"))]' % str)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            locator = (By.XPATH, "//input[@name='button']")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        return f(*krg)

    return wrap


def zgys(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, '(//td[@class="curt"])[1]')
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if str != '资格预审公告':
            # 点击
            driver.execute_script("classTypeCheck('c12806');")
            locator = (By.XPATH, '(//td[@class="curt"])[1][not(contains(string(), "%s"))]' % str)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            locator = (By.XPATH, "//input[@name='button']")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        return f(*krg)

    return wrap


def zhongbiao(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, '(//td[@class="curt"])[1]')
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if str != '中标公告':
            # 点击
            driver.execute_script("classTypeCheck('c12802');")
            locator = (By.XPATH, '(//td[@class="curt"])[1][not(contains(string(), "%s"))]' % str)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            locator = (By.XPATH, "//input[@name='button']")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        return f(*krg)

    return wrap


def chengjiao(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, '(//td[@class="curt"])[1]')
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if str != '成交公告':
            # 点击
            driver.execute_script("classTypeCheck('c12804');")
            locator = (By.XPATH, '(//td[@class="curt"])[1][not(contains(string(), "%s"))]' % str)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            locator = (By.XPATH, "//input[@name='button']")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        return f(*krg)

    return wrap


def biangen(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, '(//td[@class="curt"])[1]')
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if str != '更正公告':
            # 点击
            driver.execute_script("classTypeCheck('c12803');")
            locator = (By.XPATH, '(//td[@class="curt"])[1][not(contains(string(), "%s"))]' % str)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            locator = (By.XPATH, "//input[@name='button']")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        return f(*krg)

    return wrap


def liubiao(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, '(//td[@class="curt"])[1]')
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if str != '废标/终止公告':
            # 点击
            driver.execute_script("classTypeCheck('c12807');")
            locator = (By.XPATH, '(//td[@class="curt"])[1][not(contains(string(), "%s"))]' % str)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            locator = (By.XPATH, "//input[@name='button']")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        return f(*krg)

    return wrap


def qita(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, '(//td[@class="curt"])[1]')
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if str != '其他公告':
            # 点击
            driver.execute_script("classTypeCheck('c12820');")
            locator = (By.XPATH, '(//td[@class="curt"])[1][not(contains(string(), "%s"))]' % str)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            locator = (By.XPATH, "//input[@name='button']")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        return f(*krg)

    return wrap


def f1_data(driver, num):
    locator = (By.XPATH, "//ul[@class='newsList TipsBox']/li[1]/span/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//span[@class='pagecss']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = re.findall('(\d+)', str)[1]
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='newsList TipsBox']/li[1]/span/a").get_attribute('href').rsplit('/',maxsplit=1)[1]

        driver.execute_script("JumpPage('{}')".format(num))
        locator = (By.XPATH, "//ul[@class='newsList TipsBox']/li[1]/span/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("ul", class_='newsList TipsBox')
    trs = table.find_all("li")
    data = []
    for tr in trs:
        a = tr.find("a")
        if a == None:
            continue
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        href = a['href'].strip()
        if 'http' in href:
            link = href
        else:
            link = 'http://www.ccgp-gansu.gov.cn' + a['href'].strip()
        span = tr.find('span', class_='date').text.strip()
        tmp = [title, span, link]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f1(driver, num):
    url = driver.current_url
    if ('/article/130/' in url) or ('/web/article/142/' in url):
        df = f1_data(driver, num)
        return df
    else:
        locator = (By.XPATH, "//ul[@class='Expand_SearchSLisi']/li[1]/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, "//span[@class='pagecss']")
            str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            cnum = re.findall('(\d+)', str)[1]
        except:
            cnum = 1
        if num != int(cnum):
            val = \
            driver.find_element_by_xpath("//ul[@class='Expand_SearchSLisi']/li[1]/a").get_attribute('href').rsplit('/',
                                                                                                                   maxsplit=1)[
                1]

            driver.execute_script("JumpPage('{}')".format(num))
            locator = (By.XPATH, "//ul[@class='Expand_SearchSLisi']/li[1]/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        table = soup.find("ul", class_='Expand_SearchSLisi')
        trs = table.find_all("li")
        data = []
        for tr in trs:
            a = tr.find("a")
            try:
                title = a['title'].strip()
            except:
                title = a.text.strip()
            href = a['href'].strip()
            if 'http' in href:
                link = href
            else:
                link = 'http://www.ccgp-gansu.gov.cn' + a['href'].strip()
            if int(len(tr.find_all('span'))) >= 2:
                span1 = tr.find_all('span')[0].text.strip()
                kbsj = re.findall(r'开标时间：(.*?)\|', span1)[0].strip()
                fbsj = re.findall(r'发布时间：(.*?)\|', span1)[0].strip()
                cgr = re.findall(r'采购人：(.*?)\|', span1)[0].strip()
                dljg = re.findall(r'代理机构：(.*)', span1)[0].strip()
                span2 = tr.find_all('span')[1].text.strip()
                ggxx = span2.split('|')[1].strip()
                xxlx = span2.split('|')[2].strip()
                info = {'kbsj':kbsj,'cgr':cgr,'dljg':dljg,'ggxx':ggxx,'xxlx':xxlx}
                info = json.dumps(info, ensure_ascii=False)
            else:info = None
            tmp = [title, fbsj, link, info]
            data.append(tmp)
        df = pd.DataFrame(data)
        return df


def f2(driver):
    url = driver.current_url
    if ('/article/130/' in url) or ('/web/article/142/' in url):
        locator = (By.XPATH, "//ul[@class='newsList TipsBox']/li[1]/span/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, "//select[@id='Jumppage']/option[last()]")
            num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        except:
            num = 1
        driver.quit()
        return int(num)
    else:
        locator = (By.XPATH, "//ul[@class='Expand_SearchSLisi']/li[1]/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, "//span[@class='pagecss']")
            str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            num = re.findall('(\d+)', str)[2]
        except:
            num = 1
        driver.quit()
        return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='articleCon'][string-length()>10]")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    if '<!-- 正文 -->' not in driver.page_source:
        raise TimeoutError
    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 5: break

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_="articleCon")
    return div


data = [
    ["zfcg_zhaobiao_gongkai_gg",
     "http://www.ccgp-gansu.gov.cn/web/doSearchmxarticle.action",
     ["name", "ggstart_time", "href", "info"], gkzb(add_info(f1, {'zbfs': '公开招标'})), gkzb(f2)],
    # # #
    ["zfcg_zhaobiao_yaoqing_gg",
     "http://www.ccgp-gansu.gov.cn/web/doSearchmxarticle.action",
     ["name", "ggstart_time", "href", "info"], yqzb(add_info(f1, {'zbfs': '邀请招标'})), yqzb(f2)],
    # # #
    ["zfcg_zhaobiao_xunjia_gg",
     "http://www.ccgp-gansu.gov.cn/web/doSearchmxarticle.action",
     ["name", "ggstart_time", "href", "info"], xjzb(add_info(f1, {'zbfs': '询价'})), xjzb(f2)],
    # # #
    ["zfcg_zhaobiao_tanpan_gg",
     "http://www.ccgp-gansu.gov.cn/web/doSearchmxarticle.action",
     ["name", "ggstart_time", "href", "info"], tpzb(add_info(f1, {'zbfs': '竞争性谈判'})), tpzb(f2)],
    # # #
    ["zfcg_zhaobiao_cuoshang_gg",
     "http://www.ccgp-gansu.gov.cn/web/doSearchmxarticle.action",
     ["name", "ggstart_time", "href", "info"], cszb(add_info(f1, {'zbfs': '竞争性磋商'})), cszb(f2)],
    # # #
    ["zfcg_zhaobiao_dyly_gg",
     "http://www.ccgp-gansu.gov.cn/web/doSearchmxarticle.action",
     ["name", "ggstart_time", "href", "info"], dylyzb(add_info(f1, {'zbfs': '单一来源'})), dylyzb(f2)],
    # # #
    ["zfcg_yucai_dylygs_gg",
     "http://www.ccgp-gansu.gov.cn/web/doSearchmxarticle.action",
     ["name", "ggstart_time", "href", "info"], dylygszb(add_info(f1, {'zbfs': '单一来源'})), dylygszb(f2)],

    ["zfcg_zgys_gg",
     "http://www.ccgp-gansu.gov.cn/web/doSearchmxarticle.action",
     ["name", "ggstart_time", "href", "info"], zgys(f1), zgys(f2)],

    # # #
    ["zfcg_zhongbiao_gg",
     "http://www.ccgp-gansu.gov.cn/web/doSearchmxarticle.action",
     ["name", "ggstart_time", "href", "info"], zhongbiao(f1), zhongbiao(f2)],
    # # #
    ["zfcg_zhongbiao_lx2_gg",
     "http://www.ccgp-gansu.gov.cn/web/doSearchmxarticle.action",
     ["name", "ggstart_time", "href", "info"], chengjiao(add_info(f1, {'gglx': '成交公告'})), chengjiao(f2)],
    # # #
    ["zfcg_biangeng_gg",
     "http://www.ccgp-gansu.gov.cn/web/doSearchmxarticle.action",
     ["name", "ggstart_time", "href", "info"], biangen(f1), biangen(f2)],
    # # #
    ["zfcg_gqita_liu_zhongz_gg",
     "http://www.ccgp-gansu.gov.cn/web/doSearchmxarticle.action",
     ["name", "ggstart_time", "href", "info"], liubiao(f1), liubiao(f2)],
    # # #
    ["zfcg_gqita_gg",
     "http://www.ccgp-gansu.gov.cn/web/doSearchmxarticle.action",
     ["name", "ggstart_time", "href", "info"], qita(f1), qita(f2)],
    # # #
    ["zfcg_gqita_zhao_zhong_xygh_gg",
     "http://www.ccgp-gansu.gov.cn/web/article/130/0/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '协议供货'}), f2],
    # # #
    ["zfcg_gqita_zhao_zhong_ddcg_gg",
     "http://www.ccgp-gansu.gov.cn/web/article/142/0/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '定点采购'}), f2],
]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="甘肃省省级", **args)
    est_html(conp, f=f3, **args)


# zfcg_zhaobiao_gongkai_gg页数太多一次性爬不完
# 增加info字段
# 网站新增：http://www.ccgp-gansu.gov.cn/web/doSearchmxarticle.action
# 修改时间：2019/6/20
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "gansu"],pageloadtimeout=120,pageLoadStrategy="none")

    # driver=webdriver.Chrome()
    # url = "http://www.ccgp-gansu.gov.cn/web/article/130/0/index.htm"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    # driver=webdriver.Chrome()
    # url = "http://www.ccgp-gansu.gov.cn/web/article/402882816b494a10016b53a32a881ceb.html"
    # driver.get(url)
    # for i in range(3, 9):
    #     df=f1(driver, i)
    #     print(df.values)
    #     for i in df[2].values:
    #         f = f3(driver, i)
    #         print(f)
