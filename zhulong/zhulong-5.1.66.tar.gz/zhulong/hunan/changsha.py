import json
import math
import re

import requests
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong.util.etl import est_html, est_meta, add_info
import time
from zhulong.util.fake_useragent import UserAgent
_name_ = 'changsha'

UA = UserAgent()
headers={
'Accept': 'text/html, */*; q=0.01',
'Host': 'fwpt.csggzy.cn',
'Origin': 'https://fwpt.csggzy.cn',
'Referer': 'https://fwpt.csggzy.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type1',
'User-Agent': UA.random,
}
data_params = {
'projectName': '',
'date': '1month',
'begin_time': '',
'end_time': '',
'dealType': 'Deal_Type1',
'noticType': '1 ',
'area': '',
'huanJie': 'NOTICE',
'pageIndex': '1',
}
URL = "https://fwpt.csggzy.cn/spweb/CS/TradeCenter/ColTableInfo.do?"
proxy = {}
def get_ip():
    global proxy
    try:
        url = """http://ip.11jsq.com/index.php/api/entry?method=proxyServer.generate_api_url&packid=0&fa=0&fetch_key=&qty=1&time=1&pro=&city=&port=1&format=txt&ss=1&css=&dt=1&specialTxt=3&specialJson="""
        r = requests.get(url)
        time.sleep(1)

        ip = r.text
        proxy = {'http': ip}
    except:

        proxy = {}
    return proxy

get_ip()


def f1(driver, num):
    dealType = re.findall('Deal_Type=(.*?)&', driver.current_url)[0]
    argument = driver.current_url.rsplit('=',maxsplit=1)[-1]
    data2=data_params.copy()
    data2['noticType'] = argument if len(argument) != 1 else (str(argument)+' ')
    data2['dealType'] = dealType
    data2['pageIndex'] = num
    driver_info = webdriver.DesiredCapabilities.CHROME

    try:
        if "--proxy" in driver_info['goog:chromeOptions']['args'][0]:

            proxy_ip = driver_info['goog:chromeOptions']['args'][0].split('=')[1]
            proxies = {proxy_ip[0]: proxy_ip[1]}
            page = requests.post(URL, data=data2, proxies=proxies, headers=headers, timeout=40).text
        else:
            # print(requests.post(driver.current_url, data=data, headers=headers).text)
            page =  requests.post(URL,data=data2,headers=headers, timeout=40).text
    except:
        try:
            page = requests.post(URL, data=data2, headers=headers, proxies=proxy, timeout=40).text
        except:
            get_ip()
            page = requests.post(URL, data=data2, headers=headers, proxies=proxy, timeout=40).text
    data_temp=[]
    body = etree.HTML(page)
    content_list = body.xpath('//td[not(@style)]/parent::*')
    for content in content_list:
        name = content.xpath("./td/a/@title")[0].strip()
        href = "https://fwpt.csggzy.cn" + content.xpath("./td/a/@href")[0].strip()
        ggstart_time = content.xpath("./td[2]/text()")[0]
        temp = [name, ggstart_time, href]
        data_temp.append(temp)

    df = pd.DataFrame(data=data_temp)
    df["info"] = None
    return df


def f2(driver):
    argument = driver.current_url.rsplit('=',maxsplit=1)[-1]
    dealType = re.findall('Deal_Type=(.*?)&',driver.current_url)[0]
    data1=data_params.copy()
    data1['noticType'] = argument if len(argument) != 1 else (str(argument)+' ')
    data1['dealType'] = dealType
    driver_info = webdriver.DesiredCapabilities.CHROME
    try:
        if "--proxy" in driver_info['goog:chromeOptions']['args'][0]:

            proxy_ip = driver_info['goog:chromeOptions']['args'][0].split('=')[1]
            proxies = {proxy_ip[0]: proxy_ip[1]}

            total_page = re.findall('<.*?Page_TotalPage.*?(\d+).*?>', requests.post(URL,proxies=proxies, headers=headers, data=data1,timeout=40).text)[0]
        else:
            total_page = re.findall('<.*?Page_TotalPage.*?(\d+).*?>',requests.post(URL,headers=headers,data=data1,timeout=40).text)[0]
    except:
        total_page = re.findall('<.*?Page_TotalPage.*?(\d+).*?>', requests.post(URL, headers=headers, data=data1,timeout=40).text)[0]

    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@id="publicity_contents" or @id="notice_contents"]')
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
    div = soup.find('div', id='publicity_contents')
    if not div:
        div = soup.find('div', id='notice_contents')
    return div


data = [
    #  房建市政
    ["gcjs_zhaobiao_fjsz_gg",
     "https://fwpt.csggzy.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type1&add=1",
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{'Tag':'房建市政'}), f2],

    ["gcjs_zgys_1_fjsz_gg",
     "https://fwpt.csggzy.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type1&add=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'房建市政'}), f2],

    ["gcjs_kongzhijia_fjsz_gg",
     "https://fwpt.csggzy.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type1&add=92",
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{'Tag':'房建市政'}), f2],

    ["gcjs_zgys_fjsz_gg",
     "https://fwpt.csggzy.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type1&add=91",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'房建市政'}), f2],


    ["gcjs_zhongbiaohx_fjsz_gg",
     "https://fwpt.csggzy.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type1&add=PUBLICITY",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'房建市政'}), f2],

    ["gcjs_gqita_fjsz_gg",
     "https://fwpt.csggzy.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type1&add=WEB_JY_NOTICE",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'房建市政'}), f2],


     # 交通工程
    ["gcjs_zhaobiao_jiaotong_gg",
     "https://fwpt.csggzy.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type2&add=1",
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{'Tag':'交通工程'}), f2],

    ["gcjs_zgys_1_jiaotong_gg",
     "https://fwpt.csggzy.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type2&add=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'交通工程'}), f2],

    ["gcjs_kongzhijia_jiaotong_gg",
     "https://fwpt.csggzy.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type2&add=92",
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{'Tag':'交通工程'}), f2],

    ["gcjs_zgys_jiaotong_gg",
     "https://fwpt.csggzy.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type2&add=91",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'交通工程'}), f2],


    ["gcjs_zhongbiaohx_jiaotong_gg",
     "https://fwpt.csggzy.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type2&add=PUBLICITY",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'交通工程'}), f2],

    ["gcjs_gqita_jiaotong_gg",
     "https://fwpt.csggzy.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type2&add=WEB_JY_NOTICE",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'交通工程'}), f2],

    # 水利工程
    ["gcjs_zhaobiao_shuili_gg",
     "https://fwpt.csggzy.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type3&add=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'Tag': '水利工程'}), f2],

    ["gcjs_zgys_1_shuili_gg",
     "https://fwpt.csggzy.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type3&add=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'Tag': '水利工程'}), f2],

    ["gcjs_kongzhijia_shuili_gg",
     "https://fwpt.csggzy.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type3&add=92",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'Tag': '水利工程'}), f2],

    ["gcjs_zgys_shuili_gg",
     "https://fwpt.csggzy.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type3&add=91",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'Tag': '水利工程'}), f2],

    ["gcjs_zhongbiaohx_shuili_gg",
     "https://fwpt.csggzy.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type3&add=PUBLICITY",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'Tag': '水利工程'}), f2],

    ["gcjs_gqita_shuili_gg",
     "https://fwpt.csggzy.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type3&add=WEB_JY_NOTICE",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'Tag': '水利工程'}), f2],

    # 政府采购
    ["zfcg_zhaobiao_gg",
     "https://fwpt.csggzy.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type3&add=NOTICE",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'Tag': '水利工程'}), f2],

    ["zfcg_zhongbiao_gg",
     "https://fwpt.csggzy.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type3&add=RESULT_NOTICE",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'Tag': '水利工程'}), f2],

    ["zfcg_gqita_gg",
     "https://fwpt.csggzy.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type3&add=WEB_JY_NOTICE",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'Tag': '水利工程'}), f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖南省长沙市", **args)
    est_html(conp, f=f3, **args)

if __name__ == '__main__':


    conp = ["postgres", "since2015", "192.168.3.171", "hunan", "changsha"]
    work(conp,num=3)
    # driver = webdriver.Chrome()
    # for i in data:
    #     driver.get(i[1])
    #     print(f2(driver))
    #     driver = webdriver.Chrome()

    # driver.get("https://fwpt.csggzy.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type1&add=PUBLICITY")
    # print(f2(driver))
    # f1(driver, 3)




