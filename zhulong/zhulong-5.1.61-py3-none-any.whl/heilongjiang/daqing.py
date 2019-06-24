import time

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json

from zhulong.util.etl import est_tbs,est_meta,est_html

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

# #
# url="http://www.bzztb.gov.cn/BZWZ/jyxx/003001/003001001/003001001001/003001001001001/"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)
#

_name_='daqing'

def f1(driver,num):
    locator = (By.XPATH, '//ul[@class="notice-list lf-list1"]/form/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath('//div[@class="pagination"]/a[@class="current"]').text

    if cnum != str(num):
        url = driver.current_url
        if num ==1:
            url = url.rsplit('/', maxsplit=1)[0] + '/index.htm'
        else:
            url = url.rsplit('/', maxsplit=1)[0] + '/index_' + str(num) + '.htm'

        val = driver.find_element_by_xpath('//ul[@class="notice-list lf-list1"]/form/li[1]/a').get_attribute('href')[-20]
        driver.get(url)
        locator = (By.XPATH, '//ul[@class="notice-list lf-list1"]/form/li[1]/a[not(contains(string(),"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='infor-con2 on')
    divs = div.find_all('li')

    for li in divs:
        href = li.a['href']
        name = li.a.get_text()
        ggstart_time = li.span.get_text()
        if 'http' in href:
            href = href
        else:
            href = 'http://zfcgzx.daqing.gov.cn' + href
        tmp = [name, ggstart_time, href]

        data.append(tmp)
    # print(data)
    df=pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@class="notice-list lf-list1"]/form/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath('//div[@class="pagination"]/a[last()]').get_attribute('href')

    page = re.findall('index_(\d+).htm', page)[0]
    total = int(page)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (
    By.XPATH, '//div[@class="main"] | //div[@class="tab_content"] | //div[@class="officialDoc"] |'
              ' //table[@class="printTable"] | //div[@class="WordSection1"] | //div[@class="content"] | /html/body/div')

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

    soup = BeautifulSoup(page, 'lxml')

    div = soup.find('div', class_='tab_content')
    if div == None:
        div = soup.find('div', class_="home-detail")
        if div == None:
            div = soup.find('div', class_="officialDoc")
            if div == None:
                div=soup.find('div',class_="content")
                if div == None:
                    div = soup.find('body').find('div',class_=None,recursive=False)

                    if div == None:
                        raise ValueError

                    if 'IP已经过了有效期' in div:
                        raise TimeoutError

    return div




data=[
    ["gcjs_zhaobiao_gg","http://zfcgzx.daqing.gov.cn/jyxxJsgcZbgg/index.htm",["name","ggstart_time","href","info"],f1,f2],
    ["gcjs_gqita_da_bian_gg","http://zfcgzx.daqing.gov.cn/jyxxJsgcBgcggg/index.htm",["name","ggstart_time","href","info"],f1,f2],
    ###包含中标，中标候选人，放弃中标
    ["gcjs_zhongbiaohx_gg","http://zfcgzx.daqing.gov.cn/jyxxJsgcZbgs/index.htm",["name","ggstart_time","href","info"],f1,f2],

    ["zfcg_zhaobiao_gg","http://zfcgzx.daqing.gov.cn/jyxxZfcgCggg/index.htm",["name","ggstart_time","href","info"],f1,f2],
    ["zfcg_zhongbiaohx_gg","http://zfcgzx.daqing.gov.cn/jyxxZfcgYzbgg/index.htm",["name","ggstart_time","href","info"],f1,f2],
    ["zfcg_zhongbiao_gg","http://zfcgzx.daqing.gov.cn/jyxxZfcgZbgg/index.htm",["name","ggstart_time","href","info"],f1,f2],

    ["zfcg_liubiao_gg","http://zfcgzx.daqing.gov.cn/jyxxZfcgFbgg/index.htm",["name","ggstart_time","href","info"],f1,f2],


]

def work(conp,**args):
    est_meta(conp,data=data,diqu="黑龙江省大庆市",**args)
    est_html(conp,f=f3,**args)

if __name__=='__main__':
    conp = ["postgres", "since2015", "192.168.3.171", "heilongjiang", "daqing"]

    work(conp=conp)