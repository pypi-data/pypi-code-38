import random
from urllib.parse import unquote

import pandas as pd
import re

import requests
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
from zhulong3.util.fake_useragent import UserAgent
import json

import time

from zhulong3.util.etl import est_html, est_meta, add_info



_name_ = "sichuan_chengdu"


def f1(driver, num):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s'% proxy}
    except:
        proxies = ''
    url = driver.current_url
    start_url = 'http://tz.chengdu.com.cn/zftz/newweb/AjaxProcess/IndexPageHandler.ashx'
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': user_agent,
    }
    requestType = re.findall(r'requestType=(.*)&', url)[0]
    searchKey = re.findall(r'searchKey=(.*)', url)[0]
    Data = {
        "requestType": requestType,
        "pageIndex": num,
        "pageSize": 31,
        "areaCode": "",
        "type": "",
        "searchKey": unquote(searchKey),
    }
    # 下载超时
    timeOut = 60
    if proxies:
        res = requests.post(url=start_url, headers=headers, data=Data, proxies=proxies, timeout=timeOut)
    else:
        res = requests.post(url=start_url, headers=headers, data=Data, timeout=timeOut)
    # 需要判断是否为登录后的页面
    if res.status_code == 200:
        html = res.text
        html_data = json.loads(html)
        tables = html_data['tables']
        if requestType == 'getXMXX':
            lis = tables['xmxxTable']
        elif requestType == 'getXMSPXX':
            lis = tables['xmspxxTable']
        elif requestType == 'getXMZTBXX':
            lis = tables['xmztbxxTable']
        elif requestType == 'getXMJGYSXX':
            lis = tables['xmjgysxxTable']
        data = []
        for li in lis:
            title = li['XMMC']
            span = li['FBSJ']
            if requestType == 'getXMZTBXX':
                href = 'http://tz.chengdu.com.cn/Zftz/NewWeb/XMXXDetail.aspx?itemID=' + li['FKXMSPID']
            elif requestType == 'getXMJGYSXX':
                href = 'http://tz.chengdu.com.cn/Zftz/NewWeb/XMXXDetail.aspx?itemID=' + li['FKXMSPID']
            else:
                href = 'http://tz.chengdu.com.cn/Zftz/NewWeb/XMXXDetail.aspx?itemID=' + li['ID']
            tmp = [title, span, href]
            data.append(tmp)
        df = pd.DataFrame(data=data)
        df['info'] = None
        return df


def f2(driver):
    url = driver.current_url
    start_url = 'http://tz.chengdu.com.cn/zftz/newweb/AjaxProcess/IndexPageHandler.ashx'
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': user_agent,
    }
    requestType = re.findall(r'requestType=(.*)&', url)[0]
    searchKey = re.findall(r'searchKey=(.*)', url)[0]
    Data = {
        "requestType": requestType,
        "pageIndex": 1,
        "pageSize": 31,
        "areaCode": "",
        "type": "",
        "searchKey": unquote(searchKey),
    }
    # 下载超时
    timeOut = 60
    res = requests.post(url=start_url, headers=headers, data=Data, timeout=timeOut)
    # 需要判断是否为登录后的页面
    if res.status_code == 200:
        html = res.text
        html_data = json.loads(html)
        recordCount = html_data['recordCount']
        if int(recordCount)/31 == int(int(recordCount)/31):
            num = int(int(recordCount)/31)
        else:
            num = int(int(recordCount)/31) + 1
    driver.quit()
    return num


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='MainBody_divXMXXExist']")
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
    div = soup.find('div', id='MainBody_divXMXXExist')
    # div=div.find_all('div',class_='ewb-article')[0]
    return div


data = [

    ["gcjs_yucai_lixiang_gg",
     "http://tz.chengdu.com.cn/zftz/newweb/AjaxProcess/IndexPageHandler.ashx/requestType=getXMXX&searchKey=立项文号/项目编码/项目名称/业主",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gglx':'项目立项信息'}), f2],
    #
    ["gcjs_yucai_shenpi_gg",
     "http://tz.chengdu.com.cn/zftz/newweb/AjaxProcess/IndexPageHandler.ashx/requestType=getXMSPXX&searchKey=立项文号/项目编码/项目名称/业主",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gglx':'项目审批信息'}), f2],
    #
    ["gcjs_gqita_zhao_zhong_gg",
     "http://tz.chengdu.com.cn/zftz/newweb/AjaxProcess/IndexPageHandler.ashx/requestType=getXMZTBXX&searchKey=立项文号/项目编码/项目名称/业主/标段名称/招投标标号",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gglx':'招投标信息'}), f2],
    #
    ["gcjs_yanshou_gg",
     "http://tz.chengdu.com.cn/zftz/newweb/AjaxProcess/IndexPageHandler.ashx/requestType=getXMJGYSXX&searchKey=立项文号/项目编码/项目名称/业主",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="四川省成都市", **args)
    est_html(conp, f=f3, **args)

# 网址变更
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang2", "sichuan_chengdu"])

    # driver = webdriver.Chrome()
    # url = "http://tz.chengdu.com.cn/zftz/newweb/AjaxProcess/IndexPageHandler.ashx/requestType=getXMXX&searchKey=立项文号/项目编码/项目名称/业主"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    #
    # driver=webdriver.Chrome()
    # url = "http://tz.chengdu.com.cn/zftz/newweb/AjaxProcess/IndexPageHandler.ashx/requestType=getXMJGYSXX&searchKey=立项文号/项目编码/项目名称/业主"
    # driver.get(url)
    # for i in range(1, 6):
    #     df=f1(driver, i)
    #     print(df.values)
