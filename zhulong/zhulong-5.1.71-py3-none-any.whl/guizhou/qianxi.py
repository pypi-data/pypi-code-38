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

import json
from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html, est_tbs, add_info

_name_ = "qianxi"

def f1(driver, num):
    locator = (By.XPATH, '//tr[@class="trfont"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum=int(re.findall('Paging=(\d+)',url)[0])

    if cnum != num:
        page_count=len(driver.page_source)
        val = driver.find_element_by_xpath('//tr[@class="trfont"][1]//a').get_attribute('href')[-40:-10]
        url=re.sub('Paging=\d+','Paging=%s'%num,url)
        driver.get(url)
        locator = (By.XPATH, '//tr[@class="trfont"][1]//a[not(contains(@href,"%s"))]' % val)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        WebDriverWait(driver, 10).until(lambda driver: len(driver.page_source) != page_count)
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    divs = soup.find_all("tr",class_="trfont")

    data = []
    for div in divs:
        name = div.find("a")['title']
        href = div.find("a")['href']
        ggstart_time = div.find("td", align="right").get_text().strip(']').strip('[')

        ggtype=re.findall('【(.+?)】',name)

        ggtype=ggtype[0] if ggtype else None

        info=json.dumps({"ggtype":ggtype},ensure_ascii=False)

        if 'http' in href:
            href=href
        else:
            href='http://ggzyjy.qxn.gov.cn' + href

        tmp = [name, href, ggstart_time,info]


        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df



def f2(driver):
    locator = (By.XPATH, '//tr[@class="trfont"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        total = driver.find_element_by_xpath('//td[@class="huifont"]').text
        total=re.findall('/(\d+)$',total)[0]
    except:
        total = 1
    driver.quit()

    return int(total)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="outerwrap"][string-length()>50]')
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

    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')

    div = soup.find('div', class_='outerwrap').parent.parent

    return div


data = [
    ["gcjs_zhaobiao_gg1", "http://ggzyjy.qxn.gov.cn/qxnztb/jyxx/018001/018001001/?Paging=1",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg", "http://ggzyjy.qxn.gov.cn/qxnztb/jyxx/018001/018001004/?Paging=2",
     ["name", "href", "ggstart_time", "info"], f1, f2],

       ["zfcg_zhaobiao_gg", "http://ggzyjy.qxn.gov.cn/qxnztb/jyxx/018002/018002001/?Paging=3",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_zhongbiao_gg", "http://ggzyjy.qxn.gov.cn/qxnztb/jyxx/018002/018002003/?Paging=3",
     ["name", "href", "ggstart_time", "info"], f1, f2],

    ["zfcg_yucai_gg", "http://ggzyjy.qxn.gov.cn/qxnztb/jyxx/018002/018002008/?Paging=2",
     ["name", "href", "ggstart_time", "info"], f1, f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="贵州省黔西南州", **args)
    est_html(conp, f=f3, **args)

if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guizhou", "qianxi"])