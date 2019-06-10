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

_name_ = "shanxi_xian"


def f1(driver, num):
    locator = (By.XPATH, "//table[@class='list_style']/tbody/tr[2]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        locator = (By.XPATH, "//table[@class='btn_style']/tbody/tr[2]/td")
        li = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(re.findall(r'第 (\d+) 页', li)[0])
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@class='list_style']/tbody/tr[2]/td/a").get_attribute('href')[-20:]
        driver.execute_script('goPage({})'.format(num))

        locator = (By.XPATH, "//table[@class='list_style']/tbody/tr[2]/td/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("table", class_='list_style').tbody
    lis1 = div.find_all("tr", class_='dg_liststyle1')
    lis2 = div.find_all("tr", class_='dg_liststyle2')
    lis = lis1 + lis2
    data = []
    for li in lis:
        a = li.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        span = li.find_all("td", attrs={'width':''})[-1].text.strip()
        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = 'http://www.xacin.com.cn/XianGcjy/web/tender/' + link
        tmp = [title, span, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//table[@class='list_style']/tbody/tr[2]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//table[@class='btn_style']/tbody/tr[2]/td")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    li = driver.find_element_by_xpath("//table[@class='btn_style']/tbody/tr[2]/td").text.strip()
    total = int(re.findall(r'共 (\d+) 页', li)[0])
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@class='text_style']")
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
    div = soup.find('table', class_='text_style')
    # div=div.find_all('div',class_='ewb-article')[0]
    return div


data = [
    ["gcjs_yucai_baojian_gg",
     "http://www.xacin.com.cn/XianGcjy/web/tender/shed_gc.jsp?gc_type=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gglx':'报建信息'}), f2],

    ["gcjs_yucai_jinchang_gg",
     "http://www.xacin.com.cn/XianGcjy/web/tender/shed_gc.jsp?gc_type=2",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gglx':'进场登记'}), f2],

    ["gcjs_yucai_gg",
     "http://www.xacin.com.cn/XianGcjy/web/tender/shed_gc.jsp?gc_type=7",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gglx':'招标备案'}), f2],

    ["gcjs_zhaobiao_gg",
     "http://www.xacin.com.cn/XianGcjy/web/tender/shed_gc.jsp?gc_type=5",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zgysjg_gg",
     "http://www.xacin.com.cn/XianGcjy/web/tender/shed_gc.jsp?gc_type=3",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_kongzhijia_gg",
     "http://www.xacin.com.cn/XianGcjy/web/tender/shed_gc.jsp?gc_type=4",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
    "http://www.xacin.com.cn/XianGcjy/web/tender/shed_gc.jsp?gc_type=6",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_hetong_gg",
     "http://www.xacin.com.cn/XianGcjy/web/tender/shed_gc.jsp?gc_type=8",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="陕西省西安市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang2", "shanxi_xian"])

    # driver = webdriver.Chrome()
    # url = "http://www.xacin.com.cn/XianGcjy/web/tender/shed_gc.jsp?gc_type=2"
    # driver.get(url)
    # df = f2(driver)
    # print(df)

    # driver=webdriver.Chrome()
    # url = "http://www.xacin.com.cn/XianGcjy/web/tender/shed_gc.jsp?gc_type=5"
    # driver.get(url)
    # for i in range(1, 3):
    #     df=f1(driver, i)
    #     print(df.values)
