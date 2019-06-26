import time
from collections import OrderedDict
from os.path import dirname, join

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

from zhulong.util.etl import est_tbs, est_meta, est_html, gg_existed, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]


# url="http://ggzyjy.xuancheng.gov.cn/XCTPFront/zfcg/012001/012001001/"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)


_name_ = 'dangyang'


def f1(driver, num):
    locator = (By.XPATH, '//ul[@class="list"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        cnum = driver.find_element_by_xpath('//a[@class="wb-page-default wb-page-number wb-page-family"]').text.strip()
        cnum = re.findall('(\d+)/', cnum)[0]
    except:
        driver.find_element_by_xpath('//ul[@class="list"]/li[1]/a')
        cnum=1

    if int(cnum) != num:
        val = driver.find_element_by_xpath('//ul[@class="list"]/li[1]/a').get_attribute('href')[-30:]

        driver.execute_script("ShowAjaxNewPage(window.location.pathname,'categorypagingcontent',{})".format(num))

        locator = (By.XPATH, '//ul[@class="list"]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data_ = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    div = soup.find('ul', class_='list')
    lis = div.find_all('li')
    for li in lis:
        href = li.a['href']
        name = li.a['title']
        ggstart_time = li.find('span', class_='list-date').get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://ggzyjy.dangyang.gov.cn' + href

        tmp = [name,  ggstart_time, href]

        data_.append(tmp)
    df = pd.DataFrame(data=data_)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@class="list"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        page = driver.find_element_by_xpath('//a[@class="wb-page-default wb-page-number wb-page-family"]').text
        total = re.findall('/(\d+)', page)[0]
    except:
        total=1
    total = int(total)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@id="mainContent"]')

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

    soup = BeautifulSoup(page, 'lxml')

    div = soup.find('div', id="mainContent")

    return div


def get_data():
    data = []

    ggtype1 = OrderedDict([("zhaobiao", "001"),("gqita_bian_cheng", "002"), ("zhongbiaohx", "003"), ("zhongbiao", "004"),("liubiao", "005")])
    ggtype2 = OrderedDict([("zhaobiao", "001"),("biangeng", "002"), ("zhongbiao", "003"), ("liubiao", "004"),("yucai", "005")])

    adtype1 = OrderedDict([('施工','1'),("监理", "2"), ("勘察设计", "3"), ("其他", "4")])
    adtype2 = OrderedDict([('货物','1'),("服务", "2")])


    for w1 in ggtype1.keys():
        for w2 in adtype1.keys():
            href="http://ggzyjy.dangyang.gov.cn/dySite/jyxx/003001/003001{0}/003001{1}00{2}/".format(ggtype1[w1],ggtype1[w1],adtype1[w2])
            tmp=["gcjs_%s_diqu%s_gg"%(w1,adtype1[w2]),href,["name","ggstart_time","href",'info'],add_info(f1,{"jy_type":w2}),f2]
            data.append(tmp)

    for w1 in ggtype2.keys():
        for w2 in adtype2.keys():
            href="http://ggzyjy.dangyang.gov.cn/dySite/jyxx/003002/003002{0}/003002{1}00{2}/".format(ggtype2[w1],ggtype2[w1],adtype2[w2])
            tmp=["zfcg_%s_diqu%s_gg"%(w1,adtype2[w2]),href,["name","ggstart_time","href",'info'],add_info(f1,{"jy_type":w2}),f2]
            data.append(tmp)

    remove_arr = ["gcjs_liubiao_diqu4_gg"]

    data1 = data.copy()
    for w in data:
        if w[0] in remove_arr: data1.remove(w)

    ##data1.append()
    return data1



data = get_data()


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖北省当阳市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "hubei", "dangyang"])

