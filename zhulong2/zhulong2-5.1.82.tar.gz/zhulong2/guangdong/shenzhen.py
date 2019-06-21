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

_name_ = "guangdong_shenzhen"


def f1_data(driver, num):
    locator = (By.XPATH, "//ul[@class='list']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='total']/em[last()]")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(str)
    except:
        cnum = 1
    url = driver.current_url
    if num != cnum:
        val = driver.find_element_by_xpath("//ul[@class='list']/li[1]/a").get_attribute('href')[-20:]
        driver.find_element_by_xpath("//input[@id='num']").send_keys(num)
        driver.find_element_by_xpath("//input[@type='button']").click()
        locator = (By.XPATH, "//ul[@class='list']/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("ul", class_="list")
    trs = div.find_all("li")
    data = []
    for tr in trs:
        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        td = tr.find('span').text.strip()
        href = a['href'].strip()
        id = href.split('/', maxsplit=1)[1]
        if "fgkzbfssqgs" in url:
            link = 'http://www.cgzx.sz.gov.cn/xxgk/zfcg/fgkzbfssqgs/' + id
        elif "lyqkcj" in url:
            link = 'http://www.cgzx.sz.gov.cn/xxgk/zfcg/lyqkcj/' + id
        tmp = [title, td, link]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f1(driver, num):
    url = driver.current_url
    if 'http://www.cgzx.sz.gov.cn/xxgk/zfcg' in url:
        df = f1_data(driver, num)
        return df
    else:
        locator = (By.XPATH, "//tbody[@class='tableBody']/tr[1]/td/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, "//select[@name='__ec_pages']/option[@selected='selected']")
            str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            cnum = int(str)
        except:
            cnum = 1

        if num != cnum:
            val = driver.find_element_by_xpath("//tbody[@class='tableBody']/tr[1]/td/a").get_attribute('href')[-12:]

            selector = Select(driver.find_element_by_xpath("//select[@name='__ec_pages']"))
            selector.select_by_value('{}'.format(num))

            locator = (By.XPATH, "//tbody[@class='tableBody']/tr[1]/td/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        page = driver.page_source
        soup = BeautifulSoup(page, "html.parser")
        div = soup.find("tbody", class_="tableBody")
        trs = div.find_all("tr")
        data = []
        for tr in trs:
            a = tr.find('a')
            title = a.text.strip()
            td = tr.find_all('td')[-1].text.strip()
            href = a['href'].strip()
            id = re.findall(r'id=(.*)', href)[0]
            link = 'http://www.szzfcg.cn/portal/documentView.do?method=view&id=' + id
            info = {}
            if tr.find_all('td')[-2]:
                lx = tr.find_all('td')[-2].text.strip()
                if lx: info['lx'] = lx
            if info:
                info = json.dumps(info, ensure_ascii=False)
            else:
                info = None
            tmp = [title, td, link, info]
            data.append(tmp)
        df = pd.DataFrame(data=data)
        return df


def f2(driver):
    url = driver.current_url
    if 'http://www.cgzx.sz.gov.cn/xxgk/zfcg' in url:
        locator = (By.XPATH, "//ul[@class='list']/li[1]/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, "//div[@class='total']/span[1]")
            str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            page_all = int(str)
        except:
            page_all = 1
        driver.quit()
        return page_all
    else:
        locator = (By.XPATH, "//tbody[@class='tableBody']/tr[1]/td/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, "//select[@name='__ec_pages']/option[last()]")
            str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            page_all = int(str)
        except:
            page_all = 1
        driver.quit()
        return page_all


def f3(driver, url):
    driver.get(url)
    try:
        locator = (By.XPATH,
                   "//table[@id='bulletinContent'][string-length()>10] | //div[@class='main_con'][string-length()>10] | //div[@align='center'][string-length()>10] | //table[@align='center'][string-length()>10]")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        flag = 3
    except:
        try:
            flag = 1
            locator = (By.XPATH,
                       "//div[@class='xl-right'][string-length()>10] | //table[@id='tab'][string-length()>10]　|　//table[@width='98%' and @align='center'][string-length()>10] | //table[@width='100%' and @align='center'][string-length()>10] | //div[@class='box'][string-length()>10]")
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        except:
            flag = 2
            locator = (
            By.XPATH, "//span[@id='holder'][string-length()>10] | //p[@class='MsoNormal'][string-length()>10]")
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
    if flag == 3:
        div = soup.find('table', attrs={'align': 'center'})
        if div == None:
            div = soup.find('div', class_='main_con')
            if div == None:
                div = soup.find('div', attrs={'align': 'center'})
    elif flag == 1:
        div = soup.find('div', class_='xl-right')
        if div == None:
            div = soup.find('table', id='tab')
            if div == None:
                div = soup.find('table', attrs={'width': '98%', 'align': 'center'})
                if div == None:
                    div = soup.find('table', attrs={'width': '100%', 'align': 'center'})
                    if div == None:
                        div = soup.find('div', class_='box')
    else:
        div = soup.find('body')
    return div


data = [
    ["zfcg_yucai_gg", "http://www.szzfcg.cn/portal/topicView.do?method=view&id=2719966",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhaobiao_shiji_gg", "http://www.szzfcg.cn/portal/topicView.do?method=view&id=1660&agencyType=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],

    ["zfcg_zhaobiao_quji_gg", "http://www.szzfcg.cn/portal/topicView.do?method=view&id=1660&agencyType=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '区级'}), f2],
    #
    ["zfcg_zhongbiao_shiji_gg", "http://www.szzfcg.cn/portal/topicView.do?method=view&id=2014&agencyType=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],
    #
    ["zfcg_zhongbiao_quji_gg", "http://www.szzfcg.cn/portal/topicView.do?method=view&id=2014&agencyType=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '区级'}), f2],
    #
    ["zfcg_yucai_fgkzb_gg", "http://www.cgzx.sz.gov.cn/xxgk/zfcg/fgkzbfssqgs/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '非公开招标', 'gglx': '非公开招标方式申请公示'}), f2],
    #
    ["zfcg_yanshou_gg", "http://www.cgzx.sz.gov.cn/xxgk/zfcg/lyqkcj/",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '履约情况现场抽检'}), f2],
    #
    ["zfcg_zhaobiao_zxcg_gg", "http://www.szzfcg.cn/portal/topicView.do?method=view&id=518010",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '自行采购'}), f2],
    #
    ["zfcg_zhongbiao_zxcg_gg", "http://www.szzfcg.cn/portal/topicView.do?method=view&id=518014",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '自行采购'}), f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省深圳市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "shenzhen"])
    #
    # driver=webdriver.Chrome()
    # url = "http://www.szzfcg.cn/portal/topicView.do?method=view&id=2014&agencyType=2"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    # driver=webdriver.Chrome()
    # url = "http://www.szzfcg.cn/portal/topicView.do?method=view&id=2014&agencyType=2"
    # driver.get(url)
    # for i in range(3, 5):
    #     df=f1(driver, i)
    #     print(df.values)
    #     for i in df[2].values:
    #         f = f3(driver, i)
    #         print(f)
