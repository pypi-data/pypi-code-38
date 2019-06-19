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

_name_ = 'zhejiang_quzhou'


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='ewb-details-info']")
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
    div = soup.find('div', class_='ewb-details-info')
    return div


def f1(driver, num):
    locator = (By.XPATH, '//ul[@class="ewb-news-items"]/li[1]/a')
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-30:]

    locator = (By.XPATH, '//span[contains(@id,"index")]')
    txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    cnum = re.findall('(\d+)\/',txt)[0]

    # print('val', val, 'cnum', cnum,"num",num)
    if int(cnum) != int(num):
        url = driver.current_url
        new_url = re.sub(r"\d+\.", str(num) + '.', url)
        driver.get(new_url)

        locator = (By.XPATH, '//ul[@class="ewb-news-items"]/li[1]/a[not(contains("@href","%s"))]'%val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//ul[@class="ewb-news-items"]/li')
    for content in content_list:
        ggstart_time = content.xpath('./span/text()')[0].strip()
        name = content.xpath("./a/@title")[0].strip()
        href = "http://www.qzggzy.com"+content.xpath("./a/@href")[0].strip()
        temp = [name, ggstart_time, href]
        # print(temp)
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//span[contains(@id,"index")]')
    txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    total_page = re.findall('\/(\d+)',txt)[0]
    driver.quit()
    return int(total_page)


data = [
    #
    ["zfcg_zhaobiao_gg", "http://www.qzggzy.com/jyxx/002002/002002001/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],#
    ["zfcg_zhongbiao_gg", "http://www.qzggzy.com/jyxx/002002/002002002/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],#
    ["zfcg_hetong_gg", "http://www.qzggzy.com/jyxx/002002/002002003/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],#
    ["zfcg_gqita_zhao_bian_1_gg", "http://www.qzggzy.com/jyxx/002002/002002004/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],#
    ["zfcg_gqita_zhao_bian_2_gg", "http://www.qzggzy.com/jyxx/002002/002002005/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="浙江省衢州市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "zhejiang_quzhou"],num=2)
    # driver = webdriver.Chrome()
    # driver.get("http://www.qzggzy.com/jyxx/002002/002002001/1.html")
    # for i in range(1,4):
    #     f1(driver,i)
