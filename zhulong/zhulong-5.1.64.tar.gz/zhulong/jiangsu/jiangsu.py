import json
import math
import random
from threading import Thread

import requests
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from fake_useragent import UserAgent
import pandas as pd
from zhulong.util.etl import est_html, est_meta
import time

_name_ = 'jiangsu'

UA = UserAgent()
data_params = {
    "token": "", "pn": 0, "rn": 100, "sdt": "", "edt": "", "wd": '', "inc_wd": "", "exc_wd": "", "fields": "title",
    "cnum": "001", "sort": "{\"infodatepx\":\"0\"}", "ssort": "title", "cl": 200, "terminal": "",
    "condition": [{"fieldName": "categorynum", "isLike": True, "likeType": 2, "equal": "003001006"}],
    "time": [{"fieldName": "infodatepx", "startTime": "2000-01-01 00:00:00", "endTime": "2019-04-19 23:59:59"}],
    "highlights": "title", "statistics": '', "unionCondition": '', "accuracy": "", "noParticiple": "1",
    "searchRange": '', "isBusiness": "1"
}

headers = {
'Accept': 'application/json, text/javascript, */*; q=0.01',
'Content-Type': 'application/json;charset=UTF-8',
'Origin': 'http://jsggzy.jszwfw.gov.cn',
'Referer': 'http://jsggzy.jszwfw.gov.cn/jyxx/tradeInfonew.html?aa=003001001',
'User-Agent': UA.random
}

def get_ip():
    try:
        url = """http://ip.11jsq.com/index.php/api/entry?method=proxyServer.generate_api_url&packid=0&fa=0&fetch_key=&qty=1&time=1&pro=&city=&port=1&format=txt&ss=1&css=&dt=1&specialTxt=3&specialJson="""
        r = requests.get(url)
        time.sleep(1)

        ip = r.text
        proxy = {'http': ip}
    except:

        proxy = {}
    return proxy


def f1(driver, num):
    """
    f1 爬取并翻页  driver： web驱动对象， num：当前爬取的页面
    """
    category = driver.current_url.split('?')[1]
    driver_info = webdriver.DesiredCapabilities.CHROME
    payload = data_params.copy()
    payload['condition'][0]['equal']=category
    payload['pn']=(num-1)*100
    try:
        if "--proxy" in driver_info['goog:chromeOptions']['args'][0]:

            proxy_ip = driver_info['goog:chromeOptions']['args'][0].split('=')[1].split('://')
            proxies = {proxy_ip[0]: proxy_ip[1]}
            body = requests.post(driver.current_url, headers=headers,data=json.dumps(payload), proxies=proxies,timeout=40).text
        else:
            time.sleep(random.randint(3, 5))
            body = requests.post(driver.current_url, headers=headers,data=json.dumps(payload),timeout=40).text
    except:
        body = requests.post(driver.current_url, headers=headers,data=json.dumps(payload),proxies=get_ip(),timeout=40).text

    data = []
    content_list = json.loads(body).get('result').get("records")
    for content in content_list:
        name = content.get('title')
        ggstart_time = content.get('infodateformat')
        url = 'http://jsggzy.jszwfw.gov.cn' + content.get('linkurl')
        type = content.get('author')
        area = content.get('zhuanzai')
        info = json.dumps({'type':type,"area":area},ensure_ascii=False)
        temp = [name, ggstart_time, url, info]
        data.append(temp)

    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    """
        总页数
    """
    category = driver.current_url.split('?')[1]
    driver_info = webdriver.DesiredCapabilities.CHROME
    payload = data_params.copy()
    payload['condition'][0]['equal']=category

    try:
        if "--proxy" in driver_info['goog:chromeOptions']['args'][0]:

            proxy_ip = driver_info['goog:chromeOptions']['args'][0].split('=')[1].split('://')
            proxies = {proxy_ip[0]: proxy_ip[1]}
            content = requests.post(driver.current_url, headers=headers,data=json.dumps(payload), proxies=proxies,timeout=40).text
        else:
            time.sleep(random.randint(3, 5))
            content = requests.post(driver.current_url, headers=headers,data=json.dumps(payload),timeout=40).text
    except:
        content = requests.post(driver.current_url, headers=headers,data=json.dumps(payload),timeout=40).text

    total_page = math.ceil(int(json.loads(content).get('result').get('totalcount')) / 100)
    return int(total_page)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, "//div[@class='ewb-trade-main']")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
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

    div = soup.find('div', class_='ewb-trade-main')
    return div




data = [
    # # 工程建设招标公告
    ["gcjs_zhaobiao_gg",
     "http://jsggzy.jszwfw.gov.cn/inteligentsearch/rest/inteligentSearch/getFullTextData?003001001",
     ["name", "ggstart_time", "href", "info"],f1, f2],
    # 工程建设中标公告
    ["gcjs_zhongbiao_gg",
     "http://jsggzy.jszwfw.gov.cn/inteligentsearch/rest/inteligentSearch/getFullTextData?003001008",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # 工程建设最高限价公示
    ["gcjs_kongzhijia_gg",
     "http://jsggzy.jszwfw.gov.cn/inteligentsearch/rest/inteligentSearch/getFullTextData?003001005",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # 工程建设中标候选
    ["gcjs_zhongbiaohx_gg",
     "http://jsggzy.jszwfw.gov.cn/inteligentsearch/rest/inteligentSearch/getFullTextData?003001007",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zgysjg_gg",
     "http://jsggzy.jszwfw.gov.cn/inteligentsearch/rest/inteligentSearch/getFullTextData?003001006",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    # 政府采购预告
    ["zfcg_yucai_gg",
     "http://jsggzy.jszwfw.gov.cn/inteligentsearch/rest/inteligentSearch/getFullTextData?003004001",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    # 政府采购中标公告
    ["zfcg_zhongbiao_gg",
     "http://jsggzy.jszwfw.gov.cn/inteligentsearch/rest/inteligentSearch/getFullTextData?003004006",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # 政府采购更正公告
    ["zfcg_biangeng_gg",
     "http://jsggzy.jszwfw.gov.cn/inteligentsearch/rest/inteligentSearch/getFullTextData?003004003",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    # 政府采购招标公告
    ["zfcg_zhaobiao_gg",
     "http://jsggzy.jszwfw.gov.cn/inteligentsearch/rest/inteligentSearch/getFullTextData?003004002",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],

    # 交通工程招标
    ["gcjs_jiaotong_zhaobiao_gg",
     "http://jsggzy.jszwfw.gov.cn/inteligentsearch/rest/inteligentSearch/getFullTextData?003002001",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # 交通工程中标候选人
    ["gcjs_jiaotong_zhongbiaohx_gg",
     "http://jsggzy.jszwfw.gov.cn/inteligentsearch/rest/inteligentSearch/getFullTextData?003002003",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # 交通工程中标结果
    ["gcjs_jiaotong_zhongbiao_gg",
     "http://jsggzy.jszwfw.gov.cn/inteligentsearch/rest/inteligentSearch/getFullTextData?003002004",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # 交通工程中标结果

    # 水利工程招标公告
    ["gcjs_shuili_zhaobiao_gg",
     "http://jsggzy.jszwfw.gov.cn/inteligentsearch/rest/inteligentSearch/getFullTextData?003003001",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # 水利工程中标候选人公告
    ["gcjs_shuili_zhongbiaohx_gg",
     "http://jsggzy.jszwfw.gov.cn/inteligentsearch/rest/inteligentSearch/getFullTextData?003003003",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # 水利工程中标结果公告
    ["gcjs_shuili_zhongbiao_gg",
     "http://jsggzy.jszwfw.gov.cn/inteligentsearch/rest/inteligentSearch/getFullTextData?003003004",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    # 药品耗材采购公告
    ["yiliao_zhaobiao_gg",
     "http://jsggzy.jszwfw.gov.cn/inteligentsearch/rest/inteligentSearch/getFullTextData?003010002",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # 药品耗材成交公告
    ["yiliao_zhongbiao_gg",
     "http://jsggzy.jszwfw.gov.cn/inteligentsearch/rest/inteligentSearch/getFullTextData?003010002",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # 其他采购公告
    ["qita_zhaobiao_gg",
     "http://jsggzy.jszwfw.gov.cn/inteligentsearch/rest/inteligentSearch/getFullTextData?003011001",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # 其他成交公告
    ["qita_zhongbiao_gg",
     "http://jsggzy.jszwfw.gov.cn/inteligentsearch/rest/inteligentSearch/getFullTextData?003011002",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **kwargs):
    est_meta(conp, data=data, diqu="江苏省", **kwargs)
    est_html(conp, f=f3, **kwargs)


if __name__ == "__main__":
    # driver = webdriver.Chrome()
    #
    # url = 'http://jsggzy.jszwfw.gov.cn/inteligentsearch/rest/inteligentSearch/getFullTextData?003001001'
    # # for da in data:
    # #     url = da[1]
    # driver.get(url)
    # f1(driver,2)
    #     print(f2(driver))
    conp=["postgres", "since2015", "192.168.4.175", "jiangsu", "jiangsu"]
    # import sys
    # arg=sys.argv
    # if len(arg) >3:
    #     work(conp,num=int(arg[1]),total=int(arg[2]),html_total=int(arg[3]))
    # elif len(arg) == 2:
    #     work(conp, html_total=int(arg[1]))
    # else:
    work(conp,num=4)
    # print(get_ip())
