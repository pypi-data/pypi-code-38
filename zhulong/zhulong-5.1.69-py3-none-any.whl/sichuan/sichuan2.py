import lxml
import random
import pandas as pd
import re
import requests
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write, db_command, db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
from html.parser import HTMLParser
import json
from zhulong.util.etl import add_info, est_meta, est_html, est_tbs
from zhulong.util.fake_useragent import UserAgent

_name_ = "sichuan2"
user_agent = UserAgent()
timesEnd = time.strftime('%Y-%m-%d', time.localtime(time.time()))
equal = None


def f1(driver, num):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    except:
        proxies = ''
    start_url = 'http://ggzyjy.sc.gov.cn/inteligentsearch/rest/inteligentSearch/getFullTextData'
    if equal is None: raise ValueError
    payloadData = {
        "pn": (num - 1) * 12,
        "rn": 12,
        "sdt": "2019-01-01 00:00:00",
        "edt": "%s 23:59:59" % timesEnd,
        "fields": "title",
        "sort": "{'infodate':'0'}",
        "ssort": "title",
        "cl": 500,
        "condition": [{"fieldName": "categorynum", "equal": equal, "isLike": "true", "likeType": 2}],
        "noParticiple": "0",
        "isBusiness": "1"
    }
    payloadData = json.dumps(payloadData)
    # print(user_agent)
    headers = {
        'User-Agent': user_agent.random,
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }
    if proxies:
        res = requests.post(url=start_url, headers=headers, data=payloadData, proxies=proxies)
    else:
        res = requests.post(url=start_url, headers=headers, data=payloadData)
    # 需要判断是否为登录后的页面
    data_list = []
    time.sleep(1)
    if res.status_code != 200:
        raise ConnectionError
    else:
        content = res.text
        result = json.loads(content)
        totalcount = result['result']['records']
        for li in totalcount:
            title = li['title']
            infodate = li['infodate']
            linkurl = li['linkurl']
            tmp = [title, infodate, "http://ggzyjy.sc.gov.cn" + linkurl]
            data_list.append(tmp)
    df = pd.DataFrame(data_list)
    df['info'] = None
    return df


def f2(driver):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    except:
        proxies = ''
    global equal
    url = driver.current_url
    equal = re.findall(r'equal=(\d+)', url)[0]
    num = 1
    start_url = 'http://ggzyjy.sc.gov.cn/inteligentsearch/rest/inteligentSearch/getFullTextData'
    payloadData = {
        "pn": (num - 1) * 12,
        "rn": 12,
        "sdt": "2019-01-01 00:00:00",
        "edt": "%s 23:59:59" % timesEnd,
        "fields": "title",
        "sort": "{'infodate':'0'}",
        "ssort": "title",
        "cl": 500,
        "condition": [{"fieldName": "categorynum", "equal": equal, "isLike": "true", "likeType": 2}],
        "noParticiple": "0",
        "isBusiness": "1"
    }
    payloadData = json.dumps(payloadData)

    # print(user_agent)
    headers = {
        'User-Agent': user_agent.random,
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }
    if proxies:
        res = requests.post(url=start_url, headers=headers, data=payloadData, proxies=proxies)
    else:
        res = requests.post(url=start_url, headers=headers, data=payloadData)
    # 需要判断是否为登录后的页面
    data_list = []
    time.sleep(1)
    if res.status_code != 200:
        raise ConnectionError
    else:
        content = res.text
        result = json.loads(content)
        totalcount = result['result']['totalcount']
        try:
            if totalcount / 12 != int(totalcount / 12):
                num = int(totalcount / 12) + 1
            else:
                num = int(totalcount / 12)
        except:
            num = 1
        driver.quit()
        return int(num)


def f3(driver, url):
    driver.get(url)
    time.sleep(2)
    locator = (By.XPATH, "//div[@class='container news-detailed'][string-length()>40]")
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
    div = soup.find('div', attrs={'class': 'container news-detailed'})
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://ggzyjy.sc.gov.cn/jyxx/transactionInfo.html/equal=002001001",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zgys_gg",
     "http://ggzyjy.sc.gov.cn/jyxx/transactionInfo.html/equal=002001002",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_bian_bu_gg",
     "http://ggzyjy.sc.gov.cn/jyxx/transactionInfo.html/equal=002001003",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_liu_zhongz_gg",
     "http://ggzyjy.sc.gov.cn/jyxx/transactionInfo.html/equal=002001004",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_kaibiao_gg",
     "http://ggzyjy.sc.gov.cn/jyxx/transactionInfo.html/equal=002001005",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://ggzyjy.sc.gov.cn/jyxx/transactionInfo.html/equal=002001006",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_hetong_gg",
     "http://ggzyjy.sc.gov.cn/jyxx/transactionInfo.html/equal=002001007",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://ggzyjy.sc.gov.cn/jyxx/transactionInfo.html/equal=002002001",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "http://ggzyjy.sc.gov.cn/jyxx/transactionInfo.html/equal=002002002",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://ggzyjy.sc.gov.cn/jyxx/transactionInfo.html/equal=002002003",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_hetong_gg",
     "http://ggzyjy.sc.gov.cn/jyxx/transactionInfo.html/equal=002002004",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_zhaobiao_gg",
     "http://ggzyjy.sc.gov.cn/jyxx/transactionInfo.html/equal=002007001",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '其他类别'}), f2],

    ["qsy_zhongbiao_gg",
     "http://ggzyjy.sc.gov.cn/jyxx/transactionInfo.html/equal=002007002",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '其他类别'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="四川省省级", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "sichuan", "sichuan2"])

# 修改日期：2019/5/16
