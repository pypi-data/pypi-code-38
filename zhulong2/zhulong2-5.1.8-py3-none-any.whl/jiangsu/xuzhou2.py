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

_name_ = 'jiangsu_xuzhou2'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@id='tblInfo']")
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
    div = soup.find('table', id='tblInfo')
    return div


def f1(driver, num):
    locator = (By.XPATH, "//font[@color='red']/b")
    cnum = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text
    if int(cnum) != int(num):
        locator = (By.XPATH, "//div[@id='categorypagingcontent']/table/tbody/tr[1]/td/a")
        val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute('href')[-40:]
        project_code = driver.current_url.split('/')[-2]
        driver.execute_script("ShowAjaxNewPage('/zgxz/','%s',%s);" % (project_code,num))
        locator = (By.XPATH, '//div[@id="categorypagingcontent"]/table/tbody/tr[1]/td/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@id='categorypagingcontent']/table/tbody/tr")
    for content in content_list:
        name = content.xpath("./td/a/@title")[0].strip()
        ggstart_time = content.xpath('./td[last()]/text()')[0].strip()
        href = "http://www.xz.gov.cn" + content.xpath("./td/a/@href")[0].strip()
        temp = [name, ggstart_time, href]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):

    locator = (By.XPATH, "//font[@color='blue'][2]/b")
    total_page = int(WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text)

    # print('total_page', total_page)
    driver.quit()

    return int(total_page)



data = [

    ["zfcg_zhaobiao_gg", "http://www.xz.gov.cn/zgxz/zwgk/008022/008022002/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg", "http://www.xz.gov.cn/zgxz/zwgk/008022/008022003/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="江苏省徐州市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "jiangsu_xuzhou2"])
