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

_name_ = 'liaoning_chaoyang'


def f3(driver, url):
    driver.get(url)
    try:
        locator = (By.XPATH, '//table[@id="tblInfo"]')
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        flag = 1
    except:
        locator = (By.XPATH, '//*[@id="container"]/div[2]/div[2]')
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
    if flag ==1:
        div = soup.find('table', id='tblInfo')
    else:
        div = soup.find('div',class_="ewb-show-con")
    return div


def f1(driver, num):
    locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]/a')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//ul[@class="wb-data-item"]/li[1]/a').get_attribute("href")[-50:]
    cnum = re.findall('(\d+)/',driver.find_element_by_xpath('//div[@class="pages"]//li[@class="wb-page-li visible-desktop"]').text)[0]

    # print('val', val, 'cnum', cnum,'num',num)
    if int(cnum) != int(num):
        driver.execute_script("ShowAjaxNewPage('categorypagingcontent','/ZGCY/','004017001',%s)"%num)
        locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//ul[@class="wb-data-item"]/li')
    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        url = "http://www.zgcy.gov.cn" + content.xpath("./a/@href")[0]
        temp = [name, ggstart_time, url]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="pages"]//li[@class="wb-page-li visible-desktop"]')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    total_page = re.findall('/(\d+)',driver.find_element_by_xpath('//div[@class="pages"]//li[@class="wb-page-li visible-desktop"]').text)[0]
    driver.quit()
    return int(total_page)



data = [

    ["zfcg_zhaobiao_gg","http://www.zgcy.gov.cn/ZGCY/zwgk/004017/004017001/",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg","http://www.zgcy.gov.cn/ZGCY/zwgk/004017/004017002/",["name", "ggstart_time", "href", "info"], f1, f2],

    #验收公示，需求公示，都无法访问
]



def work(conp, **arg):
    est_meta(conp, data=data, diqu="辽宁省朝阳市", **arg)
    est_html(conp, f=f3, **arg)



if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "liaoning_chaoyang"],pageloadtimeout=60,pageloadstrategy='none',)
