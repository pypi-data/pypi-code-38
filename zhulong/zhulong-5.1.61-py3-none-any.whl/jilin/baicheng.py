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

#
# url="http://www.ccggzy.gov.cn/qxxxgk/003002/003002004/CountyPurhcaseNotice.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)
#

_name_='baicheng'

def f1(driver,num):
    locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]/div/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('/(\d+?).html', url)[0]

    url = url.rsplit('/', maxsplit=1)[0] + '/' + str(num) + '.html'

    if cnum != str(num):

        val = driver.find_element_by_xpath('//ul[@class="wb-data-item"]/li[1]/div/a').get_attribute('href')[-30:-5]

        driver.get(url)
        # 第二个等待
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
        ggstart_time = tr.span.get_text().strip()

        name = name.replace('[正在报名]', '')
        name = name.replace('[报名结束]', '')

        if 'http' in href:
            href = href
        else:
            href = 'http://ggzy.jlbc.gov.cn' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]/div/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        page = driver.find_element_by_xpath('//span[@id="index"]').text

        total = re.findall('/(\d+)', page)[0]
    except:
        total=1
    total = int(total)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               '//div[@class="ewb-about-content"] | //div[@class="ewb-process tabview"] | //div[@class="ewb-container ewb-alter"]')

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    try:
        mark = driver.find_element_by_xpath('//div[@class="ewb-location"]/a[4]').text
        driver.find_element_by_xpath('//ul[@data-role="head"]/li[string()="{}"]'.format(mark)).click()
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
            if i > 5: break

        page = driver.page_source

        soup = BeautifulSoup(page, 'html.parser')

        div = soup.find('div', attrs={'data-role': 'tab-content', 'class': ''})

    except:

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

        div = soup.find('div', class_='news-article')
    return div


data=[

    ["gcjs_zhaobiao_gg","http://ggzy.jlbc.gov.cn/jyxx/003001/003001001/1.html",["name","ggstart_time","href","info"],f1,f2],
    ["gcjs_biangeng_gg","http://ggzy.jlbc.gov.cn/jyxx/003001/003001002/1.html",["name","ggstart_time","href","info"],f1,f2],
    ["gcjs_zhongbiaohx_gg","http://ggzy.jlbc.gov.cn/jyxx/003001/003001003/1.html",["name","ggstart_time","href","info"],f1,f2],
    ["gcjs_zhongbiao_gg","http://ggzy.jlbc.gov.cn/jyxx/003001/003001004/1.html",["name","ggstart_time","href","info"],f1,f2],

    ["zfcg_zhaobiao_gg","http://ggzy.jlbc.gov.cn/jyxx/003002/003002001/1.html",["name","ggstart_time","href","info"],f1,f2],
    ["zfcg_biangeng_gg","http://ggzy.jlbc.gov.cn/jyxx/003002/003002002/1.html",["name","ggstart_time","href","info"],f1,f2],
    ["zfcg_zhongbiao_gg","http://ggzy.jlbc.gov.cn/jyxx/003002/003002003/1.html",["name","ggstart_time","href","info"],f1,f2],
]


##网址变更 http://ggzy.jlbc.gov.cn
##变更时间 2019-5-16


def work(conp,**args):
    est_meta(conp,data=data,pageLoadStrategy='none',pageloadtimeout=60,diqu="吉林省白城市",**args)
    est_html(conp,f=f3,**args)

if __name__=='__main__':


    work(conp=["postgres","since2015","192.168.3.171","jilin","baicheng"],headless=False,num=1)