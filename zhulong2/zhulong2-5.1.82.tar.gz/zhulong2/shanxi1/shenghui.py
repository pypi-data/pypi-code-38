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

_name_ = 'shanxi1_shenghui'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//td[@colspan='4']/table")
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
    div = soup.find('td', colspan='4')
    return div


def f1(driver, num):
    locator = (By.XPATH, "//table[@id='node_list']/tbody/tr")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//table[@id='node_list']/tbody/tr/td/a").get_attribute("href")[-10:]

    cnum = int(driver.find_element_by_xpath("//div[@class='pager']//font").text)
    # print('val', val, 'cnum', cnum)
    if int(cnum) != int(num):
        url = driver.current_url
        url = re.sub('page=\d+', 'page=' + str(num), url, count=1)
        driver.get(url)
        locator = (By.XPATH, '//table[@id="node_list"]/tbody/tr/td/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table[@id="node_list"]/tbody/tr')
    for content in content_list:
        name = content.xpath("./td/a/text()")[0].strip()
        ggstart_time = content.xpath("./td[2]/text()")[0].strip('[').strip(']')
        url = "http://www.sxzfcg.cn/"+content.xpath("./td/a/@href")[0]
        temp = [name, ggstart_time, url]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):

    locator = (By.XPATH, "//div[@class='pager']")
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    page = driver.find_element_by_xpath("//div[@class='pager']").text
    total_page = re.findall('/(\d+)',page)[0]
    driver.quit()
    return int(total_page)


data = [
    #
    ["zfcg_zhaobiao_huowu_gg","http://www.sxzfcg.cn/view.php?nav=61&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'货物'}), f2],
    ["zfcg_zhaobiao_gongcheng_gg","http://www.sxzfcg.cn/view.php?nav=62&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'工程'}), f2],
    ["zfcg_zhaobiao_fuwu_gg", "http://www.sxzfcg.cn/view.php?nav=63&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'服务'}), f2],

    ["zfcg_biangeng_huowu_gg","http://www.sxzfcg.cn/view.php?nav=64&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'货物'}), f2],
    ["zfcg_biangeng_gongcheng_gg","http://www.sxzfcg.cn/view.php?nav=65&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'工程'}), f2],
    ["zfcg_biangeng_fuwu_gg", "http://www.sxzfcg.cn/view.php?nav=66&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'服务'}), f2],

    ["zfcg_zhongbiao_huowu_gg", "http://www.sxzfcg.cn/view.php?nav=67&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'货物'}), f2],
    ["zfcg_zhongbiao_gongcheng_gg", "http://www.sxzfcg.cn/view.php?nav=68&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'工程'}), f2],
    ["zfcg_zhongbiao_fuwu_gg", "http://www.sxzfcg.cn/view.php?nav=69&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'服务'}), f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="山西省", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "shanxi1"])
