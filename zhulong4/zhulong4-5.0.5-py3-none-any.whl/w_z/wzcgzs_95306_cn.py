import time

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json

from zhulong4.util.etl import est_tbs, est_meta, est_html,est_meta_large


_name_ = 'wzcgzs_95306_cn'


def f1(driver, num):
    locator = (By.XPATH, '//table[@class="listInfoTable"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('curPage=(\d+)&', url)[0]

    if num != int(cnum):
        val = driver.find_element_by_xpath('//table[@class="listInfoTable"]//tr[2]//a').get_attribute('href')[-30:]

        url = re.sub('curPage=(\d+)&', 'curPage=%s&' % num, url)
        driver.get(url)

        locator = (By.XPATH, '//table[@class="listInfoTable"]//tr[2]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', class_='listInfoTable').find_all('tr')[1:-1]

    for tr in div:
        tds = tr.find_all('td')
        if len(tds)==1:
            continue
        href = tds[1].a['href']
        name = tds[1].a.get_text()
        index_num = tds[2].get_text()
        gg_type = tds[3].get_text()
        ggstart_time = tds[-1].get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://wzcgzs.95306.cn' + href
        info={'index_num':index_num,'gg_type':gg_type}
        info=json.dumps(info,ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//table[@class="listInfoTable"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//div[@class="LsitInfoFrameBtmBg"]/b[last()]').text
    total = re.findall('共(\d+)页', total)[0]
    total = int(total)
    driver.quit()
    return total



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH,'//div[@class="noticeBox"]')
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    time.sleep(0.1)
    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 10: break
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_="noticeBox")
    return div


data = [

    #包含招标,中标
    ["qy_gqita_zhao_zhong_gg","http://wzcgzs.95306.cn/notice/indexlist.do?dealGroup=10&unitType=&noticeType=01&dealType=&materialType=&extend=1&curPage=1&notTitle=&inforCode=&time0=&time1=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qy_yucai_gg","http://wzcgzs.95306.cn/notice/indexlist.do?dealGroup=20&unitType=&noticeType=01&dealType=&materialType=&extend=1&curPage=1&notTitle=&inforCode=&time0=&time1=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qy_biangeng_gg", "http://wzcgzs.95306.cn/notice/indexlist.do?dealGroup=10&unitType=&noticeType=02&dealType=&materialType=&extend=1&curPage=1&notTitle=&inforCode=&time0=&time1=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qy_gqita_bian_da_gg", "http://wzcgzs.95306.cn/notice/indexlist.do?dealGroup=10&unitType=&noticeType=03&dealType=&materialType=&extend=1&curPage=1&notTitle=&inforCode=&time0=&time1=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qy_zhongbiaohx_gg", "http://wzcgzs.95306.cn/notice/indexlist.do?dealGroup=10&unitType=&noticeType=04&dealType=&materialType=&extend=1&curPage=1&notTitle=&inforCode=&time0=&time1=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="中国铁路物资集团", **args)
    est_html(conp, f=f3, **args)



if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch3", "wzcgzs_95306_cn"])


