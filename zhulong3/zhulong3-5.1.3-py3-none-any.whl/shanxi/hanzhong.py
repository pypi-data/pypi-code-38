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

_name_ = "shanxi_hanzhong"


def f1(driver, num):
    locator = (By.XPATH, '(//span[@class="a01"])[1]/a | //table[@width="96%"]/tbody/tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        locator = (By.XPATH, "//div[@id='page']/em")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath('(//span[@class="a01"])[1]/a | //table[@width="96%"]/tbody/tr[1]//a').get_attribute('href')[-15:]
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
        try:
            locator = (By.XPATH, "(//span[@class='a01'])[1]/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            locator = (By.XPATH, "//table[@width='96%']/tbody/tr[1]//a[not(contains(@href, '{}'))]".format(val))
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("table", width='96%')
    if div == None:
        div = soup.find("table", width='90%')
    lis = div.tbody.find_all('tr')
    data = []
    for li in lis:
        a = li.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()

        span = li.find_all("td")[-1].text.strip()

        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = 'http://www.hzzbb.com/' + link
        info = {}
        if '至' in span:
            span2 = re.split('至', span)[1]
            if '止' in span2: span2 = re.split('止', span2)[0]
            info['endtimes'] = span2
            span = re.split('至', span)[0]
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:
            info = None
        tmp = [title, span, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    locator = (By.XPATH, '(//span[@class="a01"])[1]/a | //table[@width="96%"]/tbody/tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@id='page']/a[last()]")
        num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@id='table1'] | //table[@height='20']")
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
    div = soup.find('table', id='table1')
    if div == None:
        div = soup.find('table', height='20')
    # div=div.find_all('div',class_='ewb-article')[0]
    return div



data = [
    ["gcjs_zhaobiao_gg",
     "http://www.hzzbb.com/zhaobiao.asp?fd=&lb=&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zgysjg_gg",
     "http://www.hzzbb.com/yushen.asp?fd=&lb=&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_fabao_gg",
     "http://www.hzzbb.com/fabaogs.asp?fd=&page=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gglx':'直接发包公示'}), f2],

    ["gcjs_zhongbiao_gg",
     "http://www.hzzbb.com/zhongbiao.asp?fd=&zhob=1&page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]



def work(conp, **args):
    est_meta(conp, data=data, diqu="陕西省汉中市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang2", "shanxi_hanzhong"])

    # driver = webdriver.Chrome()
    # url = "http://www.hzzbb.com/zhaobiao_detail.asp?id=1412"
    # driver.get(url)
    # f = f3(driver, url)
    # print(f)
    # df = f2(driver)
    # print(df)
    #
    # driver=webdriver.Chrome()
    # url = "http://www.hzzbb.com/zhongbiao.asp?fd=&zhob=1&page=1"
    # driver.get(url)
    # for i in range(1, 3):
    #     df=f1(driver, i)
    #     print(df.values)
