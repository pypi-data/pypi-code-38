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

_name_ = 'zhejiang_wenzhou'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='Content-Main FloatL'][string-length()>10]")
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
    div = soup.find('div', class_='Content-Main FloatL')
    return div


def f1(driver, num):
    locator = (By.XPATH, '//*[@id="4475593"]/div/div[2]/div[1]/a')
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//*[@id="4475593"]/div/div[2]/div[1]/a').get_attribute("href")[-30:]

    cnum = driver.find_element_by_xpath('//input[@class="default_pgCurrentPage"]').get_attribute("value")
    # print('val', val, 'cnum', cnum,"num",num)
    if int(cnum) != int(num):
        url = driver.current_url
        url1 = re.sub(r"pageNum=\d+", 'pageNum=' + str(num), url)
        driver.get(url1)
        locator = (By.XPATH, '//*[@id="4475593"]/div/div[2]/div[1]/a')
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
        driver.find_element_by_xpath('//div[@class="default_pgBtn default_pgRefresh"]').click()
        locator = (By.XPATH, '//*[@id="4475593"]/div/div[2]/div[1]/a[@href!="%s"]' % val)
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="default_pgContainer"]/div[contains(@style,33)]')
    for content in content_list:
        ggstart_time = content.xpath('./div[last()]/text()')[0].strip()
        name = content.xpath("./div/a/text()")[0].strip()
        href = content.xpath("./div/a/@href")[0].strip()
        temp = [name, ggstart_time, href]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//span[@class="default_pgTotalPage"]')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
    total_page = driver.find_element_by_xpath('//span[@class="default_pgTotalPage"]').text
    driver.quit()
    return int(total_page)


data = [
    #
    ["zfcg_zhaobiao_gg", "http://www.wenzhou.gov.cn/col/col1218664/index.html?uid=4475593&pageNum=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="浙江省温州市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "zhejiang_wenzhou"])

