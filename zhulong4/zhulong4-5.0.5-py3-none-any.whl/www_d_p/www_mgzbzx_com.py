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

_name_ = "www_mgzbzx_com"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='lb-link']/ul/li[2]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        locator = (By.XPATH, "//div[@class='pag-txt']/em[1]")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@class='lb-link']/ul/li[2]/a").get_attribute('href')[-15:]
        if "index_" not in url:
            s = "index_%d" % (num) if num > 1 else "index"
            url = re.sub("index", s, url)
        elif num == 1:
            url = re.sub("index_[0-9]*", "index", url)
        else:
            s = "index_%d" % (num) if num > 1 else "index"
            url = re.sub("index_[0-9]*", s, url)
        driver.get(url)
        locator = (By.XPATH, "//div[@class='lb-link']/ul/li[2]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("div", class_='lb-link').ul
    lis = div.find_all('li', attrs={'class':''})
    data = []
    for li in lis:
        a = li.find("a")
        try:
            title = a['title'].strip()
        except:
            title = li.find('span', class_='bidLink  timeb on').text.strip()
        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = 'http://www.mgzbzx.com/' + link
        try:
            span = li.find("span", class_='bidDate').text.strip()
        except:
            try:
                span = re.findall(r'<!--span class="bidDate">(.*)</span-->', li)[0]
            except:
                span = '-'
        tmp = [title, span, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='lb-link']/ul/li[2]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='pag-txt']/em[last()]")
        num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@class='StdInputTable'] | //div[@class='mbox lpInfo']")
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
    div = soup.find('table', class_='StdInputTable')
    if div == None:
        div = soup.find('div', class_='mbox lpInfo')
    return div


data = [
    ["qy_zhaobiao_gg",
     "http://www.mgzbzx.com/cghw/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qy_zhongbiao_gg",
     "http://www.mgzbzx.com/cgzb/index.jhtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qy_zhaobiao_jingjia_gg",
     "http://www.mgzbzx.com/xszb/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'竞价招标'}), f2],

    ["qy_zhongbiao_lx1_gg",
     "http://www.mgzbzx.com/xszbgg/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx':'成交公告'}), f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="马钢集团", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang3", "www_mgzbzx_com"],pageloadtimeout=120,pageLoadStrategy="none")

    # driver = webdriver.Chrome()
    # url = "http://www.mgzbzx.com/xszbgg/index.jhtml"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    # #
    # driver=webdriver.Chrome()
    # url = "http://www.mgzbzx.com/cgzb/index.jhtml"
    # driver.get(url)
    # for i in range(65, 66):
    #     df=f1(driver, i)
    #     print(df.values)
    #     for i in df[2].values:
    #         f = f3(driver, i)
    #         print(f)
