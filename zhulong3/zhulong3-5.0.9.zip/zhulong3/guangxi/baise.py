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

from zhulong3.util.etl import est_html, est_meta, add_info

_name_ = "guangxi_baise"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='con']/ul/li[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@id='pages']/span")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    except:
        cnum = 1
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@class='con']/ul/li[1]//a").get_attribute('href')[-15:]

        if num == 1:
            url = re.sub("-[0-9]*\.html", "-1.html", url)
        else:
            s = "-%d.html" % (num) if num > 1 else "-1.html"
            url = re.sub("-[0-9]*\.html", s, url)
            # print(cnum)
        driver.get(url)
        locator = (By.XPATH, "//div[@class='con']/ul/li[1]//a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("div", class_='con').ul
    lis = div.find_all("li")
    data = []
    for li in lis:
        a = li.find('div', class_='xm').a
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        span = li.find("div", class_='gs').text.strip()
        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = 'http://zjw.baise.gov.cn/' + link
        ###
        dw = li.find("div", class_='dw').text.strip()
        tz = li.find("div", class_='tz').text.strip()
        jz = li.find("div", class_='jz').text.strip()
        td = {'jsdw': dw, 'jsdz':tz ,'jzsj': jz}
        if re.findall(r'^【(\w+?)】', title):
            lx = re.findall(r'^【(\w+?)】', title)[0]
            td['lx'] =lx
        info = json.dumps(td, ensure_ascii=False)
        tmp = [title, span, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='con']/ul/li[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@id='pages']/a[last()-1]")
        num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        num = 1
    total = int(num)
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='Article']")
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
    div = soup.find('div', id='Article')
    # div=div.find_all('div',class_='ewb-article')[0]
    return div


data = [
    #
    ["gcjs_yucai_piqian_gg", "http://zjw.baise.gov.cn/list-42-1.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gglx':'规划批前公示'}), f2],

    ["gcjs_yucai_pihou_gg", "http://zjw.baise.gov.cn/list-21-1.html",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gglx':'规划批后公示'}), f2],
    #
    ["gcjs_gqita_zhao_zhong_gg", "http://zjw.baise.gov.cn/list-22-1.html",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gglx':'招标标公示'}), f2],
    #
    ["gcjs_gqita_gg", "http://zjw.baise.gov.cn/list-24-1.html",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gglx':'其他公示'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广西省百色市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang2", "guangxi_baise"])

    # driver = webdriver.Chrome()
    # url = "http://zjw.baise.gov.cn/list-24-1.html"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    #
    # driver=webdriver.Chrome()
    # url = "http://zjw.baise.gov.cn/list-24-1.html"
    # driver.get(url)
    # for i in range(1, 6):
    #     df=f1(driver, i)
    #     print(df.values)
