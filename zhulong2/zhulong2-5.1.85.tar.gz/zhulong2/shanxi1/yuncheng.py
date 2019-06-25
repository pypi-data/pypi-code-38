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

from zhulong2.util.etl import est_meta, est_html, add_info

_name_ = 'shanxi1_yuncheng'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//*[@id="BBS_content"]')
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
    div = soup.find('div', id='BBS_content')
    return div


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='lm_main_box']/div/ul/li")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//div[@class='lm_main_box']/div/ul/li/a").get_attribute("href")[-15:]

    cnum = int(driver.find_element_by_xpath("//span[@class='pageinfo']/b").text)
    # print('val', val, 'cnum', cnum)
    if int(cnum) != int(num):
        url = driver.current_url
        p = str((num-1)*20)
        p_1 = int(p)//200 * 200 + 1
        # print("p",p,"p_1",p_1)
        url = '/'.join(url.split('/')[:7])+'/'+p+'/'+str(p_1)+'.html'
        driver.get(url)
        locator = (By.XPATH, '//div[@class="lm_main_box"]/div/ul/li/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@class='lm_main_box']/div/ul[not(contains(@class,'page f14 weiruan'))]/li")
    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()
        # print(name)
        ggstart_time = content.xpath("./span/text()")[0].strip()
        url = "http://www.ccgp-yuncheng.gov.cn"+content.xpath("./a/@href")[0]
        temp = [name, ggstart_time, url]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//span[@class='pageinfo']")
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    page = driver.find_element_by_xpath("//span[@class='pageinfo']").text
    total_page = re.findall('共(\d+)页',page)[0]
    # print('total_page', total_page)
    driver.quit()
    return int(total_page)


data = [
    #
    ["zfcg_zhaobiao_gg","http://www.ccgp-yuncheng.gov.cn/news_list/3/14/0/0/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg","http://www.ccgp-yuncheng.gov.cn/news_list/3/16/0/0/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg", "http://www.ccgp-yuncheng.gov.cn/news_list/3/15/0/0/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_liubiao_gg", "http://www.ccgp-yuncheng.gov.cn/news_list/3/17/0/0/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_danyilaiyuan_gg", "http://www.ccgp-yuncheng.gov.cn/news_list/3/18/0/0/1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'method':'单一来源'}), f2],

    ["zfcg_yucai_gg", "http://www.ccgp-yuncheng.gov.cn/news_list/3/19/0/0/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_gg", "http://www.ccgp-yuncheng.gov.cn/news_list/3/21/0/0/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="山西省运城市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "shanxi_yuncheng"])