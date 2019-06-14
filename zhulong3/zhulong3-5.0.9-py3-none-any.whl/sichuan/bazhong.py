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

_name_ = "sichuan_bazhong"


def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='NewList']/li[1]/span/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        cnum = re.findall(r'page=(\d+)', url)[0]
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='NewList']/li[1]/span/a").get_attribute('href')[-10:]
        if "page" not in url:
            s = "page=%d" % (num) if num > 1 else "page=1"
            url = url + s
        elif num == 1:
            url = re.sub("page=[0-9]*", "page=1", url)
        else:
            s = "page=%d" % (num) if num > 1 else "page=1"
            url = re.sub("page=[0-9]*", s, url)
            # print(cnum)
        driver.get(url)
        locator = (By.XPATH, "//ul[@class='NewList']/li[1]/span/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("ul", class_='NewList')
    lis = div.find_all("li")
    data = []
    for li in lis:
        a = li.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        span = li.find("span", class_='date').text.strip()
        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = 'http://zfcxjsj.cnbz.gov.cn/' + link.split('/',maxsplit=1)[1]
        tmp = [title, span, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//ul[@class='NewList']/li[1]/span/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//a[@class='lastPage']")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    li = driver.find_element_by_xpath("//a[@class='lastPage']").get_attribute('href')

    total = int(re.findall(r'page=(\d+)', li)[0])
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='Details']")
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
    div = soup.find('div', id='Details')
    # div=div.find_all('div',class_='ewb-article')[0]
    return div


data = [

    ["gcjs_gqita_zhao_zhong_gg", "http://zfcxjsj.cnbz.gov.cn/list.php?id=45&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="四川省巴中市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang2", "sichuan_bazhong"])

    # driver = webdriver.Chrome()
    # url = "http://zfcxjsj.cnbz.gov.cn/list.php?id=45&page=1"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    #
    # driver=webdriver.Chrome()
    # url = "http://zfcxjsj.cnbz.gov.cn/list.php?id=45&page=1"
    # driver.get(url)
    # for i in range(1, 3):
    #     df=f1(driver, i)
    #     print(df.values)
