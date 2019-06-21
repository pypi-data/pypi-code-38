import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json

import time

from zhulong4.util.etl import est_html, est_meta, add_info

_name_ = "www_dlzb_com_c1608"


def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='gclist_ul']/li[1]/a[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        locator = (By.XPATH, "//div[@class='pages']/strong")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='gclist_ul']/li[1]/a[1]").get_attribute('href')[-15:]
        if num == 1:
            url = re.sub("c-1608/[0-9]*", "c-1608/1", url)
        else:
            s = "c-1608/%d" % (num) if num > 1 else "c-1608/1"
            url = re.sub("c-1608/[0-9]*", s, url)
        driver.get(url)

        locator = (By.XPATH, "//ul[@class='gclist_ul']/li[1]/a[1][not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("ul", class_='gclist_ul')
    lis = div.find_all('li', class_='bg_li')
    data = []
    for li in lis[1:]:
        a = li.find_all("a")[0]
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = 'https://www.dlzb.com/' + link

        span = li.find('span', class_='dlgs_riqi').text.strip()
        tmp = [title, span, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//ul[@class='gclist_ul']/li[1]/a[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='pages']/a[last()-1]")
        num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='content']")
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
    div = soup.find('div', id='content')
    return div



data = [
    ["qy_gqita_zhao_zhong_gg",
     "https://www.dlzb.com/c-1608/1/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="哈尔滨电气集团有限公司", **args)
    est_html(conp, f=f3, **args)



# 页面有些信息需要VIP才能查看
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang3", "www_dlzb_com_c1608"])

    # driver = webdriver.Chrome()
    # url = "https://www.dlzb.com/c-1608/1/"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    #
    # driver=webdriver.Chrome()
    # url = "https://www.dlzb.com/c-1608/1/"
    # driver.get(url)
    # for i in range(1, 3):
    #     df=f1(driver, i)
    #     print(df.values)
