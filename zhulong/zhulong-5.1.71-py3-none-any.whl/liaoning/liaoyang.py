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

_name_='liaoyang'
def f1(driver, num):
    locator = (By.XPATH,"//li[@class='no-active']/a")
    WebDriverWait(driver,20).until(EC.presence_of_element_located(locator))
    page_temp = driver.find_element_by_xpath("//li[@class='no-active']/a").text
    cnum = re.findall("(\d+)\/",page_temp)[0]
    locator = (By.XPATH, "//ul[@id='info']/li")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//ul[@id='info']/li[1]/div[@class='title']/a").text
    if int(cnum) != int(num):
        driver.find_element_by_xpath('//div[@id="jumpDiv"]/input').clear()
        driver.find_element_by_xpath('//div[@id="jumpDiv"]/input').send_keys(num)
        driver.find_element_by_id('jump').click()
        locator = (
            By.XPATH, '//ul[@id="info"]/li[1]/div[@class="title"]/a[not(contains(string(),"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//ul[@id='info']/li")
    for content in content_list:
        name = content.xpath("./div[@class='title']/a/text()")[0].strip()
        logicId = re.findall("\d+",content.xpath("./@onclick")[0].strip())[0]

        url_temp = 'http://ggzyjy.liaoyang.gov.cn/' + "releaseCms/dynamicArticle.do?siteCode=GGZY&logicId="+logicId+"&selfSiteSiteId=152341388865840&columnLogicId=152341388865850&isWap=0&navigationSiteId=152696583127019"
        try:
            url = requests.get(url_temp,allow_redirects=False).headers['location']
        except:url = url_temp
        # print(logicId)
        ggstart_time = time.strftime('%Y-',time.localtime(int(logicId)//100000 if len(logicId) == 15 else int(logicId)//10000)) + content.xpath("./div[@class='date']/text()")[0]
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)

    df = pd.DataFrame(data=data)
    df["info"] = None
    return df

def f2(driver):
    locator = (By.XPATH,"//li[@class='no-active']/a")
    WebDriverWait(driver,20).until(EC.presence_of_element_located(locator))
    page_temp = driver.find_element_by_xpath("//li[@class='no-active']/a").text
    total_page = re.findall("\/(\d+)",page_temp)[0]
    driver.quit()
    return int(total_page)

def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, "//div[@class='colbor01'][string-length()>30]")
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
    div = soup.find('div', class_='colbor01')
    return div

data = [
    ["zfcg_zhaobiao_gg",
     "http://www.liaoyang.gov.cn/OpenData/opendata/ggzy/list/PurchaseList1.html",
     ["name", "ggstart_time", "href", "info"],f1, f2],
    ["zfcg_gqita_zhong_liu_gg",
     "http://www.liaoyang.gov.cn/OpenData/opendata/ggzy/list/PurchaseList4.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://www.liaoyang.gov.cn/OpenData/opendata/ggzy/list/PurchaseList2.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_gg",
     "http://www.liaoyang.gov.cn/OpenData/opendata/ggzy/list/ConstructionList1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://www.liaoyang.gov.cn/OpenData/opendata/ggzy/list/ConstructionList2.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://www.liaoyang.gov.cn/OpenData/opendata/ggzy/list/ConstructionList3.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp,**args):
    est_meta(conp, data=data, diqu="辽宁省辽阳市",**args)
    est_html(conp, f=f3,**args)


if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.4.175", "liaoning", "liaoyang"],num=4)
    # url = "http://www.liaoyang.gov.cn/OpenData/opendata/ggzy/list/PurchaseList1.html"
    # driver = webdriver.Chrome()
    # driver.get(url)
    # for i in range(1,50):f1(driver,i)
