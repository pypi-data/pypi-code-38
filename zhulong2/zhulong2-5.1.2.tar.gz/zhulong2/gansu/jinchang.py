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

from zhulong2.util.etl import est_html, est_meta, add_info
from zhulong2.util.fake_useragent import UserAgent

_name_ = "gansu_jinchang"


def f1(driver, num):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    except:
        proxies = ''
    url = driver.current_url
    columnid = re.findall(r'col/col(\d+)/', url)[0]
    unitid = re.findall(r'uid=(\d+)', url)[0]
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    start_url = "http://www.jc.gansu.gov.cn/module/jslib/jquery/jpage/dataproxy.jsp?startrecord={}&endrecord={}&perpage=11".format(
        ((num - 1) * 3 * 11 + 1), (num * 3 * 11))
    headers = {
        'User-Agent': user_agent,
    }
    data = {
        "col": "1",
        "appid": "1",
        "webid": "1",
        "path": "/",
        "columnid": columnid,
        "sourceContentType": "1",
        "unitid": unitid,
        "webname": "金昌市人民政府",
        "permissiontype": "0",
    }
    if proxies:
        res = requests.post(url=start_url, headers=headers, data=data, proxies=proxies)
    else:
        res = requests.post(url=start_url, headers=headers, data=data)
    if res.status_code == 200:
        page = res.text
        if page:
            page = re.findall(r'<recordset>(.*)</recordset>', page, re.S)[0]
            soup = BeautifulSoup(page, 'html.parser')
            divs = soup.find_all('record')
            data_list = []
            for div in divs:
                lis = re.findall(r'CDATA\[(.*)\]\]></record>', str(div), re.S)[0]
                soup = BeautifulSoup(lis, 'html.parser')
                lis = soup.find_all('tr')
                for li in lis:
                    info = {}
                    a = li.find('a')
                    title = a.text.strip()
                    link = 'http://www.jc.gansu.gov.cn/' + a['href'].strip()
                    span = li.find('span', class_='bt_time').text.strip()
                    if re.findall(r'^\[(.*?)\]', title):
                        diqu = re.findall(r'^\[(.*?)\]', title)[0]
                        info['diqu'] = diqu
                    if info:
                        info = json.dumps(info, ensure_ascii=False)
                    else:
                        info = None
                    tmp = [title, span, link, info]
                    data_list.append(tmp)
            df = pd.DataFrame(data_list)
            return df


def f2(driver):
    locator = (By.XPATH, "//*[@id='87963']/div/table[1]/tbody/tr/td[2]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//span[@class='default_pgTotalPage']")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = int(st)
    except:
        num = 1
    if int(num) / 3 == int(int(num) / 3):
        num = int(int(num) / 3)
    else:
        num = int(int(num) / 3) + 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    if '404' in driver.title:
        return 404
    locator = (By.XPATH, "//table[@id='c'][string-length()>30]")
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
    div = soup.find('table', id="c")
    return div


data = [
    ["zfcg_gqita_zhao_bian_gg",
     "http://www.jc.gansu.gov.cn/col/col1303/index.html?uid=87963&pageNum=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["zfcg_zhongbiao_gg",
     "http://www.jc.gansu.gov.cn/col/col1304/index.html?uid=87963&pageNum=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="甘肃省金昌市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "jinchang"])
