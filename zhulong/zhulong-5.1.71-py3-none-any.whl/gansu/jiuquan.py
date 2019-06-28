import math
from pprint import pprint

import pandas as pd
import re
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
from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html
from zhulong.util.fake_useragent import UserAgent
from zhulong.util.etl import add_info
import json
from collections import OrderedDict
import requests
import random

_name_ = 'jiuquan'


def f1(driver, num):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        if proxies_chromeOptions:
            proxy = proxies_chromeOptions[0].split('=')[1]
            proxies = {'http': '%s' % proxy}
        else:
            proxies = {}
    except:
        proxies = {}

    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        # 'User-Agent': user_agent,
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        "Referer": "http://www.ggzyjypt.com.cn/jyxxgk/008002/tradelist.html",
        "Host": "www.ggzyjypt.com.cn",

    }
    payloadData = {
        "pageIndex": str(num),
        "pageSize": 20,
        "searchTitle": "",

    }
    Data = dict(payloadData, **d_dict)

    # 下载超时
    timeOut = 60
    time.sleep(0.5 + random.random())
    res = requests.post(
        url=start_url,
        headers=headers,
        data=Data,
        proxies=proxies,
        timeout=timeOut)
    # 需要判断是否为登录后的页面
    if res.status_code != 200:
        raise ConnectionError
    data = []
    html_data = res.text
    soup = json.loads(html_data)
    custom = soup['custom']
    custom = json.loads(custom)
    Table = custom.get('Table')

    if Table:
        for li in Table:
            title = li.get('title')
            ggstart_time = li.get('infodate')
            href = 'http://www.ggzyjypt.com.cn/' + li.get('href')
            info = {'gglx': li.get('categoryname')}
            info = json.dumps(info, ensure_ascii=False)
            tmp = [title, ggstart_time, href, info]

            data.append(tmp)
    else:
        Table = custom.get('dataList')
        for li in Table:
            title = li.get('annoTitle')
            ggstart_time = li.get('publishDate')
            href = li.get('detailUrl')
            info = None

            tmp = [title, ggstart_time, href, info]



            data.append(tmp)



    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    global start_url, d_dict
    start_url = None
    url = driver.current_url
    d_dict = {}
    if 'getZtbGgList' in url:
        val_list = url.rsplit('/', maxsplit=2)
        start_url = val_list[0]
        categorynum = val_list[1]
        diqu = val_list[2]
        if categorynum:
            d_dict['categorynum'] = categorynum
        if diqu:
            d_dict['diqu'] = diqu
    else:
        start_url = url



    num = get_pageall(start_url, d_dict)
    driver.quit()

    return int(num)


def get_pageall(start_url, d_dict):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        if proxies_chromeOptions:
            proxy = proxies_chromeOptions[0].split('=')[1]
            proxies = {'http': '%s' % proxy}
        else:
            proxies = {}
    except BaseException:
        proxies = {}

    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        "Referer": "http://www.ggzyjypt.com.cn/jyxxgk/008001/tradelist.html",
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': user_agent,

    }
    payloadData = {
        "pageIndex": 1,
        "pageSize": 20,
        "searchTitle":"",
    }




    Data = dict(payloadData, **d_dict)

    time.sleep(0.5 + random.random())
    res = requests.post(
        url=start_url,
        headers=headers,
        data=Data,
        proxies=proxies,
        timeout=40)
    # 需要判断是否为登录后的页面
    if res.status_code != 200:
        raise ConnectionError

    html_data = res.text
    soup = json.loads(html_data)
    custom = soup['custom']
    custom = json.loads(custom)

    RowCount = custom.get('RowCount')
    if not RowCount:
        RowCount = custom.get('totalCount')

    if not RowCount:
        RowCount = 0

    num = math.ceil(int(RowCount) / 20)

    return num


def f3_wait(driver):

    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 5:
            break
def f4(driver,num):
    locator=(By.XPATH,'//ul[@id="showList"]/li[1]//a')
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//span[@class="current pageIdx"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum=int(driver.find_element_by_xpath('//span[@class="current pageIdx"]').text)
    if cnum!=num:
        val=driver.find_element_by_xpath('//ul[@id="showList"]/li[1]//a').get_attribute('href')[-20:]

        search_button = driver.find_element_by_xpath('//input[@class="pg_num_input"]')
        driver.execute_script("arguments[0].value = '%s';" % num, search_button)
        click_button = driver.find_element_by_xpath('//a[@class="pg_gobtn"]')
        driver.execute_script("arguments[0].click()", click_button)

        locator = (
            By.XPATH, "//ul[@id='showList']/li[1]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page=driver.page_source
    soup=BeautifulSoup(page,'html.parser')
    div=soup.find("ul",id="showList")

    dls=div.find_all("li")
    data=[]
    for dl in dls:
        name=dl.find('a')['title']
        href=dl.find('a')['href']
        ggstart_time=dl.find('span',class_='wb-data-date').get_text()
        if 'http' in href:
            href=href
        else:
            href='http://www.ggzyjypt.com.cn'+href
        tmp=[name,ggstart_time,href]

        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df

def f5(driver):
    locator = (By.XPATH, '//ul[@id="showList"]/li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//span[@class="current pageIdx"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total=driver.find_element_by_xpath('//span[@class="pg_maxpagenum"]').text
    total=re.findall('/(\d+)',total)[0]
    driver.quit()

    return int(total)

def f3(driver, url):
    driver.get(url)
    locator = (
        By.XPATH,
        "//div[@class='fnews-article'][string-length()>50] | //div[@id='a'][string-length()>100] | //div[@class='news-article'][string-length()>50]")
    WebDriverWait(
        driver, 10).until(
        EC.presence_of_all_elements_located(locator))

    f3_wait(driver)

    # f3 情况1
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_='fnews-article')
    if not div:
        div = soup.find('div', class_='tabbd clearfix')
        if not div:
            div = soup.find('div', class_='news-article')

    return div


def get_data():
    data = []
    ss = OrderedDict([("市本级", "620901"), ("敦煌市", "620982"), ("金塔县", "620921"), ("瓜州县", "620922"), ("肃州区", "620925"),
                      ("玉门市", "620981"), ("肃北蒙古族自治县", "620923"), ("阿克塞哈萨克族自治县", "620924")])

    # 工程建设部分
    for w1 in ss.keys():
        categorynum = '008001'
        href = "http://www.ggzyjypt.com.cn/EpointWebBuilder_jqggzy/getGgListAction.action?cmd=getZtbGgList/%s/%s" % (
            categorynum, ss[w1])
        tb = "gcjs_gqita_diqu%s_gg" % (ss[w1])
        col = ["name", "ggstart_time", "href", "info"]
        tmp = [tb, href, col, add_info(f1, {"diqu": w1}), f2]
        data.append(tmp)
    #
    # # 政府采购部分
    for w2 in ss.keys():
        categorynum = '008002'
        href = "http://www.ggzyjypt.com.cn/EpointWebBuilder_jqggzy/getGgListAction.action?cmd=getZtbGgList/%s/%s" % (
            categorynum, ss[w2])
        tb = "zfcg_gqita_diqu%s_gg" % (ss[w2])
        col = ["name", "ggstart_time", "href", "info"]
        tmp = [tb, href, col, add_info(f1, {"diqu": w2}), f2]
        data.append(tmp)

    # # 重大项目部分
    for w2 in ss.keys():
        categorynum = '008008'
        href = "http://www.ggzyjypt.com.cn/EpointWebBuilder_jqggzy/getGgListAction.action?cmd=getZtbGgList/%s/%s" % (
            categorynum, ss[w2])
        tb = "gcjs_gqita_diqu%s_zdxm_gg" % (ss[w2])
        col = ["name", "ggstart_time", "href", "info"]
        tmp = [tb, href, col, add_info(f1, {"diqu": w2, 'xmlx': '重大项目'}), f2]
        data.append(tmp)

    # 政府采购协议供货部分
    t = [

        ["gcjs_gqita_xianeyixia_gg", "http://www.ggzyjypt.com.cn/jyxxgk/008009/tradelist.html",
         ["name", "ggstart_time", "href", "info"], add_info(f4, {'xmlx': '限额以下'}), f5],

        ["zfcg_gqita_xianeyixia_gg", "http://www.ggzyjypt.com.cn/jyxxgk/008010/tradelist.html",
         ["name", "ggstart_time", "href", "info"], add_info(f4, {'xmlx': '限额以下'}), f5]
    ]
    data.extend(t)

    data1 = data.copy()
    # remove_arr = []
    # for w in data:
    #     if w[0] in remove_arr: data1.remove(w)
    return data1
    # 创建data


data = get_data()
# pprint(data)


# f3 为全流程



def work(conp, **args):
    est_meta(conp, data=data, diqu="甘肃省酒泉市", **args)
    # est_html(conp, f=f3, **args)


if __name__ == "__main__":
    work(
        conp=[
            "postgres",
            "since2015",
            '192.168.3.171',
            "gansu",
            "jiuquan"],
        num=10,
        )
