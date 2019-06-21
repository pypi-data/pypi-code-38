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

_name_ = "zb_crlintex_com"


def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='ul2']/li[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        cnum = re.findall(r'pageIndex=(\d+)', url)[0]
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='ul2']/li[1]//a").get_attribute('href')[-20:]
        if num == 1:
            url = re.sub("pageIndex=[0-9]*", "pageIndex=1", url)
        else:
            s = "pageIndex=%d" % (num) if num > 1 else "pageIndex=1"
            url = re.sub("pageIndex=[0-9]*", s, url)
        driver.get(url)

        locator = (By.XPATH, "//ul[@class='ul2']/li[1]//a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("ul", class_='ul2')
    lis = div.find_all('li')
    data = []
    for li in lis:
        a = li.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = 'http://zb.crlintex.com' + link
        span = li.find('span', class_='floatright span2').text.strip()
        span = re.findall(r'\[(.*)\]', span)[0]

        span2 = li.find('span', class_='span1').text.strip()
        span2 = re.findall(r'\[(.*)\]', span2)[0]
        info = json.dumps({'zblx':span2}, ensure_ascii=False)
        tmp = [title, span, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    locator = (By.XPATH, "//ul[@class='ul2']/li[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='divpage']/div/a[last()-2]")
        num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='box3 floatleft']")
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
    div = soup.find('div', class_='box3 floatleft')
    return div



data = [
    ["qy_gqita_zhao_liu_gg",
     "http://zb.crlintex.com/Home/cgxx?pageIndex=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="华润(集团)有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang3", "zb_crlintex_com"])

    # driver = webdriver.Chrome()
    # url = "http://zb.crlintex.com/Home/cgxx?pageIndex=1"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    #
    # driver=webdriver.Chrome()
    # url = "http://zb.crlintex.com/Home/cgxx?pageIndex=1"
    # driver.get(url)
    # for i in range(1, 3):
    #     df=f1(driver, i)
    #     print(df.values)
