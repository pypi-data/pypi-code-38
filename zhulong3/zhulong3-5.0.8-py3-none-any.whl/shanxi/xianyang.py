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

from zhulong3.util.etl import est_html, est_meta, add_info

_name_ = "shanxi_xianyang"


def f1(driver, num):
    locator = (By.XPATH, "//table[@id='NewList']/tbody/tr[1]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        cnum = soup.find('span', id='Pager1_CurPage').text.strip()
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@id='NewList']/tbody/tr[1]/td/a").get_attribute('href')[-30:]
        locator = (By.XPATH, "//input[@id='Pager1_NavPage']")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).clear()
        locator = (By.XPATH, "//input[@id='Pager1_NavPage']")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).send_keys(num, Keys.ENTER)
        locator = (By.XPATH, "//table[@id='NewList']/tbody/tr[1]/td/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("table", id='NewList').tbody
    lis = div.find_all("tr", class_='nslist')
    data = []
    for li in lis:
        a = li.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        span = li.find("td", align="right").text.strip()
        span = re.findall(r'\[(.*)\]', span)[0]
        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = 'http://www.xyjsgc.com/website/main/' + link
        tmp = [title, span, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//table[@id='NewList']/tbody/tr[1]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//span[@id='Pager1_Pages']")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        num = soup.find('span', id='Pager1_Pages').text.strip()
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='all auto_h']")
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
    div = soup.find('div', class_='all auto_h')
    # div=div.find_all('div',class_='ewb-article')[0]
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.xyjsgc.com/website/main/Channel.aspx?fcol=122002",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.xyjsgc.com/website/main/Channel.aspx?fcol=122005",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://www.xyjsgc.com/website/main/Channel.aspx?fcol=122007",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="陕西省咸阳市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang2", "shanxi_xianyang"])

    # driver = webdriver.Chrome()
    # url = "http://www.xyjsgc.com/website/main/Channel.aspx?fcol=122007"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    #
    # driver=webdriver.Chrome()
    # url = "http://www.xyjsgc.com/website/main/Channel.aspx?fcol=122007"
    # driver.get(url)
    # for i in range(1, 3):
    #     df=f1(driver, i)
    #     print(df.values)
