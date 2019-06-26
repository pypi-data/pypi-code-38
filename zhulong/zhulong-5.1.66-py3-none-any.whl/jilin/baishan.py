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

_name_='baishan'

def f1(driver,num):
    locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]/div/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('/(\d+?).html', url)[0]

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
            href = 'http://bsggzyjy.cbs.gov.cn' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]/div/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath('//li[@class="ewb-page-li ewb-page-noborder ewb-page-num"]/a').get_attribute(
    'href')

    total = re.findall('/(\d+?).html', page)
    if not total:
        total=1
    else:
        total=total[0]

    total = int(total)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="ewb-article-info"][string-length()>10]')

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
    div.find('div',class_='ewb-article-sources').extract()

    return div




data=[

    ["gcjs_zhaobiao_gg","http://bsggzyjy.cbs.gov.cn/jyxx/003001/003001001/1.html",["name","ggstart_time","href","info"],f1,f2],
    ["gcjs_biangeng_gg","http://bsggzyjy.cbs.gov.cn/jyxx/003001/003001002/1.html",["name","ggstart_time","href","info"],f1,f2],
    ["gcjs_zhongbiaohx_gg","http://bsggzyjy.cbs.gov.cn/jyxx/003001/003001003/1.html",["name","ggstart_time","href","info"],f1,f2],
    ["gcjs_zhongbiao_gg","http://bsggzyjy.cbs.gov.cn/jyxx/003001/003001004/1.html",["name","ggstart_time","href","info"],f1,f2],

    ["zfcg_zhaobiao_gg","http://bsggzyjy.cbs.gov.cn/jyxx/003002/003002001/1.html",["name","ggstart_time","href","info"],f1,f2],
    ######包含：流标，变更
    ["zfcg_gqita_bian_liu_gg","http://bsggzyjy.cbs.gov.cn/jyxx/003002/003002002/1.html",["name","ggstart_time","href","info"],f1,f2],
    ["zfcg_zhongbiao_gg","http://bsggzyjy.cbs.gov.cn/jyxx/003002/003002003/1.html",["name","ggstart_time","href","info"],f1,f2],
    ["zfcg_liubiao_gg","http://bsggzyjy.cbs.gov.cn/jyxx/003002/003002004/1.html",["name","ggstart_time","href","info"],f1,f2],

]

def work(conp,**args):
    est_meta(conp,data=data,diqu="吉林省白山市",**args)
    est_html(conp,f=f3,**args)

if __name__=='__main__':


    work(conp=["postgres","since2015","192.168.3.171","jilin","baishan"],headless=False,num=1)