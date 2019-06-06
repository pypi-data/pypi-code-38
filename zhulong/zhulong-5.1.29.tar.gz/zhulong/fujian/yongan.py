
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


_name_="yongan"



def f1(driver, num):
    url = driver.current_url
    locator = (By.XPATH, "//ul[@class='ewb-notice-items']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//li[@class='ewb-page-li ewb-page-noborder ewb-page-num']/span")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = re.findall(r'(\d+)/', st)[0]
    except:
        cnum = 1

    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='ewb-notice-items']/li[1]/a").get_attribute('href')[-30:]
        driver.execute_script("ShowAjaxNewPage(window.location.pathname,'categorypagingcontent',{})".format(num))

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
        href = a["href"]
        if 'http' in href:
            link = href
        else:
            link = "http://www.smggzy.cn:8086" + href.strip()
        td = tr.find("span", class_="r ewb-ndate").text.strip()
        tmp = [title, td, link]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df




def f2(driver):
    url = driver.current_url
    locator = (By.XPATH, "//ul[@class='ewb-notice-items']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//li[@class='ewb-page-li ewb-page-noborder ewb-page-num']/span")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num_total = re.findall(r'/(\d+)', str)[0]
    except:
        num_total = 1

    driver.quit()
    return int(num_total)



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
    # div=div.find_all('div',class_='ewb-article')[0]
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.smggzy.cn:8086/smwz/yongan/027002/027002001/027002001001/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_bian_bu_gg",
     "http://www.smggzy.cn:8086/smwz/yongan/027002/027002001/027002001002/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.smggzy.cn:8086/smwz/yongan/027002/027002001/027002001004/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_zhong_liu_gg",
     "http://www.smggzy.cn:8086/smwz/yongan/027002/027002001/027002001005/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://www.smggzy.cn:8086/smwz/yongan/027002/027002002/027002002001/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_bian_bu_gg",
     "http://www.smggzy.cn:8086/smwz/yongan/027002/027002002/027002002002/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://www.smggzy.cn:8086/smwz/yongan/027002/027002002/027002002005/",
     ["name", "ggstart_time", "href", "info"], f1, f2],


]


def work(conp,**args):
    est_meta(conp,data=data,diqu="福建省永安市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","fujian","yongan"])
