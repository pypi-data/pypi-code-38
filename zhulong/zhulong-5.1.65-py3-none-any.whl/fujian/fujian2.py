import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write,db_command,db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import requests
import json
from zhulong.util.fake_useragent import UserAgent
from zhulong.util.etl import add_info, est_meta, est_html, est_tbs, add_info, est_meta_large
import math

_name_="fujian2"


EndTime = time.strftime("%Y-%m-%d", time.localtime())
Cookie = None
surl,ss=None,None


def f1_data(driver, num):
    driver.get(surl)
    locator = (By.XPATH, "//div[@id='list']/div[1]//h4/a")
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-9:]
    locator = (By.XPATH, "//span[@class='fp-text']/b")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text

    url = driver.current_url
    if num != int(cnum):
        driver.execute_script('setPage(%d)' % num)
        locator = (By.XPATH, "//div[@id='list']/div[1]//h4/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("div", id="list")
    trs = table.find_all("div" ,class_='publicont')
    data = []
    for tr in trs:
        a = tr.find_all('a')
        try:
            title = a[0]["title"].strip()
        except:
            title = a[0].text.strip()
        if not title:raise ValueError
        if ss == 'dayi':
            span = tr.find_all("span", class_='span_o')[-1]
            if span.find('a'):
                href = span.find('a')["href"]
                if 'http' in href:
                    link = href
                else:
                    link = "https://www.fjggfw.gov.cn/Website/FJBID_DATA/" + href.strip()
                td = '-'
                tmp = [title, td, link]
                data.append(tmp)
            else:continue

        elif ss == 'zhongbhx':
            span = tr.find_all("span", class_='span_o')[-2]
            if span.find('a'):
                href = span.find('a')["href"]
                if 'http' in href:
                    link = href
                else:
                    link = "https://www.fjggfw.gov.cn/Website/FJBID_DATA/" + href.strip()
                td = '-'
                tmp = [title, td, link]
                data.append(tmp)
            else:continue

        elif ss == 'zhongb':
            span = tr.find_all("span", class_='span_o')[-3]
            if span.find('a'):
                href = span.find('a')["href"]
                if 'http' in href:
                    link = href
                else:
                    link = "https://www.fjggfw.gov.cn/Website/FJBID_DATA/" + href.strip()
                td = '-'
                tmp = [title, td, link]
                data.append(tmp)
            else:continue

        elif ss == 'zb':
            href = a[0]["href"]
            if 'http' in href:
                link = href
            else:
                link = "https://www.fjggfw.gov.cn/Website/FJBID_DATA/" + href.strip()
            try:
                td = tr.find_all("span", class_='span_o')[0].text.strip()
            except:
                td = '-'
            tmp = [title, td, link]
            data.append(tmp)

    df = pd.DataFrame(data)
    df['info'] = None
    return df



def f1(driver, num):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s'% proxy}
    except:
        proxies = ''
    url = driver.current_url
    if '/FJBID_DATA_LIST.aspx' in url:
        daf = f1_data(driver, num)
        return daf
    data = payload_Data(url, num)
    start_url = 'https://www.fjggfw.gov.cn/Website/AjaxHandler/BuilderHandler.ashx'
    ua = UserAgent()
    user_agent = ua.random
    headers = {
        'User-Agent': user_agent,
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        "Cookie": Cookie
    }
    if proxies:
        res = requests.post(url=start_url, headers=headers, data=data, proxies=proxies,timeout=60)
    else:
        res = requests.post(url=start_url, headers=headers, data=data,timeout=60)
    # 需要判断是否为登录后的页面
    if res.status_code != 200:
        raise ConnectionError
    else:
        html = res.text
        if html:
            html = json.loads(html)
            datas = html["data"]
            if datas==[]:
                df = pd.DataFrame()
                print("暂无数据")
                return df
            data = []
            for tr in datas:
                title = tr["NAME"].strip()
                td = tr["TM"].strip()
                href = 'https://www.fjggfw.gov.cn/Website/JYXX_GCJS.aspx?ID=%s&GGTYPE=%s' %(tr['M_ID'], tr['GGTYPE'])

                info = {}
                diqu = tr['AREANAME']
                if diqu:info['diqu']=diqu
                ly = tr['PLATFORM_NAME']
                if ly:info['ly']=ly
                gglx = tr['TITLE']
                if gglx:info['gglx']=gglx
                hy = tr['PROTYPE_TEXT']
                if hy:info['hy']=hy
                if info:info = json.dumps(info, ensure_ascii=False)
                else: info=None
                tmp = [title, td, href, info]
                data.append(tmp)

            df = pd.DataFrame(data)
            return df


def payload_Data(url, num):
    # gcjs
    if "gcjs_zb" in url:
        data= {"OPtype": "GetListNew","pageNo": num,"pageSize": 10,"proArea": -1,"category": "GCJS","announcementType": 1,"ProType": -1,"xmlx": -1,"projectName": "","TopTime": "2009-01-01 00:00:00","EndTime": "%s 23:59:59" % EndTime,}

    elif "gcjs_zgys" in url:

        data = {"OPtype": "GetListNew","pageNo": num,"pageSize": 10,"proArea": -1,"category": "GCJS","announcementType": 6,"ProType": -1,"xmlx": -1,"projectName": "","TopTime": "2009-01-01 00:00:00","EndTime": "%s 23:59:59" % EndTime,}

    elif "gcjs_bg" in url:

        data = {"OPtype": "GetListNew","pageNo": num,"pageSize": 10,"proArea": -1,"category": "GCJS","announcementType": "2,3,7","ProType": "-1","xmlx": "-1","projectName": "","TopTime": "2009-01-01 00:00:00","EndTime": "%s 23:59:59" % EndTime,}

    elif "gcjs_zhongbhx" in url:

        data =  {"OPtype": "GetListNew","pageNo": num,"pageSize": "10","proArea": "-1","category": "GCJS","announcementType": "4","ProType": "-1","xmlx": "-1","projectName": "","TopTime": "2009-01-01 00:00:00","EndTime": "%s 23:59:59"% EndTime,}

    elif "gcjs_zhongb" in url:

        data = {"OPtype": "GetListNew","pageNo": num,"pageSize": "10","proArea": "-1","category": "GCJS","announcementType": "5","ProType": "-1","xmlx": "-1","projectName": "","TopTime": "2009-01-01 00:00:00","EndTime": "%s 23:59:59"% EndTime,}

    # zfcg
    elif "zfcg_zb" in url:
        data = {"OPtype": "GetListNew","pageNo": num,"pageSize": "10","proArea": "-1","category": "ZFCG","announcementType": "1","ProType": "-1","xmlx": "-1","projectName": "","TopTime": "2009-01-01 00:00:00","EndTime": "%s 23:59:59"% EndTime,}

    elif "zfcg_bg" in url:
        data = {"OPtype": "GetListNew","pageNo": num,"pageSize": "10","proArea": "-1","category": "ZFCG","announcementType": "4","ProType": "-1","xmlx": "-1","projectName": "","TopTime": "2009-01-01 00:00:00","EndTime": "%s 23:59:59"% EndTime,}

    elif "zfcg_zhongb" in url:
        data = {"OPtype": "GetListNew","pageNo": num,"pageSize": "10","proArea": "-1","category": "ZFCG","announcementType": "2","ProType": "-1","xmlx": "-1","projectName": "","TopTime": "2009-01-01 00:00:00","EndTime": "%s 23:59:59"% EndTime,}

    # qita
    elif "qt_zb" in url:
        data = {"OPtype": "GetListNew","pageNo": num,"pageSize": "10","proArea": "-1","category": "QT","announcementType": "1","ProType": "-1","xmlx": "-1","projectName": "","TopTime": "2019-03-08 00:00:00","EndTime": "%s 23:59:59" % EndTime,}

    elif "qt_zhongb" in url:
        data = {"OPtype": "GetListNew","pageNo": num,"pageSize": "10","proArea": "-1","category": "QT","announcementType": "2","ProType": "-1","xmlx": "-1","projectName": "","TopTime": "2019-03-08 00:00:00","EndTime": "%s 23:59:59" % EndTime,}
    return data


def f2(driver):
    global Cookie
    url = driver.current_url
    if '/FJBID_DATA_LIST.aspx' in url:
        global surl,ss
        surl,ss=None,None
        surl = url.rsplit('/', maxsplit=1)[0]
        ss = url.rsplit('/', maxsplit=1)[1]
        driver.get(surl)
        locator = (By.XPATH, "//div[@id='list']/div[1]//h4/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, "//span[@class='fp-text']/i")
        num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        driver.quit()
        return int(num)

    else:
        data = payload_Data(url, 1)
        url = url.rsplit('/', maxsplit=1)[0]
        driver.get(url)
        # cookies = driver.get_cookies()
        Cookie = ''
        for cookie in driver.get_cookies():
            cook = "%s=%s;" % (cookie['name'], cookie['value'])
            Cookie+=cook
        num = get_pageall(url, Cookie, data)
        driver.quit()
        return num


def get_pageall(url, Cookie, data):
    start_url = 'https://www.fjggfw.gov.cn/Website/AjaxHandler/BuilderHandler.ashx'
    ua = UserAgent()
    user_agent = ua.random
    headers = {
        'User-Agent': user_agent,
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        "Cookie": Cookie
    }
    res = requests.post(url=start_url, headers=headers, data=data,timeout=60)
    # 需要判断是否为登录后的页面
    if res.status_code != 200:
        raise ConnectionError
    else:
        html = res.text
        if html:
            html = json.loads(html)
            # data = html["data"]
            total = int(html['total'])
            page_all = math.ceil(total / 10)
            return page_all


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='gc_body'][string-length()>30]")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    locator = (By.XPATH, "//div[@id='noteContentMain'][string-length()>15]")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find('div', class_="gc_body")
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "https://www.fjggfw.gov.cn/Website/JYXXNew.aspx/gcjs_zb",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zgys_gg",
     "https://www.fjggfw.gov.cn/Website/JYXXNew.aspx/gcjs_zgys",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_biangeng_gg",
     "https://www.fjggfw.gov.cn/Website/JYXXNew.aspx/gcjs_bg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "https://www.fjggfw.gov.cn/Website/JYXXNew.aspx/gcjs_zhongbhx",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhaobiao_gg",
     "https://www.fjggfw.gov.cn/Website/JYXXNew.aspx/gcjs_zhongb",
     ["name", "ggstart_time", "href", "info"],f1, f2],

    ["zfcg_zhaobiao_gg",
     "https://www.fjggfw.gov.cn/Website/JYXXNew.aspx/zfcg_zb",
     ["name", "ggstart_time", "href", "info"],f1, f2],

    ["zfcg_biangeng_gg",
     "https://www.fjggfw.gov.cn/Website/JYXXNew.aspx/zfcg_bg",
     ["name", "ggstart_time", "href", "info"], f1,f2],

    ["zfcg_zhongbiao_gg",
     "https://www.fjggfw.gov.cn/Website/JYXXNew.aspx/zfcg_zhongb",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["jqita_zhaobiao_gg",
     "https://www.fjggfw.gov.cn/Website/JYXXNew.aspx/qt_zb",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_gg",
     "https://www.fjggfw.gov.cn/Website/JYXXNew.aspx/qt_zhongb",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ####
    ["jqita_zhoabiao_lishishuju_gg",
     "https://www.fjggfw.gov.cn/Website/FJBID_DATA/FJBID_DATA_LIST.aspx/zb",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_dayi_lishishuju_gg",
     "https://www.fjggfw.gov.cn/Website/FJBID_DATA/FJBID_DATA_LIST.aspx/dayi",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiaohx_lishishuju_gg",
     "https://www.fjggfw.gov.cn/Website/FJBID_DATA/FJBID_DATA_LIST.aspx/zhongbhx",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhongbiao_lishishuju_gg",
     "https://www.fjggfw.gov.cn/Website/FJBID_DATA/FJBID_DATA_LIST.aspx/zhongb",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]



def work(conp,**args):
    est_meta_large(conp,data=data,diqu="福建省省级",**args)
    est_html(conp,f=f3,**args)


# 修改日期：2019/6/26
# 替换爬虫文件
if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","fujian","fujian2"])

    # url="https://www.fjggfw.gov.cn/Website/FJBID_DATA/FJBID_DATA_LIST.aspx/zb"
    # driver=webdriver.Chrome()
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    # url="https://www.fjggfw.gov.cn/Website/FJBID_DATA/FJBID_DATA_LIST.aspx/zb"
    # driver=webdriver.Chrome()
    # driver.get(url)
    # for i in range(3332, 3334):
    #     df = f1(driver, i)
    #     print(df.values)
    #     for d in df[2].values:
    #         dd = f3(driver, d)
    #         print(dd)

