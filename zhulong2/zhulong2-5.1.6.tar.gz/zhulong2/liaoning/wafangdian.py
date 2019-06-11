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

_name_ = 'liaoning_wafangdian'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="news-content-page"]')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
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
    div = soup.find('div', class_='news-content-page')
    return div


def f1(driver, num):
    locator = (By.XPATH, '//ul[@class="large-list"]/li/a')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//ul[@class="large-list"]/li[1]/a').get_attribute("href")[-15:]
    cnum = driver.find_element_by_xpath('//*[@id="pages"]/b[2]/font').text

    # print('val', val, 'cnum', cnum,'num',num)
    if int(cnum) != int(num):
        url = driver.current_url
        url = url.rsplit('/',maxsplit=1)[0] +'/'+ str(num)+".html"
        driver.get(url)
        locator = (By.XPATH, '//ul[@class="large-list"]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//ul[@class="large-list"]/li')
    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        url =  content.xpath("./a/@href")[0]
        if 'http://www' not in url:
            url = "http://www.dlwfd.gov.cn/" + url
        temp = [name, ggstart_time, url]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//*[@id="pages"]/b[2]')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    total_page = re.findall('/(\d+)',driver.find_element_by_xpath('//*[@id="pages"]/b[2]').text)[0]
    # print('total_page', total_page)
    driver.quit()
    # print(total_page)
    return int(total_page)



data = [

    ["zfcg_zhaobiao_gg","http://www.dlwfd.gov.cn/xxgk/zbcg/zzcg/1.html",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg","http://www.dlwfd.gov.cn/xxgk/zbcg/gczb/1.html",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://www.dlwfd.gov.cn/xxgk/zbcg/zbgg/1.html", ["name", "ggstart_time", "href", "info"], f1,f2],

    #验收公示，需求公示，都无法访问
]



def work(conp, **arg):
    est_meta(conp, data=data, diqu="辽宁省瓦房店市", **arg)
    est_html(conp, f=f3, **arg)



if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "liaoning_wafangdian"],pageloadtimeout=60,pageloadstrategy='none')

