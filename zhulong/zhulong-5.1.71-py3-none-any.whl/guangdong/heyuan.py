import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

import time

from zhulong.util.etl import est_html, est_meta, add_info

_name_ = "heyuan"


def f1(driver, num):
    locator = (By.CLASS_NAME, "ewb-list-bd")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        cnum = int(driver.find_element_by_xpath("//li[@class='ewb-page-li current']").text.strip())
    except:
        cnum = 1
    locator = (By.XPATH, "//ul/li[1][@class='ewb-com-item clearfix']//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    if num != cnum:
        val = driver.find_element_by_xpath("//ul/li[1][@class='ewb-com-item clearfix']//a").text
        if 'subpage' in url:
            s = '%d.html' % num if num > 1 else 'subpage.html'
            url = re.sub('subpage\.html', s, url)
        elif num == 1:
            url = re.sub('[0-9]*\.html', 'subpage.html', url)
        else:
            s = '%d.html' % num if num > 1 else 'subpage.html'
            url = re.sub('[0-9]*\.html', s, url)
        driver.get(url)
        locator = (By.XPATH, "//ul/li[1][@class='ewb-com-item clearfix']//a[string()!='%s']" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("div", class_="ewb-list-bd")

    lis = div.find_all("li", class_="clearfix")
    data = []
    for li in lis:
        a = li.find('a')
        span = li.find("span")
        name = a['title']
        ggstart_time = span.text.strip()
        href = "http://61.143.150.176" + a['href']
        info = ''.join([w.text.strip() for w in li.find_all('font')])
        info = json.dumps({'tag': info}, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    # df["info"]=None
    return df


def f2(driver):
    locator = (By.XPATH, "//ul/li[1][@class='ewb-com-item clearfix']//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//li[@id='index']/span")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath("//li[@id='index']/span").text.split("/")[1]

    total = int(total)

    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.CLASS_NAME, "ewb-list-bd")

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    before = len(driver.page_source)
    time.sleep(0.5)
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

    div = soup.find('div', class_='ewb-list-bd')
    # div=div.find_all('div',class_='ewb-article')[0]

    return div


data = [
    ["gcjs_gqita_gg", "http://61.143.150.176/jsgc/subpage.html", ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_gg", "http://61.143.150.176/zfcg/subpage.html", ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省河源市", **args)
    est_html(conp, f=f3, **args)


# 修改日期：2019/6/24
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guangdong", "heyuan"], num=1, headless=False)


