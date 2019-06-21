import re

import requests
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong3.util.etl import est_html, est_meta
import time

_name_ = 'shanxi1_changzhi'


def f1(driver, num):

    locator = (By.XPATH, "//table[@id='DG_Type']/tbody/tr[not(contains(@align,'center'))][1]/td/a")
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-15:]

    locator = (By.XPATH, "//span[@id='Lb_State']/b[1]")
    cnum = int(WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text)

    if int(cnum) != int(num):
        locator = (By.XPATH,"//input[@id='Tb_Go']")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).clear()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).send_keys(num)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//input[@id="Bt_Go"]'))).click()


        locator = (By.XPATH, '//table[@id="DG_Type"]/tbody/tr[not(contains(@align,"center"))][1]/td/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//table[@id='DG_Type']/tbody/tr[not(contains(@align,'center'))][not(contains(@align,'right'))]")
    for content in content_list:
        name = content.xpath("./td/a/text()")[0].strip()
        ggstart_time = content.xpath("./td[4]/text()")[0].strip()
        url = "http://www.czjjzx.net/"+content.xpath("./td/a/@href")[0].strip('.')
        temp = [name, ggstart_time, url]
        data.append(temp)

    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//span[@id='Lb_State']/b[2]")
    total_page = int(WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text)
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    time.sleep(0.1)

    locator = (By.XPATH, "//td[@valign='middle']")
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
    soup = BeautifulSoup(page, 'lxml')
    div = soup.find('div', class_='con1')
    if not div: div = soup.find('td', valign='middle')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.czjjzx.net/type.aspx?typeid=3",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.czjjzx.net/type.aspx?typeid=4",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://www.czjjzx.net/type.aspx?typeid=5",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="山西省长治市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "shanxi1_changzhi"]
    work(conp,num=2)
    # driver = webdriver.Chrome()
    # driver.get("http://www.czjjzx.net/type.aspx?typeid=3")
    # print(f2(driver))

    # f1(driver,5)
    # f1(driver,2)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://zjj.sxxz.gov.cn/zbgg/201902/t20190227_2715616.html'))
    # driver.close()
