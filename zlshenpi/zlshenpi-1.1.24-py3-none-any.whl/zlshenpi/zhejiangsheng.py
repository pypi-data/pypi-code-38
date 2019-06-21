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
from zlshenpi.util.etl import add_info, est_meta, est_html, est_tbs, add_info
import sys
import time
import json

_name_ = "zhejiangsheng"


def f1(driver, num):
    locator = (By.XPATH, '//table[@id="resultShowTable"]//tr[1]/td[1]/a')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath('//span[@id="nav"]').text

    if num != int(cnum):
        val = driver.find_element_by_xpath('//table[@id="resultShowTable"]//tr[1]').get_attribute('pid')

        search_button = driver.find_element_by_xpath('//input[@id="goPage"]')
        driver.execute_script("arguments[0].value = '%s';" % num, search_button)
        click_button = driver.find_element_by_xpath('//input[@id="goPage"]/following-sibling::a')
        driver.execute_script("arguments[0].click()", click_button)

        locator = (
        By.XPATH, '//table[@id="resultShowTable"]//tr[1][not(contains(@pid, "%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    data=[]
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    cons = soup.find('table', id='resultShowTable').find('tbody').find_all('tr')
    for con in cons:
        tds = con.find_all('td')

        name = tds[1]['title'].strip()
        xm_code = tds[0].get_text().strip()
        shixiang = tds[2]['title'].strip()

        bumen = tds[3].get_text().strip()
        jieguo = tds[4].get_text().strip()
        ggstart_time = tds[5].get_text()
        info = json.dumps({'shixiang': shixiang, 'bumen': bumen,  'jieguo': jieguo,'xm_code':xm_code},
                          ensure_ascii=False)

        pid = con['pid']
        aid = con['aid']
        href='http://tzxm.zjzwfw.gov.cn/resultshowdetail.html?pid=%s&aid=%s'%(pid,aid)

        tmp = [name, ggstart_time, href, info]
        # print(tmp)
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):

    locator = (By.XPATH, '//table[@id="resultShowTable"]//tr[1]/td[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath('//span[@id="pages"]').text.strip()
    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="box"][string-length()>50]')
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
    div = soup.find('div',class_='box')

    return div


data = [


    ["xm_shenpi_gg",
     "http://tzxm.zjzwfw.gov.cn/resultshow.html",
     ["name", "ggstart_time", "href", "info"], f1,f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="浙江省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlshenpi", "zhejiangsheng"],)
