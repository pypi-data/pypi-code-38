import random
import pandas as pd
import re
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write,db_command,db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import json
from zhulong.util.etl import add_info,est_meta,est_html,est_tbs
from zhulong.util.fake_useragent import UserAgent


_name_="jianou"



def f1_requests(datas, start_url, s=0):
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'User-Agent': user_agent,
    }
    res = requests.get(url=start_url, headers=headers, data=datas)
    # 需要判断是否为登录后的页面
    if res.status_code == 200:
        html = res.text
        if html:
            html = json.loads(html)
            datalist = html["data"]
            data_list = []
            for data in datalist:
                if s == 3:
                    title = data['TITLE']
                    td = data['TM']
                    link = "http://www.joztb.com/views/tradeCenter/jianou/trade.html?id="+data['ID']+"&type=articles&ons=%E4%B9%A1%E9%95%87%E6%8B%9B%E6%A0%87"
                    try:
                        yw_type = data['TYPE_NAME']
                    except:
                        yw_type = ''
                    info = json.dumps({'yw_type': yw_type}, ensure_ascii=False)
                    tmp = [title, td, link, info]
                    data_list.append(tmp)
                else:
                    title = data['NAME']
                    td = data['PUBLISHED_TIME']
                    link = data['URL']
                    if s == 2:
                        link = link.strip() + "/zhongbiaogg"
                    try:
                        diqu = data['AREANAME']
                    except:
                        diqu = ''
                    try:
                        yw_type = data['BIG_TYPE_TEXT']
                    except:
                        yw_type = ''
                    try:
                        hy_type = data['TYPE_TEXT']
                    except:
                        hy_type = ''
                    info = json.dumps({'diqu':diqu, 'yw_type':yw_type, 'hy_type':hy_type}, ensure_ascii=False)
                    tmp = [title, td, link, info]
                    data_list.append(tmp)
            df = pd.DataFrame(data_list)
            return df



def f1(driver, num):
    url = driver.current_url
    if "type=%E6%8B%9B%E6%A0%87%E5%85%AC%E5%91%8A" in url:
        datas = {
            'method': 'Web.GetJiaoYiList',
            'pageindex': '{}'.format(num),
            'pagesize': '15',
            'BIG_TYPE': 'A',
            'NAME': '',
            'TYPE': '',
            'AREA_CODE': '35',
            'PUBLISHED_TIME_START': '2016-11-01',
            'PUBLISHED_TIME_END': '',
            'STATUS': '',
        }
        start_url = "http://www.enjoy5191.com:9001/api/GetDataHandler.ashx?PLATFORM_CODE=E3507837011"
        df = f1_requests(datas, start_url, s=1)
        return df

    elif "type=%E4%B8%AD%E6%A0%87%E5%85%AC%E7%A4%BA" in url:
        datas = {
            'method': 'Web.GetJiaoYiList',
            'pageindex': '{}'.format(num),
            'pagesize': '15',
            'BIG_TYPE': '',
            'NAME': '',
            'TYPE': '',
            'AREA_CODE': '',
            'PUBLISHED_TIME_START': '',
            'PUBLISHED_TIME_END': '',
            'STATUS': '',
            'in_status': '3,4'
        }
        start_url = "http://www.enjoy5191.com:9001/api/GetDataHandler.ashx?PLATFORM_CODE=E3507837011"
        df = f1_requests(datas, start_url, s=2)
        return df

    else:
        datas = {
            'method':'Web.GetNewsList',
            'in_type':'73e4fff0-9a96-42d9-8300-542d29c22b06',
            'pageindex': '{}'.format(num),
            'pagesize':'15',
            'TITLE':'',
            'CREATE_TM_START':'1900-01-01',
            'CREATE_TM_END':'',
        }
        start_url = "http://www.enjoy5191.com:9001/api/GetDataHandler.ashx?PLATFORM_CODE=E3507837011"
        df = f1_requests(datas, start_url, s=3)
        return df


def f2_requests(data, start_url):
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'User-Agent': user_agent,
    }
    res = requests.get(url=start_url, headers=headers, data=data)
    # 需要判断是否为登录后的页面
    if res.status_code == 200:
        html = res.text
        if html:
            html = json.loads(html)
            total = html["total"]
            if total/15 == int(total/15):
                page_all = int(total/15)
            else:
                page_all = int(total/15) + 1
            return page_all



def f2(driver):
    url = driver.current_url
    if "type=%E6%8B%9B%E6%A0%87%E5%85%AC%E5%91%8A" in url:
        data = {
            'method': 'Web.GetJiaoYiList',
            'pageindex': '1',
            'pagesize': '15',
            'BIG_TYPE': 'A',
            'NAME': '',
            'TYPE': '',
            'AREA_CODE': '35',
            'PUBLISHED_TIME_START': '2016-11-01',
            'PUBLISHED_TIME_END': '',
            'STATUS': '',
        }
        start_url = "http://www.enjoy5191.com:9001/api/GetDataHandler.ashx?PLATFORM_CODE=E3507837011"
        num_total = f2_requests(data, start_url)
        driver.quit()
        return int(num_total)

    if "type=%E4%B9%A1%E9%95%87%E6%8B%9B%E6%A0%87" in url:
        locator = (By.XPATH, "//*[contains(text(),'非电子标')]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
    try:
        locator = (By.XPATH, "//span[@class='pageInfo']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num_total = re.findall(r'(\d+)', str)[0]
    except:
        num_total = 1

    driver.quit()
    return int(num_total)



def f3(driver, url):
    if "/zhongbiaogg" in url:
        url = url.rsplit('/', maxsplit=1)[0]
        driver.get(url)
        try:
            locator = (By.XPATH, "(//*[contains(text(),'中标公示')])[1]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        except:
            locator = (By.XPATH, "(//*[contains(text(),'中标公告')])[1]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()

        locator = (By.XPATH, "//iframe[@class='myFrame'] | //iframe[@id='ifrEdit'] | //iframe[@id='myFrame']")
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
        try:
            dd = driver.find_element_by_xpath("//iframe[@class='myFrame'] | //iframe[@id='myFrame']")
        except:
            dt = driver.find_element_by_xpath("//iframe[@id='ifrEdit']")
            driver.switch_to_frame(dt)
            locator = (By.XPATH, "//iframe[@id='ifrEdit1']")
            WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
            dd = driver.find_element_by_xpath("//iframe[@id='ifrEdit1']")
        driver.switch_to_frame(dd)
        time.sleep(2)
        locator = (By.XPATH, "//div[@class='bodys viewsbodys'][string-length()>15] | //div[@class='bidderPublic'][string-length()>15] |　//embed[@id='plugin'] | //div[@class='wrap'][string-length()>15]")
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
        time.sleep(1)
        before = len(driver.page_source)
        time.sleep(0.5)
        after = len(driver.page_source)
        i = 0
        while before != after:
            before = len(driver.page_source)
            time.sleep(0.5)
            after = len(driver.page_source)
            i += 1
            if i > 5: break
        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        div = soup.find('div', class_='bodys viewsbodys')
        if div == None:
            div = soup.find('div', class_='bidderPublic')
            if div == None:
                div = soup.find('div', class_='wrap')
                if div == None:
                    div = soup.find('embed', id='plugin')['src']
        return div

    elif 'http://www.joztb.com/views/tradeCenter/jianou/trade.html' in url:
        driver.get(url)
        locator = (By.XPATH, "//div[@class='md-content'][string-length()>15]")
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
        before = len(driver.page_source)
        time.sleep(1)
        after = len(driver.page_source)
        i = 0
        while before != after:
            before = len(driver.page_source)
            time.sleep(1)
            after = len(driver.page_source)
            i += 1
            if i > 5: break
        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        div = soup.find('div', class_='md-content')
        return div

    driver.get(url)
    locator = (By.XPATH, "//iframe[@class='myFrame'] | //iframe[@id='ifrEdit'] | //iframe[@id='myFrame']")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    try:
        dd = driver.find_element_by_xpath("//iframe[@class='myFrame'] | //iframe[@id='myFrame']")
    except:
        dt = driver.find_element_by_xpath("//iframe[@id='ifrEdit']")
        driver.switch_to_frame(dt)
        locator = (By.XPATH, "//iframe[@id='ifrEdit1']")
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
        dd = driver.find_element_by_xpath("//iframe[@id='ifrEdit1']")
    driver.switch_to_frame(dd)
    time.sleep(2)
    locator = (By.XPATH, "//div[@class='view'][string-length()>15] |　//embed[@id='plugin'] | //div[@class='wrap'][string-length()>15]")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    before = len(driver.page_source)
    time.sleep(1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(1)
        after = len(driver.page_source)
        i += 1
        if i > 5: break

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_='view')
    if div == None:
        div = soup.find('div', class_='wrap')
        if div == None:
            div = soup.find('embed', id='plugin')['src']
    return div



data = [
    ["gcjs_zhaobiao_gg",
     "http://www.joztb.com/views/tradeCenter/jianou/trade.html?type=%E6%8B%9B%E6%A0%87%E5%85%AC%E5%91%8A",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiao_gg",
     "http://www.joztb.com/views/tradeCenter/jianou/trade.html?type=%E4%B8%AD%E6%A0%87%E5%85%AC%E7%A4%BA",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_zhao_zhong_liu_bu_xiangzhen_gg",
     "http://www.joztb.com/views/tradeCenter/jianou/trade.html?type=%E4%B9%A1%E9%95%87%E6%8B%9B%E6%A0%87",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp,**args):
    est_meta(conp,data=data,diqu="福建省建瓯市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.4.175","fujian","jianou"])


    # driver=webdriver.Chrome()
    # url = "http://www.joztb.com/views/tradeCenter/jianou/trade.html?type=%E4%B9%A1%E9%95%87%E6%8B%9B%E6%A0%87"
    # driver.get(url)
    # # d = f3(driver, url)
    # # print(d)
    # df = f2(driver)
    # print(df)
    # driver = webdriver.Chrome()
    # url = "http://www.joztb.com/views/tradeCenter/jianou/trade.html?type=%E4%B9%A1%E9%95%87%E6%8B%9B%E6%A0%87"
    # driver.get(url)
    # for i in range(3, 5):
    #     df=f1(driver, i)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver,f)
    #         print(d)
