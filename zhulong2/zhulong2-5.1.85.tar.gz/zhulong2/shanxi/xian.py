import random
from collections import OrderedDict
import pandas as pd
import re
import requests
from lxml import etree
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
from zhulong2.util.etl import est_html, est_meta, add_info, est_meta_large


_name_ = "shanxi_xian"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='ddlist']/ul/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//td[@id='fanye1033']")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = re.findall(r'(\d+)/', st)[0]
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@class='ddlist']/ul/li[1]/a").get_attribute('href')[-12:]
        driver.find_element_by_xpath("//input[@class='defaultInputStyle']").clear()
        driver.find_element_by_xpath("//input[@class='defaultInputStyle']").send_keys(num)
        driver.execute_script('javascript:a1033_gopage_fun()')
        locator = (By.XPATH, "//div[@class='ddlist']/ul/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    ul = soup.find("div", class_="ddlist").ul
    trs = ul.find_all("li")
    data = []
    for tr in trs:
        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        td = tr.find('span').text.strip()
        link = 'http://xaczj.xa.gov.cn/'+a['href'].rsplit('../', maxsplit=1)[1]
        tmp = [title, td, link]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='ddlist']/ul/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//td[@id='fanye1033']")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'/(\d+)', st)[0]
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='wzcontent'][string-length()>30]")
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
    div1 = soup.find('div', class_='wztitle')
    div2 = soup.find('div', class_='wzcontent')
    div = str(div1)+str(div2)
    return div


data = [
    ["zfcg_zhaobiao_gg",
     "http://xaczj.xa.gov.cn/zfcg/sjcggg/dzjjgg.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'网上竞价'}), f2],
    #
    ["zfcg_zhongbiao_gg",
     "http://xaczj.xa.gov.cn/zfcg/sjcggg/dzjjcjgg.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'网上竞价'}), f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="陕西省西安市", **args)
    est_html(conp, f=f3, **args)


# 网站新增：http://xaczj.xa.gov.cn/zfcg/sjcggg/dzjjcjgg.htm
# 修改时间：2019/6/20
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "xian"], pageloadtimeout=120)

    # driver = webdriver.Chrome()
    # for d in data:
    #     driver.get(d[1])
    #     print(d[1])
    #     df = f2(driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     df = f1(driver,3)
    #     print(df.values)
    #     for j in df[2].values:
    #         df = f3(driver, j)
    #         print(df)