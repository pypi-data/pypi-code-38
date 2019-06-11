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
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

import time

from zhulong2.util.etl import est_html, est_meta, add_info, est_meta_large

from zhulong2.util.fake_useragent import UserAgent

_name_ = "guangdong_guangzhou"

tt_url = None
tt = None
n = 0

def f1(driver, num):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    except:
        proxies = ''
    url = driver.current_url
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': user_agent,
    }
    payloadData = {
        'current': num,
        'rowCount': 10,
        'searchPhrase': '',
        'title_name': '',
        'porid': '{}'.format(tt),
        'kwd': '',
    }
    # 下载超时
    timeOut = 60
    if proxies:
        res = requests.post(url=tt_url, headers=headers, data=payloadData, timeout=timeOut, proxies=proxies)
    else:
        res = requests.post(url=tt_url, headers=headers, data=payloadData, timeout=timeOut)
    # 需要判断是否为登录后的页面
    if res.status_code == 200:
        n = 0
        html = res.text
        html_data = json.loads(html)
        lis = html_data["rows"]
        data = []
        for tr in lis:
            title = tr['title']
            td = tr['creation_time']
            info_id = tr['info_id']
            link = 'http://gzg2b.gzfinance.gov.cn/gzgpimp/portalsys/portal.do?method=pubinfoView&&info_id=' + info_id + '&&porid=' + tt + '&t_k=null'
            tmp = [title, td, link]
            data.append(tmp)
        df = pd.DataFrame(data=data)
        df['info'] = None
        return df
    else:
        global n
        n += 1
        if n < 10:
            time.sleep(10 * n)
            return f1(driver, num)
        else:
            raise TimeoutError


def f2(driver):
    global tt_url, tt
    tt_url = None
    tt = None
    start_url = driver.current_url
    tt_url = start_url.rsplit('/', maxsplit=1)[0]
    tt = start_url.rsplit('/', maxsplit=1)[1]
    page_num = get_pageall(tt_url, tt)
    driver.quit()
    return int(page_num)


def get_pageall(tt_url, tt):
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': user_agent,
    }
    payloadData = {
        'current': 1,
        'rowCount': 10,
        'searchPhrase': '',
        'title_name': '',
        'porid': '{}'.format(tt),
        'kwd': '',
    }
    # 下载超时
    timeOut = 25
    sesion = requests.session()
    res = sesion.post(url=tt_url, headers=headers, data=payloadData, timeout=timeOut)
    # 需要判断是否为登录后的页面
    if res.status_code == 200:
        html = res.text
        html_data = json.loads(html)
        total = html_data['total']
        total = int(total)
        if total / 10 == int(total / 10):
            page_all = int(total / 10)
        else:
            page_all = int(total / 10) + 1
        return page_all


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='panel panel-default'][string-length()>20]")

    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))

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
    div = soup.find('div', class_='panel panel-default')
    return div


data = [
    ["zfcg_zhaobiao_danyilaiyuan_gg",
     "http://gzg2b.gzfinance.gov.cn/gzgpimp/portalsys/portal.do?method=queryHomepageList&t_k=null/dylygs",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '单一来源'}), f2],
    #
    ["zfcg_zhaobiao_gg",
     "http://gzg2b.gzfinance.gov.cn/gzgpimp/portalsys/portal.do?method=queryHomepageList&t_k=null/zbgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_biangeng_gg",
     "http://gzg2b.gzfinance.gov.cn/gzgpimp/portalsys/portal.do?method=queryHomepageList&t_k=null/bggg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://gzg2b.gzfinance.gov.cn/gzgpimp/portalsys/portal.do?method=queryHomepageList&t_k=null/cgjggg",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_yanshou_gg",
     "http://gzg2b.gzfinance.gov.cn/gzgpimp/portalsys/portal.do?method=queryHomepageList&t_k=null/htys",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_gqita_yuanxitong_gg",
     "http://gzg2b.gzfinance.gov.cn/gzgpimp/portalsys/portal.do?method=queryHomepageList&t_k=null/yxtgg",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '原系统公告'}), f2],
    #
    ["zfcg_gqita_fzfcg_gg",
     "http://gzg2b.gzfinance.gov.cn/gzgpimp/portalsys/portal.do?method=queryHomepageList2&t_k=null/fzfcg",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '非政府采购公告'}), f2],
]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="广东省广州市", **args)
    est_html(conp, f=f3, **args)


# zfcg_yuanxitong_gg页数太多跑不完
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "guangzhou"])

    # driver=webdriver.Chrome()
    # url = "http://gzg2b.gzfinance.gov.cn/gzgpimp/portalsys/portal.do?method=queryHomepageList&t_k=null/yxtgg"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    # driver=webdriver.Chrome()
    # url = "http://gzg2b.gzfinance.gov.cn/gzgpimp/portalsys/portal.do?method=queryHomepageList&t_k=null/yxtgg"
    # driver.get(url)
    # for i in range(15662, 15663):
    #     df=f1(driver, i)
    #     print(df.values)
    #     for i in df[2].values:
    #         f = f3(driver, i)
    #         print(f)
