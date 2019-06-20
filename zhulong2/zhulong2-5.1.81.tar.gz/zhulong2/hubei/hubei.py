import datetime
import json
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
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from zhulong2.util.etl import est_tbs, est_meta, est_html, est_gg, add_info,est_meta_large

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://www.ccgp-hubei.gov.cn:8050/quSer/search"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_='hubei_hubei'


def f1(driver,num):
    locator = (By.XPATH, '//div[@class="news-list list-page"]/ul/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum=driver.find_element_by_xpath('//ul[@class="pagination"]/li[@class="active"]/a').text
    if int(cnum) != num:
        val=driver.find_element_by_xpath('//div[@class="news-list list-page"]/ul/li[1]/a').get_attribute('href').rsplit(
            '/', maxsplit=1)[1]

        driver.execute_script("pageGo({})".format(num))

        locator = (By.XPATH, '//div[@class="news-list list-page"]/ul/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data_ = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='news-list list-page').find('ul')
    ass = div.find_all('li', recursive=False)
    for li in ass:

        href=li.a['href']
        cgfs=li.a.find('font').extract().get_text()
        cglx=li.a.find('font').extract().get_text()
        name=li.a.get_text().rsplit(']',maxsplit=1)[1]
        ggstart_time=li.span.get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.ccgp-hubei.gov.cn' + href
        info={'jy_type':cgfs,'zbfs':cglx}
        info=json.dumps(info,ensure_ascii=False)
        tmp = [name, ggstart_time, href,info]
        data_.append(tmp)

    df=pd.DataFrame(data=data_)

    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="news-list list-page"]/ul/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//ul[@class="pagination"]/li[last()-1]/a').text.strip()
    total=int(total)
    driver.quit()
    return total


def query_data(f):
    def inner(*args):
        driver=args[0]
        locator = (By.XPATH, '//select[@class="form-control input-sm pull-left"]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        curl=driver.current_url
        if curl != "http://www.ccgp-hubei.gov.cn:8050/quSer/search":
            ctotal = driver.find_element_by_xpath('//ul[@class="pagination"]/li[last()]').text
            ctotal = re.findall('共\d+/(\d+)页', ctotal)[0]

            sele = driver.find_element_by_xpath('//select[@class="form-control input-sm pull-left"]')
            Select(sele).select_by_index(0)
            driver.find_element_by_xpath('//input[@type="button"]').click()
            locator = (By.XPATH, '//ul[@class="pagination"]/li[last()-1]/a[text() !="%s"][not(contains(string(),"尾"))]' % ctotal)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        return f(*args)
    return inner


def f3(driver, url):
    driver.get(url)
    time.sleep(0.5)

    locator = (By.XPATH, '//div[@class="row"][string-length()>10]')

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
    div = soup.find('div',class_=re.compile('^row$'))
    try:
        div.find('ul', class_='breadcrumb no-margin-left').extract()
    except:
        pass

    return div



data=[

    ["zfcg_zhaobiao_gg","http://www.ccgp-hubei.gov.cn/notice/cggg/pzbgg/index_1.html",["name", "ggstart_time", "href",'info'],query_data(f1),query_data(f2)],
    ["zfcg_zhongbiao_gg","http://www.ccgp-hubei.gov.cn/notice/cggg/pzhbgg/index_1.html",["name", "ggstart_time", "href",'info'],query_data(f1),query_data(f2)],
    ["zfcg_biangeng_gg","http://www.ccgp-hubei.gov.cn/notice/cggg/pgzgg/index_1.html",["name", "ggstart_time", "href",'info'],query_data(f1),query_data(f2)],
    ["zfcg_liubiao_gg","http://www.ccgp-hubei.gov.cn/notice/cggg/pfbgg/index_1.html",["name", "ggstart_time", "href",'info'],query_data(f1),query_data(f2)],
    ["zfcg_zhaobiao_danyilaiyuan_gg","http://www.ccgp-hubei.gov.cn/notice/cggg/pdylygg/index_1.html",["name", "ggstart_time", "href",'info'], query_data(f1),query_data(f2)],
    ["zfcg_gqita_gg","http://www.ccgp-hubei.gov.cn/notice/cggg/pqtgg/index_1.html",["name", "ggstart_time", "href",'info'],query_data(f1),query_data(f2)],

]


##f1中有zbfs,单一来源不用加info


def work(conp,**args):
    est_meta_large(conp,data=data,diqu="湖北省湖北",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","lch","hubei_hubei"]

    work(conp=conp,num=1,headless=False,total=10)