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

_name_ = "guangxi_qinzhou"

start_url = None
gg_name = None


def f1_data(driver, num):
    locator = (By.XPATH, "//table[@id='content_DataTable']/tbody[2]/tr/td[3]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        cnum = int(re.findall(r'pnum=(\d+)&', start_url)[0])
    except:
        cnum = 1
    if num != cnum:
        val = driver.find_element_by_xpath("//table[@id='content_DataTable']/tbody[2]/tr/td[3]/a").get_attribute(
            'onclick')
        val = re.findall(r"\('\.(.*)','_blank'\)", val)[0]
        if num == 1:
            url = re.sub("pnum=[0-9]*", "pnum=1", start_url)
        else:
            s = "pnum=%d" % (num) if num > 1 else "pnum=1"
            url = re.sub("pnum=[0-9]*", s, start_url)
        driver.get(url)
        locator = (
        By.XPATH, "//table[@id='content_DataTable']/tbody[2]/tr/td[3]/a[not(contains(@onclick, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("table", id="content_DataTable")
    lis = div.find_all('tbody')
    data = []
    for tr in lis[1:]:
        td1 = tr.find_all('td')[2]
        a1 = td1.find('a')
        ### 获取成交结果和竞价情况的html代码
        td2 = tr.find_all('td')[6]
        try:
            a2 = td2.find_all('a')[0]
            a3 = td2.find_all('a')[1]
        except:
            # 报错是因为有一项没有，现在就该找出是哪项没有
            try:
                span1 = td2.find('span').text.strip()
                if span1 == '成交结果':
                    a2 = td2.find_all('a')[0]
                    a3 = None
                else:
                    a3 = td2.find_all('a')[0]
                    a2 = None
            except:
                continue

        try:
            title = a1['title'].strip()
        except:
            title = a1.text.strip()
        td = tr.find_all('td', align="center")[-1].text.strip()
        try:
            info = {'info_html': '{}'.format(tr)}
            info = json.dumps(info, ensure_ascii=False)
        except:
            info = None
        if gg_name == 'zhaobiao':
            link = re.findall(r"\('\.(.*)','_blank'\)", a1['onclick'].strip())[0]
            link = 'http://zfcg.qzzfcg.cn' + link
        elif gg_name == 'zhongbiao':
            try:
                if a2 == None:
                    continue
                link = re.findall(r"\('\.(.*)','_blank'\)", a2['onclick'].strip())[0]
                link = 'http://zfcg.qzzfcg.cn' + link
            except:
                link = '-'
        elif gg_name == 'jingjiajieguo':
            try:
                if a3 == None:
                    continue
                link = re.findall(r"\('\.(.*)','_blank'\)", a3['onclick'].strip())[0]
                link = 'http://zfcg.qzzfcg.cn' + link
            except:
                link = '-'

        tmp = [title, td, link, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f1(driver, num):
    url = driver.current_url
    if 'http://zfcg.qzzfcg.cn/' in url:
        df = f1_data(driver, num)
        return df
    else:
        locator = (By.XPATH, "//li[@class='xx']/ol[@class='list'][1]/li/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, "//ol[@class='pages']/a[@class='current']")
            str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            cnum = int(str)
        except:
            cnum = 1

        url = driver.current_url
        if num != cnum:
            val = driver.find_element_by_xpath("//li[@class='xx']/ol[@class='list'][1]/li/a").get_attribute('href')[-6:]
            if '&page' not in url:
                s = "&page=%d" % (num) if num > 1 else "&page=1"
                url += s
            elif num == 1:
                url = re.sub("page=[0-9]*", "page=1", url)
            else:
                s = "page=%d" % (num) if num > 1 else "page=1"
                url = re.sub("page=[0-9]*", s, url)
                # print(cnum)
            driver.get(url)
            locator = (By.XPATH, "//li[@class='xx']/ol[@class='list'][1]/li/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        page = driver.page_source
        soup = BeautifulSoup(page, "html.parser")
        div = soup.find("li", class_='xx')
        lis = div.find_all('ol', class_='list')
        data = []
        for tr in lis:
            a = tr.find('a')
            try:
                title = a['title'].strip()
            except:
                title = a.text.strip()
            td = tr.find('li', class_="xd").text.strip()
            td = re.findall(r'\[(.*)\]', td)[0]
            link = a['href'].strip()
            tmp = [title, td, link]
            data.append(tmp)
        df = pd.DataFrame(data=data)
        df['info'] = None
        return df


def f2(driver):
    url = driver.current_url
    if 'http://zfcg.qzzfcg.cn/' in url:
        global gg_name, start_url
        gg_name = None
        gg_name = url.rsplit('/', maxsplit=1)[1]
        start_url = url.rsplit('/', maxsplit=1)[0]
        locator = (By.XPATH, "//table[@id='content_DataTable']/tbody[2]/tr/td[3]/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, "//table[@width='100%'][1]//font[3]")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = int(str)
        driver.quit()
        return num
    else:
        locator = (By.XPATH, "//li[@class='xx']/ol[@class='list'][1]/li/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, "//ol[@class='pages']")
            str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            num = int(re.findall(r'(\d+)', str)[1])
        except:
            num = 1
        driver.quit()
        return num


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='qzsz_nav'][string-length()>10] | //div[@id='content_Body'][string-length()>10]")
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
    div = soup.find('div', class_='qzsz_nav')
    if div == None:
        div = soup.find('form', attrs={'name': 'theForm'})
        if div == None:
            div = soup.find('div', id="content_Body")
    # div=div.find_all('div',class_='ewb-article')[0]
    return div


today_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))

data = [
    ["zfcg_zhaobiao_gg",
     "http://www.qzzfcg.cn/xl/?l=%E9%87%87%E8%B4%AD%E4%BF%A1%E6%81%AF%2C%E9%87%87%E8%B4%AD%E5%85%AC%E5%91%8A",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhongbiao_gg",
     "http://www.qzzfcg.cn/xl/?l=%E9%87%87%E8%B4%AD%E4%BF%A1%E6%81%AF%2C%E4%B8%AD%E6%A0%87%E5%85%AC%E5%91%8A",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_biangeng_gg",
     "http://www.qzzfcg.cn/xl/?l=%E9%87%87%E8%B4%AD%E4%BF%A1%E6%81%AF%2C%E5%8F%98%E6%9B%B4%E5%85%AC%E5%91%8A",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_gqita_yugongshi_gg",
     "http://www.qzzfcg.cn/xl/?l=%E9%87%87%E8%B4%AD%E4%BF%A1%E6%81%AF%2C%E9%A2%84%E5%85%AC%E7%A4%BA",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '预公示'}), f2],
    #
    ["zfcg_zhaobiao_ecjj_gg",
     "http://zfcg.qzzfcg.cn/?pnum=1&do=YWJjZGVmc2VhcmNo&tab=YWJjZGVm&sw=&statsort=&statissue=&ds=2010-01-01&de=" + today_date + "/zhaobiao",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '二次竞价'}), f2],
    #
    ["zfcg_gqita_jjqk_ecjj_gg",
     "http://zfcg.qzzfcg.cn/?pnum=1&do=YWJjZGVmc2VhcmNo&tab=YWJjZGVm&sw=&statsort=&statissue=&ds=2010-01-01&de=" + today_date + "/jingjiajieguo",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '二次竞价', 'gglx': '竞价情况'}), f2],
    #
    ["zfcg_zhongbiao_ecjj_gg",
     "http://zfcg.qzzfcg.cn/?pnum=1&do=YWJjZGVmc2VhcmNo&tab=YWJjZGVm&sw=&statsort=&statissue=&ds=2010-01-01&de=" + today_date + "/zhongbiao",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '二次竞价'}), f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广西省钦州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "qinzhou"])
