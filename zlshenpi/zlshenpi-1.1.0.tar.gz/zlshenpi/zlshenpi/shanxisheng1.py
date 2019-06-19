import math

import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zlshenpi.util.etl import add_info, est_meta, est_html, est_tbs, add_info, est_meta_large
import sys
import time
import json

_name_ = "shanxisheng1"


def f1(driver, num):
    locator = (By.XPATH, '//table[@id="table1"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath('//table[@id="table1"]//tr[last()]/td').text
    cnum=re.findall('当前(.+?)页',cnum)[0].strip()
    cnum=re.findall('(\d+)\/',cnum)[0]

    if num != int(cnum):
        val = driver.find_element_by_xpath('//table[@id="table1"]//tr[2]//a').get_attribute('href')

        driver.execute_script("getjson(%s)"%num)

        locator = (
        By.XPATH, '//table[@id="table1"]//tr[2]//a[not(contains(@href, "%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data=[]
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    cons = soup.find('table', id='table1').find('tbody').find_all('tr')[1:-1]
    for con in cons:
        tds = con.find_all('td')

        name = tds[1].get_text().strip()
        xm_code = tds[0].get_text().strip()
        qiye = tds[2].get_text().strip()

        tds[3].find('script').clear()
        jieguo = tds[3].get_text().strip()
        href=tds[-1].a['href']
        ggstart_time='not'
        info = json.dumps({'qiye': qiye,   'jieguo': jieguo,'xm_code':xm_code},
                          ensure_ascii=False)

        href='http://www.shanxitzxm.gov.cn'+href

        tmp = [name, ggstart_time, href, info]
        # print(tmp)
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):

    locator = (By.XPATH, '//table[@id="table1"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath('//table[@id="table1"]//tr[last()]//a[last()]').get_attribute('onclick')
    total=re.findall('getjson\((\d+)\)',total)[0]
    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="hubei_con bmgk_mar"][string-length()>50]')
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
    div = soup.find('div',class_='hubei_con bmgk_mar')

    return div


data = [

    ["xm_beian_gg",
     "http://www.shanxitzxm.gov.cn/indexlink/xxgk/bacx.jspx",
     ["name", "ggstart_time", "href", "info"], f1,f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data,interval_page=1000, num=20,diqu="山西省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlshenpi", "shanxisheng1"],num=1,headless=False)
