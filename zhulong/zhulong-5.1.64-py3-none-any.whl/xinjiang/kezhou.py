import time
from collections import OrderedDict
from os.path import dirname, join
from pprint import pprint

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


_name_ = 'kezhou'


def f1(driver, num):
    locator = (By.XPATH, '//tr[@valign="top"][1]/td[2]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath('//div[@id="MoreInfoList1_Pager"]//td[1]/font[@color="red"]/b').text.strip()

    if int(cnum) != num:
        val = driver.find_element_by_xpath('//tr[@valign="top"][1]/td[2]/a').get_attribute('href')[-50:-25]

        driver.execute_script("javascript:__doPostBack('MoreInfoList1$Pager','{}')".format(num))

        locator = (By.XPATH, '//tr[@valign="top"][1]/td[2]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data_ = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    lis = soup.find_all('tr', valign='top')
    for li in lis:
        tds = li.find_all('td')
        href = tds[1].a['href']
        name = tds[1].a['title']
        ggstart_time = tds[2].get_text().strip()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.kzggzyjy.com.cn' + href

        tmp = [name,  ggstart_time,href]

        data_.append(tmp)
    df = pd.DataFrame(data=data_)
    df["info"]=None
    return df


def f2(driver):
    locator = (By.XPATH, '//tr[@valign="top"][1]/td[2]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.find_element_by_xpath('//div[@id="MoreInfoList1_Pager"]//td[1]/font[@color="blue"][2]/b').text
    total = int(page)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//td[@class="infodetail"]')

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

    div = soup.find('table', id="tblInfo")


    return div


def get_data():
    data = []

    ggtype1 = OrderedDict([("zhaobiao", "001"),("biangeng", "002"), ("zhongbiaohx", "003")])
    ggtype2 = OrderedDict([("zhaobiao", "001"),("biangeng", "002"), ("zhongbiao", "003")])
    adtype1 = OrderedDict([('阿图什市','1'),("阿克陶县", "2"), ("阿合奇县", "3"), ("乌恰县", "4"),('克州本级','5')])


    #gcjs
    for w1 in ggtype1.keys():
        for w2 in adtype1.keys():
            href="http://www.kzggzyjy.com.cn/kzweb/jyxx/021001/021001{ggtype}/021001{ggtype}00{diqu}/MoreInfo.aspx?CategoryNum=021001{ggtype}00{diqu}".format(ggtype=ggtype1[w1],diqu=adtype1[w2])
            tmp=["gcjs_%s_diqu%s_gg"%(w1,adtype1[w2]),href,["name","ggstart_time","href",'info'],add_info(f1,{"diqu":w2}),f2]
            data.append(tmp)
    #zfcg
    for w1 in ggtype2.keys():
        for w2 in adtype1.keys():
            href="http://www.kzggzyjy.com.cn/kzweb/jyxx/021002/021002{ggtype}/021002{ggtype}00{diqu}/MoreInfo.aspx?CategoryNum=021002{ggtype}00{diqu}".format(ggtype=ggtype2[w1],diqu=adtype1[w2])
            tmp=["zfcg_%s_diqu%s_gg"%(w1,adtype1[w2]),href,["name","ggstart_time","href",'info'],add_info(f1,{"diqu":w2}),f2]
            data.append(tmp)

    data1 = data.copy()


    ##data1.append()
    return data1



data = get_data()
# pprint(data)


def work(conp, **args):
    est_meta(conp, data=data, diqu="新疆省克州", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "xinjiang", "kezhou"],num=1,total=2)

    pass

