import random
from collections import OrderedDict

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

from zhulong2.util.fake_useragent import UserAgent

_name_ = "shanxi_shenghui"

tt_url = None
tt = None


def f1(driver, num):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    except:
        proxies = ''
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': user_agent,
    }
    payloadData = {
        "parameters['purcatalogguid']": "",
        "page.pageNum": num,
        "parameters['title']": "",
        "parameters['startdate']": "",
        "parameters['enddate']": "",
        "parameters['regionguid']": tt,
        "parameters['projectcode']": "",
        "province": "",
        "parameters['purmethod']": "",
    }
    # 下载超时
    timeOut = 25
    time.sleep(random.uniform(1, 3))
    if proxies:
        res = requests.post(url=tt_url, headers=headers, data=payloadData, timeout=timeOut, proxies=proxies)
    else:
        res = requests.post(url=tt_url, headers=headers, data=payloadData, timeout=timeOut)
    # 需要判断是否为登录后的页面
    if res.status_code == 200:
        html = res.text
        html_data = BeautifulSoup(html, 'html.parser')
        div = html_data.find('div', class_="list-box")
        tbody = div.find('table', class_="table table-no tab-striped tab-hover").tbody
        trs = tbody.find_all('tr')
        data = []
        for tr in trs:
            a = tr.find('a')
            try:
                title = a['title'].strip()
            except:
                title = a.text.strip()
            try:
                td = tr.find_all('td')[-1].text.strip()
            except:
                td = '-'
            link = a['href'].strip()
            try:
                diqu = tr.find_all('td')[1].text.strip()
                diqu = re.findall(r'\[(.*?)\]', diqu)[0]
                info = {'diqu': '{}'.format(diqu)}
                info = json.dumps(info, ensure_ascii=False)
            except:
                info = None
            tmp = [title, td, link, info]
            data.append(tmp)
        df = pd.DataFrame(data=data)
        return df


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
        "parameters['purcatalogguid']": "",
        "page.pageNum": 1,
        "parameters['title']": "",
        "parameters['startdate']": "",
        "parameters['enddate']": "",
        "parameters['regionguid']": tt,
        "parameters['projectcode']": "",
        "province": "",
        "parameters['purmethod']": "",
    }
    # 下载超时
    timeOut = 25
    res = requests.post(url=tt_url, headers=headers, data=payloadData, timeout=timeOut)
    # 需要判断是否为登录后的页面
    if res.status_code == 200:
        html = res.text
        html_data = BeautifulSoup(html, 'html.parser')
        ul = html_data.find('ul', class_="pagination")
        total = ul.find_all('a')[-1]['href']
        total = re.findall(r',(\d+)', total)[0]
        return total


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='contain detail-con'][string-length()>10]")
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
    div = soup.find('div', class_='contain detail-con')
    # div=div.find_all('div',class_='ewb-article')[0]

    return div


def get_data():
    xs = OrderedDict(
        [("西安市", "6101"), ("铜川市", "6102"), ("宝鸡市", "6103"), ("咸阳市", "6104"), ("渭南市", "6105"), ("延安市", "6106"),
         ("汉中市", "6107"),
         ("榆林市", "6108"), ("安康市", "6109"), ("商洛市", "6110"), ("杨凌示范区", "6111"), ("西咸新区", "6169")])
    ggtype2 = OrderedDict([("zhaobiao", "3"), ("zhongbiao", "5"), ("biangeng", "4"), ("zhongzhi", "6"), ("gqita", "99"),
                           ("zhaobiao_danyilaiyuan", "1")])
    data = []

    for w1 in ggtype2.keys():
        for w2 in xs.keys():
            p1 = "%s" % (ggtype2[w1])
            p2 = "%s" % (xs[w2])
            href = "http://www.ccgp-shaanxi.gov.cn/notice/noticeaframe.do?isgovertment=&noticetype=%s/%s" % (p1, p2)
            info = {}
            if 'zhaobiao_danyilaiyuan' in w1:
                info['zbfs'] = '单一来源'
            info['diqu1'] = w2
            if info:
                tmp = ["zfcg_%s_xs%s_gg" % (w1, xs[w2]), href, ["name", "ggstart_time", "href", "info"],add_info(f1, info), f2]
            else:
                tmp = ["zfcg_%s_xs%s_gg" % (w1, xs[w2]), href, ["name", "ggstart_time", "href", "info"],f1, f2]
            data.append(tmp)
    # remove_arr=["gcjs_biangeng_gctype004_gg","gcjs_biangeng_gctype005_gg","gcjs_biangeng_gctype005_gg"]
    data1 = data.copy()
    # for w in data:
    #     if w[0] in remove_arr:data1.remove(w)
    return data1


data1 = get_data()

data2 = [
    ["zfcg_zhaobiao_shengji_gg",
     "http://www.ccgp-shaanxi.gov.cn/notice/noticeaframe.do?isgovertment=&noticetype=3/610001",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu1': '省级'}), f2],
    #
    ["zfcg_zhongbiao_shengji_gg",
     "http://www.ccgp-shaanxi.gov.cn/notice/noticeaframe.do?isgovertment=&noticetype=5/610001",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu1': '省级'}), f2],
    #
    ["zfcg_biangeng_shengji_gg",
     "http://www.ccgp-shaanxi.gov.cn/notice/noticeaframe.do?isgovertment=&noticetype=4/610001",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu1': '省级'}), f2],
    #
    ["zfcg_zhongzhi_shengji_gg",
     "http://www.ccgp-shaanxi.gov.cn/notice/noticeaframe.do?isgovertment=&noticetype=6/610001",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu1': '省级'}), f2],
    #
    ["zfcg_gqita_shengji_gg",
     "http://www.ccgp-shaanxi.gov.cn/notice/noticeaframe.do?isgovertment=&noticetype=99/610001",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu1': '省级'}), f2],
    #
    ["zfcg_zhaobiao_danyilaiyuan_shengji_gg",
     "http://www.ccgp-shaanxi.gov.cn/notice/noticeaframe.do?isgovertment=&noticetype=1/610001",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu1': '省级', 'gglx': '单一来源'}), f2],

]

data = data1 + data2


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="陕西省省级", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "shanxi"], pageloadtimeout=120)
