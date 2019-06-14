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

_name_ = "shanxi_baoji"


def f1(driver, num):
    locator = (By.XPATH, "//div[@id='article_list']/ul/li[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        li = driver.find_element_by_xpath("//a[@id='totalpage']").text.strip()
        cnum = int(re.findall(r'(\d+) /', li)[0])
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@id='article_list']/ul/li[1]//a").get_attribute('href')[-10:]
        if num == 1:
            url = re.sub("0-[0-9]*", "0-1", url)
        else:
            s = "0-%d" % (num) if num > 1 else "0-1"
            url = re.sub("0-[0-9]*", s, url)
            # print(cnum)
        driver.get(url)
        locator = (By.XPATH, "//div[@id='article_list']/ul/li[1]//a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("div", id='article_list').ul
    lis = div.find_all("li")
    data = []
    for li in lis:
        a = li.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        span = li.find("span").text.strip()
        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = 'http://www.bjszjsgl.com/' + link.split('/',maxsplit=1)[1]
        tmp = [title, span, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@id='article_list']/ul/li[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//a[@id='totalpage']")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    li = driver.find_element_by_xpath("//a[@id='totalpage']").text.strip()
    total = int(re.findall(r'/ (\d+)', li)[0])
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='large_con']")
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
    div = soup.find('div', class_='large_con')
    # div=div.find_all('div',class_='ewb-article')[0]
    return div


data = [

    ["gcjs_gqita_zhao_zhong_gg", "http://www.bjszjsgl.com/infor.php?51-0-1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="陕西省宝鸡市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang2", "shanxi_baoji"])


