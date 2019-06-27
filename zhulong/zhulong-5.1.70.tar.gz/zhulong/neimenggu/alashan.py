import re
import time
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
import pandas as pd
from zhulong.util.etl import est_meta, est_html
from zhulong.util.fake_useragent import UserAgent

_name_ = "alashan"
ua = UserAgent()
param = {
    'businessType': '2',
    'announcementType': '003',
    'page': '1',
    'rows': '15',
    'areaCode': '152900',
}

headers = {
    'User-Agent': ua.random
}
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


def f1(driver, num):
    announcementType, businessType = driver.current_url.split('?')[1].split('_')
    url = driver.current_url.split('?')[0]
    driver_info = webdriver.DesiredCapabilities.CHROME
    data_param = param.copy()
    data_param['page'] = num
    data_param['businessType'] = businessType
    data_param['announcementType'] = announcementType
    try:
        if "--proxy" in driver_info['goog:chromeOptions']['args'][0]:
            proxy_ip = driver_info['goog:chromeOptions']['args'][0].split('=')[1].split('://')
            proxies = {proxy_ip[0]: proxy_ip[1]}
            res = requests.post(url, headers=headers, data=data_param, timeout=40, proxies=proxies).text
        else:
            if proxy == {}: get_ip()
            res = requests.post(url, headers=headers, data=data_param, timeout=40, proxies=proxy).text

    except:
        try:
            res = requests.post(url, headers=headers, data=data_param, timeout=40, proxies=proxy).text

        except:
            get_ip()
            res = requests.post(url, headers=headers, data=data_param, timeout=40, proxies=proxy).text

    content = json.loads(res, encoding='utf-8')

    # print(res)
    data1 =[]
    content_list = content['data']['list']
    # print(content_list)
    for content in content_list:
        name = content['title']
        href = 'http://www.alsggzyjy.cn/PublicServer/public/commonAnnouncement/showDetail.html?'+'businessType='+content['businessType']+'&id='+content['id']
        ggstart_time = content['publishTime']

        temp = [name, ggstart_time, href]
        data1.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data1)
    df["info"] = None
    return df


def f2(driver):

    announcementType,businessType = driver.current_url.split('?')[1].split('_')
    url = driver.current_url.split('?')[0]
    driver_info = webdriver.DesiredCapabilities.CHROME
    data_param = param.copy()
    data_param['announcementType'] = announcementType
    data_param['businessType'] = businessType

    try:
        if "--proxy" in driver_info['goog:chromeOptions']['args'][0]:
            proxy_ip = driver_info['goog:chromeOptions']['args'][0].split('=')[1].split('://')
            proxies = {proxy_ip[0]: proxy_ip[1]}
            # print(proxies)
            res = requests.post(url, headers=headers, data=data_param, timeout=40, proxies=proxies).text
        else:
            if proxy == {}: get_ip()
            res = requests.post(url, headers=headers, data=data_param, timeout=40, proxies=proxy).text
    except:
        try:
            res = requests.post(url, headers=headers, data=data_param, timeout=40, proxies=proxy).text
        except:
            get_ip()
            res = requests.post(url, headers=headers, data=data_param, timeout=40, proxies=proxy).text

    # res = requests.post(driver.current_url, headers=headers, data=data_param).text
    content = json.loads(res, encoding='utf-8')
    # print(content)
    total_page = int(content['data']['pages'])
    driver.quit()
    return total_page


def f3(driver, url):
    driver.get(url)

    locator = (By.ID, "body")
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
    div = soup.find('div', id='body')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.alsggzyjy.cn/PublicServer/commonAnnouncementAction/getCommonAnnouncementList.do?000_2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_biangeng_gg",
     "http://www.alsggzyjy.cn/PublicServer/commonAnnouncementAction/getCommonAnnouncementList.do?001_2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.alsggzyjy.cn/PublicServer/commonAnnouncementAction/getCommonAnnouncementList.do?002_2",
     ["name", "ggstart_time", "href", "info"], f1, f2],



    ["gcjs_gqita_zhong_liu_gg",
     "http://www.alsggzyjy.cn/PublicServer/commonAnnouncementAction/getCommonAnnouncementList.do?003_2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    #
    ["zfcg_zhaobiao_gg",
     "http://www.alsggzyjy.cn/PublicServer/commonAnnouncementAction/getCommonAnnouncementList.do?006_1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://www.alsggzyjy.cn/PublicServer/commonAnnouncementAction/getCommonAnnouncementList.do?001_1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://www.alsggzyjy.cn/PublicServer/commonAnnouncementAction/getCommonAnnouncementList.do?003_1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_liubiao_gg",
     "http://www.alsggzyjy.cn/PublicServer/commonAnnouncementAction/getCommonAnnouncementList.do?007_1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_hetong_gg",
     "http://www.alsggzyjy.cn/PublicServer/commonAnnouncementAction/getCommonAnnouncementList.do?005_1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **kwargs):
    est_meta(conp, data=data, diqu="内蒙古自治阿拉善市", **kwargs)
    est_html(conp, f=f3, **kwargs)


if __name__ == "__main__":
    # url = "http://www.alsggzyjy.cn/PublicServer/commonAnnouncementAction/getCommonAnnouncementList.do?007_1"
    # driver = webdriver.Chrome()
    # driver.get(url)
    # print(f2(driver))
    # for i in range(1,20):
    # f1(driver,14)
    # print(f3(driver,
    #          'http://www.alsggzyjy.cn/PublicServer/public/commonAnnouncement/showDetail.html?businessType=2&id=827e5e2b-e015-452b-8182-94e2326ab895'))
    # # url = "http://zwzx.bynr.gov.cn/sunshineGov/list.shtml?columnId=402883f365a786900165a7ea6f700011&siteId=1&newsType=ggzyjy&pageNumber=1"
    # driver = webdriver.Chrome()
    # driver.get(url)
    # print(f2(driver))
    #
    work(conp=["postgres", "since2015", "192.168.3.171", "neimenggu", "alashan"],num=1,total=3)
