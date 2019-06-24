import datetime
import json
import random
import time

import pandas as pd
import re

import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zhulong2.util.fake_useragent import UserAgent

from zhulong2.util.etl import est_tbs, est_meta, est_html, est_gg


# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hengyang.gov.cn/jyxx/jsgc/zbgg_64796/index.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_='hunan_zhangjiajie'


def f1(driver,num):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    except:
        proxies={}
    ua=UserAgent()
    time.sleep(0.1)
    for i in range(1, int(len(PAGE)) + 1):
        if sum(PAGE[:i - 1]) < num <= sum(PAGE[:i]):
            num = num - sum(PAGE[:i - 1])

            headers = {
                "User-Agent": ua.chrome,
                "Referer": "http://www.ccgp-hunan.gov.cn/page/notice/more_city.jsp?noticeTypeID=prcmNotices&area_id=74",
                       }

            form_data = {
                "startDate": str(DATE[i]+datetime.timedelta(days=1)),
                "endDate": str(DATE[i - 1]),
                "page": num,
                "pageSize": 18,
                "area_id": 74,
            "areaCode": "zjjs",
            }

            url = "http://www.ccgp-hunan.gov.cn/mvc/getNoticeList4WebCity.do"

            time.sleep(random.random())
            req = requests.post(url, data=form_data, headers=headers, proxies=proxies, timeout=10)
            if req.status_code != 200:
                print(req.status_code)
                raise ValueError

            response = json.loads(req.text)

            contents = response['rows']

            data_=[]
            for content in contents:

                name = content.get('NOTICE_TITLE')
                address = content.get('AREA_NAME')
                ggstart_time = content.get('NEWWORK_DATE')
                gg_type = content.get('NOTICE_NAME')
                jy_type = content.get('PRCM_MODE_NAME')
                type = content.get('NOTICE_TYPE_NAME')
                org_name = content.get('DEPT_NAME')
                href = content.get('NOTICE_ID')
                src_code = content.get('SRC_CODE')

                if int(src_code) == 1:
                    href = "http://www.ccgp-hunan.gov.cn/page/notice/notice.jsp?noticeId=" + str(href)
                else:
                    href="http://www.ccgp-hunan.gov.cn/page/notice/notice.jsp?noticeId=" + str(href)+'&area_id=74'

                info = {'diqu': address, 'gg_type': gg_type + '|' + type, 'zbfs': jy_type, 'org_name': org_name}

                info = json.dumps(info, ensure_ascii=False)
                tmp = [name, ggstart_time, href, info]
                data_.append(tmp)

            is_useful = True
            break

    if 'is_useful' not in locals():
        print('页数不合法%d' % num)


    df=pd.DataFrame(data=data_)

    return df


def f2(driver):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    except:
        proxies={}
    global DATE
    global PAGE
    DATE=[]
    PAGE = []
    now_time = datetime.date.today()
    time_interval = datetime.timedelta(days=300)
    last_time = now_time - time_interval
    end_time = datetime.date(year=2015, month=1, day=1)
    date_list = []
    date_list.extend([now_time, last_time])
    while last_time > end_time:
        last_time -= time_interval
        date_list.append(last_time)
    DATE=date_list.copy()

    while len(date_list) > 1:
        form_data = {
            "startDate": str(date_list[1]+datetime.timedelta(days=1)),
            "endDate": str(date_list[0]),
            "page": 1,
            "pageSize": 18,
            "area_id": 74,
            "areaCode": "zjjs",
        }

        url = "http://www.ccgp-hunan.gov.cn/mvc/getNoticeList4WebCity.do"

        req = requests.post(url, data=form_data,proxies=proxies)
        content = json.loads(req.text)

        count_num = int(content['total'])
        page_count = count_num // 18 + 1 if count_num % 18 else count_num // 18

        PAGE.append(page_count)
        date_list = date_list[1:]
    total=sum(PAGE)

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//iframe[@id='content']")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    driver.switch_to.frame("content")
    locator = (By.XPATH, '//body[string-length()>10]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

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

    page1 = driver.page_source
    soup1 = BeautifulSoup(page1, 'html.parser')
    div1 = soup1.find('body')

    driver.switch_to.parent_frame()
    page2 = driver.page_source
    soup2 = BeautifulSoup(page2, 'html.parser')
    div2 = soup2.find('div', class_='relevant_notice')
    div = BeautifulSoup(str(div1) + str(div2), 'html.parser')
    if 'IP已经过了有效期' in str(div):
        raise ValueError

    return div



data=[

    ["zfcg_gqita_gg","http://www.ccgp-hunan.gov.cn/page/notice/more_city.jsp?noticeTypeID=prcmNotices&area_id=74",
     ["name", "ggstart_time", "href", 'info'], f1, f2],

]

def work(conp,**args):
    est_meta(conp,data=data,diqu="湖南省张家界市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","lch","hunan_zhangjiajie"]

    work(conp=conp,pageloadtimeout=120,cdc_total=20)