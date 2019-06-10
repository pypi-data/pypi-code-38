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

_name_='beizhen'
def f1(driver, num):
    # 只有两页
    locator = (By.XPATH,'//td[@valign="top"]//table[@class="middle-nav2"]//a')
    WebDriverWait(driver,20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//td[@valign="top"]//table[@class="middle-nav2"]//a').get_attribute("href")[-20:]
    cnum = re.findall("(\d+)/",driver.find_element_by_xpath("//div[@class='paper']").text)[0]
    # print(val , cnum)
    # if int(cnum) != int(num):
    #     url = driver.current_url.split("&")[0] + "&Page=" + str(num)
    #     driver.get(url)
    #     WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    #     locator = (
    #         By.XPATH, '//div[@class="zw"]/ul/li/a[not(contains(string(),"%s"))]' % val)
    #     WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, '//td[@valign="top"]//table[@class="middle-nav2"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//td[@valign="top"]//table[@class="middle-nav2"]')
    for content in content_list:
        name = content.xpath(".//a/text()")[0].strip()
        ggstart_time = content.xpath(".//td[@align='right']/text()")[0][1:-1]

        url = "http://ggzx.bzs.gov.cn"+content.xpath(".//a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df

def f2(driver):
    locator = (By.CLASS_NAME,"paper")
    WebDriverWait(driver,20).until(EC.visibility_of_element_located(locator))
    total_page = re.findall("/(\d+)",driver.find_element_by_xpath("//div[@class='paper']").text)[0]
    driver.quit()
    return int(total_page)

def f3(driver, url):
    driver.get(url)
    locator = (By.CLASS_NAME, "rborder")
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
    div = soup.find('td',class_="rborder")
    # print(div)
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://ggzx.bzs.gov.cn/xinxi/jianshe/jiaoyi/",
     ["name", "ggstart_time", "href", "info"],f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://ggzx.bzs.gov.cn/xinxi/jianshe/jieguo/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]
#
# 辽宁-北镇 无法打开
# date ： 2019年4月4日16:53:02
#

def work(conp,**args):
    est_meta(conp, data=data, diqu="辽宁省北镇市",**args)
    est_html(conp, f=f3,**args)


if __name__ == "__main__":
    conp=["postgres", "since2015", "192.168.3.171", "liaoning", "beizhen"]
