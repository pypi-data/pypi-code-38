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
from zhulong.util.etl import est_html, est_meta
import time

_name_ = 'yingkou'


def f1(driver, num):
    locator = (By.XPATH, '//td[@align="center"]/font[2]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    page_temp = driver.find_element_by_xpath('//td[@align="center"]').text
    cnum = re.findall("(\d+)\/", page_temp)[0]
    locator = (By.XPATH, '//td[@class="ListTitle"]/a')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//tr[1]/td[@class="ListTitle"]/a').get_attribute("href")[-40:]
    if int(cnum) != int(num):
        url = '&'.join(driver.current_url.split("&")[:-1]) + "&Page=" + str(num)
        driver.get(url)
        locator = (
            By.XPATH, '//tr[1]/td[@class="ListTitle"]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    locator = (By.CLASS_NAME, 'ListTitle')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table[@width="100%"]/tbody/tr[contains(string(),"-")]')
    for content in content_list:
        name = content.xpath("./td/a/text()")[0].strip()
        ggstart_time = content.xpath("./td[2]/text()")[0].strip()
        url = "http://www.ccgp-yingkou.gov.cn/Html/" + content.xpath("./td/a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df



def f2(driver):
    locator = (By.XPATH, '//td[@align="center"]/font[2]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    page_temp = driver.find_element_by_xpath('//td[@align="center"]').text
    total_page = re.findall("\/(\d+)", page_temp)[0]


    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)

    if 'tab topd' in driver.page_source:
        locator = (By.XPATH, "//table[@class='tab topd']")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        flag = True
    elif "page_r_mid_v" in driver.page_source:
        locator = (By.XPATH, "//div[@class='page_r_mid_v']")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        flag = 3

    else:
        try:
            locator = (By.XPATH, "//td[@align='left']/table")
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
            flag = False
        except:
            locator = (By.ID, "tblInfo")
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
            flag = 2

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
    if flag == 2:
        div = soup.find('div', id="tblInfo")
    elif flag == True:
        div = soup.find('table', class_="tab topd")
    elif flag == 3:
        div = soup.find("div",class_="page_r_mid_v")
    else:
        div = soup.find(attrs={"align": "left"})
    return div



data = [
    ["zfcg_zhaobiao_gg",
     "http://www.ccgp-yingkou.gov.cn/Html/NewsList.asp?SortID=152&SortPath=0,98,120,152,&Page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://www.ccgp-yingkou.gov.cn/Html/NewsList.asp?SortID=153&SortPath=0,98,120,153,&Page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://www.ccgp-yingkou.gov.cn/Html/NewsList.asp?SortID=156&SortPath=0,98,121,156,&Page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_gg",
     "http://www.ccgp-yingkou.gov.cn/Html/NewsList.asp?SortID=152&SortPath=0,98,120,152,&Page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://www.ccgp-yingkou.gov.cn/Html/NewsList.asp?SortID=153&SortPath=0,98,120,153,&Page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://www.ccgp-yingkou.gov.cn/Html/NewsList.asp?SortID=154&SortPath=0,98,120,154,&Page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]
"""
http://www.ccgp-yingkou.gov.cn    网站无法访问
时间：2019年5月20日15:28:07

"""

def work(conp, **args):
    est_meta(conp, data=data, diqu="辽宁省营口市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp=["postgres", "since2015", "192.168.3.171", "liaoning", "yingkou"]
    import sys
    arg=sys.argv
    if len(arg) >3:
        work(conp,num=int(arg[1]),total=int(arg[2]),html_total=int(arg[3]))
    elif len(arg) == 2:
        work(conp, html_total=int(arg[1]))
    else:
        work(conp)