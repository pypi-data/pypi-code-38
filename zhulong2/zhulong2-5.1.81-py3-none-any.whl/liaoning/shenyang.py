import json
import math
import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write, db_command, db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import time

from zhulong2.util.etl import est_meta, est_html

_name_ = 'liaoning_shenyang'

def f3(driver, url):
    driver.get(url)
    try:
        locator = (By.XPATH, "//div[@class='panel-body panel-notice']")
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        flag = 1
    except:
        locator = (By.XPATH, "//div[@class='control-label-text']")
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        flag = 2
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
    if flag == 1:
        div = soup.find('div', class_='panel-body panel-notice')
    else:
        div = soup.find('div', class_='control-label-text')

    return div


def f1(driver, num):

    locator = (By.XPATH, '//table[@id="protalInfoid"]/tbody/tr')
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    #
    val = driver.find_element_by_xpath('//table[@id="protalInfoid"]/tbody/tr[2]//a').text
    cnum = int(driver.find_element_by_xpath('//ul[@class="pagination"]/li[contains(@class,"active")]').text)
    while int(cnum) != int(num):
        total_page = math.ceil(int(re.findall("共 (\d+) 条",driver.find_element_by_xpath('//div[@class="col-xs-6 infoBar"]/span').text)[0])/50)
        if total_page - num < total_page//2:
            driver.find_elements_by_xpath('//a[@data-page="last"]')[0].click()
            locator = (By.XPATH, '//ul[@class="pagination"]/li[contains(@class,"active")][string()!=%s]'%cnum)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        cnum = int(driver.find_element_by_xpath('//ul[@class="pagination"]/li[contains(@class,"active")]').text)
        # print('val1', val, 'cnum1', cnum,'num',num)
        if cnum > int(num):
            dnum = cnum - int(num)
            for _ in range(dnum):
                driver.find_element_by_xpath("//ul[@class='pagination']/li[@class='prev']/a").click()
        else:
            dnum = int(num) > cnum
            for i in range(dnum):
                driver.find_element_by_xpath("//ul[@class='pagination']/li[@class='next']/a").click()
        locator = (By.XPATH, '//ul[@class="pagination"]/li[contains(@class,"active")][string()!=%s]' % cnum)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        cnum = int(driver.find_element_by_xpath('//ul[@class="pagination"]/li[contains(@class,"active")]').text)
        if int(cnum) == int(num):
            locator = (By.XPATH, '//table[@id="protalInfoid"]/tbody/tr[1]//a[not(contains(string(),"%s"))]' % val)
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
            break
        locator = (By.XPATH, '//table[@id="protalInfoid"][@aria-busy="false"]')
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
    data = []
    locator = (By.XPATH, '//table[@id="protalInfoid"]/tbody/tr')
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table[@id="protalInfoid"]/tbody/tr')
    for content in content_list:
        try:
            name = content.xpath(".//a/text()")[0].strip() + content.xpath("./td[2]/text()")[0].strip()
        except:
            name = content.xpath("./td[2]/text()")[0].strip()
        ggstart_time = content.xpath("./td[last()]/text()")[0].strip()
        url = "http://www.ccgp-shenyang.gov.cn/sygpimp/portalsys/portal.do?method=pubinfoView&info_id="+content.xpath(".//a/@id")[0].strip()
        temp = [name, ggstart_time, url]
        if int(content.xpath("count(./td)")) >3:
            info = content.xpath("./td[3]/text()")[0].strip()
        else:
            info = None
        info = json.dumps(info, ensure_ascii=False)
        temp.append(info)
        data.append(temp)
    df = pd.DataFrame(data=data)
    # df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//ul[@class='pagination']")
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    locator = (By.XPATH, '//table[@id="protalInfoid"]/tbody/tr[1]')
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    driver.find_elements_by_xpath('//a[@data-page="last"]')[0].click()
    locator = (By.XPATH, '//ul[@class="pagination"]/li[contains(@class,"active")][string()!=1]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_page = int(driver.find_element_by_xpath('//ul[@class="pagination"]/li[contains(@class,"active")]').text)
    # print('total_page', total_page)
    driver.quit()
    return total_page

def choice_50(driver):


    locator = (By.XPATH, "//ul[@class='pagination']")
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    locator = (By.XPATH, '//table[@id="protalInfoid"]/tbody/tr[1]')

    dropdown_text = driver.find_element_by_xpath('//button[@class="btn btn-default dropdown-toggle"]/span[@class="dropdown-text"]').text
    if int(dropdown_text) != 50:
        driver.find_element_by_xpath('//button[@class="btn btn-default dropdown-toggle"]').click()
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
        locator = (By.XPATH, '//table[@id="protalInfoid"]/tbody/tr[1]')
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
        driver.find_element_by_xpath('//ul[@role="menu"]//a[@data-action="50"]').click()
        time.sleep(1)


def before(f):
    def wrap(*args):
        driver = args[0]
        choice_50(driver)
        return f(*args)
    return wrap


data = [
    #
    ["zfcg_zhaobiao_gg", "http://www.ccgp-shenyang.gov.cn/sygpimp/portalindex.do?method=goInfo&linkId=cggg",
     ["name", "ggstart_time", "href", "info"], before(f1), before(f2)],
    ["zfcg_yanshou_gg", "http://www.ccgp-shenyang.gov.cn/sygpimp/portalindex.do?method=goInfoysgs&linkId=ysgs",
     ["name", "ggstart_time", "href", "info"], before(f1), before(f2)],
]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="辽宁省沈阳市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "liaoning_shenyang"],pageloadstrategy='none')
    # driver = webdriver.Chrome()
    # driver.get("http://www.ccgp-shenyang.gov.cn/sygpimp/portalindex.do?method=goInfo&linkId=cggg")
    # print(before(f1)(driver,88))