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

_name_ = 'jiangsu_lianyungang'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='news-article']")
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
    div = soup.find('div', class_='news-article')
    return div


def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='ewb-info-items']/li[1]/div/a")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//ul[@class='ewb-info-items']/li[1]/div/a").get_attribute("href")[-10:]

    cnum = re.findall(r'(\d*)\.html', driver.current_url)[0]
    # print('val', val, 'cnum', cnum)
    if int(cnum) != int(num):
        url = driver.current_url
        url = re.sub(r'\d*\.html', str(num) + ".html", url, count=1)
        # print("url",url)
        driver.get(url)
        locator = (By.XPATH, '//ul[@class="ewb-info-items"]/li[1]/div/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//ul[@class='ewb-info-items']/li")
    for content in content_list:
        area = content.xpath("./div/a/font/text()")[0].strip().strip('[').strip(']')
        try:
            name = content.xpath("./div/a/text()")[0].strip()
        except:
            name = content.xpath("./div/a/font/font/text()")[0].strip()

        ggstart_time = content.xpath("./span/text()")[0].strip().strip('[').strip(']')
        url = "http://www.lygzfcg.gov.cn/" + content.xpath("./div/a/@href")[0]
        temp = [name, ggstart_time, url, area]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    try:
        locator = (By.XPATH, '//span[@class="wb-page-default wb-page-number wb-page-family"]')
        WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
        total_page = re.findall('/(\d+)', driver.find_element_by_xpath(
            '//span[@class="wb-page-default wb-page-number wb-page-family"]').text)[0]
    except:
        total_page = 1
    # print('total_page', total_page)
    driver.quit()
    return int(total_page)


data = [
    #
    ["zfcg_zhaobiao_gg", "http://www.lygzfcg.gov.cn/cgxx/002001/1.html",
     ["name", "ggstart_time", "href", "area", "info"], f1, f2],
    ["zfcg_yucai_gg", "http://www.lygzfcg.gov.cn/cgxx/002002/1.html",
     ["name", "ggstart_time", "href", "area", "info"],f1, f2],
    ["zfcg_biangeng_gg", "http://www.lygzfcg.gov.cn/cgxx/002003/1.html",
     ["name", "ggstart_time", "href", "area", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://www.lygzfcg.gov.cn/cgxx/002004/1.html",
     ["name", "ggstart_time", "href", "area", "info"], f1, f2],
    ["zfcg_liubiao_gg", "http://www.lygzfcg.gov.cn/cgxx/002005/1.html",
     ["name", "ggstart_time", "href", "area", "info"], f1, f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="江苏省连云港市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "jiangsu_lianyungang"])
