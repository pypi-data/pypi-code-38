
import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write,db_command,db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import time

import json
from zhulong.util.etl import add_info,est_meta,est_html,est_tbs


_name_="sanming"



def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='ewb-notice-items']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//li[@class='ewb-page-li ewb-page-noborder ewb-page-num']/span")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = re.findall(r'(\d+)/', st)[0]
    except:
        cnum = 1
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='ewb-notice-items']/li[1]/a").get_attribute('href')[-40:]
        if "?pageing" not in url:
            s = "?pageing=%d" % (num) if num > 1 else "?pageing=1"
            url = url + s
        elif num == 1:
            url = re.sub("pageing=[0-9]*", "pageing=1", url)
        else:
            s = "pageing=%d" % (num) if num > 1 else "pageing=1"
            url = re.sub("pageing=[0-9]*", s, url)
        driver.get(url)
        try:
            locator = (By.XPATH, "//ul[@class='ewb-notice-items']/li[1]/a[not(contains(@href,'%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            driver.refresh()
            locator = (By.XPATH, "//ul[@class='ewb-notice-items']/li[1]/a[not(contains(@href,'%s'))]" % val)
            WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("ul", class_="ewb-notice-items")
    trs = table.find_all("li", class_="clearfix")
    data = []
    for tr in trs:
        a = tr.find('a')
        try:
            title = a["title"].strip()
        except:
            title = a.text.strip()
        link = a["href"].strip()
        td = tr.find("span", class_="r ewb-ndate").text.strip()
        href = "http://www.smggzy.cn"+link
        tmp = [title, td, href]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df




def f2(driver):
    locator = (By.XPATH, "//ul[@class='ewb-notice-items']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//li[@class='ewb-page-li ewb-page-noborder ewb-page-num']/span")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = re.findall(r'/(\d+)', st)[0]
    except:
        num = 1
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='ewb-show-info'][string-length()>15]")
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
    div = soup.find('div', class_="ewb-show-info")
    return div


data = [

    ["gcjs_zhaobiao_gg",
     "http://www.smggzy.cn/smwz/jyxx/022001/022001001/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_bian_da_gg",
     "http://www.smggzy.cn/smwz/jyxx/022001/022001002/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.smggzy.cn/smwz/jyxx/022001/022001004/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_zhong_zhongz_liu_gg",
     "http://www.smggzy.cn/smwz/jyxx/022001/022001005/",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["zfcg_zhaobiao_gg",
     "http://www.smggzy.cn/smwz/jyxx/022002/022002001/",
    ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_gqita_bian_da_gg",
     "http://www.smggzy.cn/smwz/jyxx/022002/022002002/",
    ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhongbiao_gg",
     "http://www.smggzy.cn/smwz/jyxx/022002/022002005/",
    ["name", "ggstart_time", "href", "info"],f1,f2],


    ["qsy_zhaobiao_gg",
     "http://www.smggzy.cn/smwz/jyxx/022006/022006001/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_gqita_bian_da_gg",
     "http://www.smggzy.cn/smwz/jyxx/022006/022006002/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_gqita_zhong_liu_gg",
     "http://www.smggzy.cn/smwz/jyxx/022006/022006005/",
     ["name", "ggstart_time", "href", "info"], f1, f2],


]


def work(conp,**args):
    est_meta(conp,data=data,diqu="福建省三明市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","fujian","sanming"])
