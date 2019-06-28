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

from zhulong.util.etl import est_tbs, est_meta, est_html, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url="http://ggzy.siping.gov.cn/jyxx/004002/004002002/about.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)
#

_name_='siping'


def f1(driver,num):
    locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]/div/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    try:
        cnum = driver.find_element_by_xpath('//li[@class="ewb-page-li ewb-page-border current"]').text.strip()
    except:
        locator = (By.XPATH, '//ul[@class="wb-data-item"][count(*)<=18 and count(*)>=1]')
        WebDriverWait(driver, 5).until(EC.presence_of_element_located(locator))
        cnum='1'

    if cnum != str(num):
        url = url.rsplit('/', maxsplit=1)[0] + '/' + str(num) + '.html'
        val = driver.find_element_by_xpath('//ul[@class="wb-data-item"]/li[1]/div/a').get_attribute('href')[-30:-5]

        driver.get(url)

        locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]/div/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('ul', class_='wb-data-item')
    trs = div.find_all('li')

    for tr in trs:

        href = tr.div.a['href']
        name = tr.div.a.get_text().strip()
        ggstart_time = tr.span.get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://ggzy.siping.gov.cn' + href

        tmp = [name, ggstart_time, href]
        print(tmp)
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    driver.maximize_window()

    locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]/div/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    while True:
        val = driver.find_element_by_xpath('//ul[@class="wb-data-item"]/li[1]/div/a').get_attribute('href')[-30:-5]
        try:
            href=driver.find_element_by_xpath('//li[@class="ewb-page-li ewb-page-border "][last()]/a').get_attribute('href')

            driver.get(href)
        except:
            locator = (By.XPATH, '//ul[@class="wb-data-item"][count(*)<=18 and count(*)>=1]')
            WebDriverWait(driver, 5).until(EC.presence_of_element_located(locator))
            total=1
            break
        locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]/div/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        time.sleep(1)
        try:
            val = driver.find_element_by_xpath('//ul[@class="wb-data-item"]/li[1]/div/a').get_attribute('href')[-30:-5]
            href=driver.find_element_by_xpath('//li[@class="ewb-page-li ewb-page-border ewb-page-hover"][2]/a').get_attribute('href')
            driver.get(href)

            locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]/div/a[not(contains(@href,"%s"))]' % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            locator = (By.XPATH,'//li[@class="ewb-page-li ewb-page-border ewb-page-hover"][2][count(*)=0]')
            WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
            total = driver.find_element_by_xpath('//li[@class="ewb-page-li ewb-page-border current"]').get_attribute('textContent')

            break

    total = int(total)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="ewb-article"]')

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
    div = soup.find('div',class_='ewb-article')
    div.find('div',class_="ewb-article-sources").extract()
    return div



data=[
    ["gcjs_zhaobiao_gg","http://ggzy.siping.gov.cn/jyxx/004001/004001001/about.html",["name","ggstart_time","href","info"],f1,f2],
    ["gcjs_gqita_da_bian_gg","http://ggzy.siping.gov.cn/jyxx/004001/004001002/about.html",["name","ggstart_time","href","info"],f1,f2],
    ["gcjs_zhongbiaohx_gg","http://ggzy.siping.gov.cn/jyxx/004001/004001003/about.html",["name","ggstart_time","href","info"],f1,f2],
    ["gcjs_zhongbiao_gg","http://ggzy.siping.gov.cn/jyxx/004001/004001004/about.html",["name","ggstart_time","href","info"],f1,f2],
    ["gcjs_liubiao_gg","http://ggzy.siping.gov.cn/jyxx/004001/004001005/about.html",["name","ggstart_time","href","info"],f1,f2],

    ["zfcg_zhaobiao_gg","http://ggzy.siping.gov.cn/jyxx/004002/004002001/about.html",["name","ggstart_time","href","info"],f1,f2],
    ["zfcg_gqita_da_bian_gg","http://ggzy.siping.gov.cn/jyxx/004002/004002002/about.html",["name","ggstart_time","href","info"],f1,f2],
    ["zfcg_zhongbiao_gg","http://ggzy.siping.gov.cn/jyxx/004002/004002003/about.html",["name","ggstart_time","href","info"],f1,f2],
    ["zfcg_liubiao_gg","http://ggzy.siping.gov.cn/jyxx/004002/004002005/about.html",["name","ggstart_time","href","info"],f1,f2],

    ["gcjs_jiaotongshuili_zhaobiao_gg","http://ggzy.siping.gov.cn/jyxx/004003/004003001/about.html",["name","ggstart_time","href","info"],add_info(f1,{"gclx":"交通水利"}),f2],
    ["gcjs_jiaotongshuili_gqita_da_bian_gg","http://ggzy.siping.gov.cn/jyxx/004003/004003002/about.html",["name","ggstart_time","href","info"],add_info(f1,{"gclx":"交通水利"}),f2],
    ["gcjs_jiaotongshuili_zhongbiaohx_gg","http://ggzy.siping.gov.cn/jyxx/004003/004003003/about.html",["name","ggstart_time","href","info"],add_info(f1,{"gclx":"交通水利"}),f2],
    ["gcjs_jiaotongshuili_zhongbiao_gg","http://ggzy.siping.gov.cn/jyxx/004003/004003004/about.html",["name","ggstart_time","href","info"],add_info(f1,{"gclx":"交通水利"}),f2],
    ["gcjs_jiaotongshuili_liubiao_gg","http://ggzy.siping.gov.cn/jyxx/004003/004003005/about.html",["name","ggstart_time","href","info"],add_info(f1,{"gclx":"交通水利"}),f2],

]

def work(conp,**args):
    est_meta(conp,data=data,diqu="吉林省四平市",**args)
    est_html(conp,f=f3,**args)

if __name__=='__main__':
    conp = ["postgres", "since2015", "192.168.3.171", "jilin", "siping"]

    work(conp=conp,headless=False,num=1,total=5,cdc_total=5)