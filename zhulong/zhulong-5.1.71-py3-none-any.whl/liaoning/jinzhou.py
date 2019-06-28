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

_name_='jinzhou'
def f1(driver, num):

    locator = (By.ID,'index')
    WebDriverWait(driver,20).until(EC.presence_of_element_located(locator))
    cnum = int(driver.find_element_by_id("index").text.split('/')[0])
    locator = (By.XPATH, '//*[@id="jt"]/ul/li[1]/a')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//*[@id="jt"]/ul/li[1]/a').get_attribute("href")[-20:]
    if int(cnum) != int(num):
        url = re.sub('\d+\.html',str(num)+'.html',driver.current_url)
        driver.get(url)

        locator = (By.XPATH, '//*[@id="jt"]/ul/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    locator = (By.CLASS_NAME, 'ewb-mess-items')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//ul[@class="ewb-mess-items"]/li')
    for content in content_list:
        name = content.xpath("./a")[0].xpath("string(.)").strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        url = "http://ggzy.jz.gov.cn"+content.xpath("./a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.ID,'index')
    WebDriverWait(driver,20).until(EC.presence_of_element_located(locator))
    total_page = int(driver.find_element_by_id("index").text.split('/')[1])

    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    if "ewb-info-bd" in driver.page_source:
        locator = (By.CLASS_NAME, "ewb-info-bd")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        flag = True
    elif "tblInfo" in driver.page_source:
        locator = (By.ID, "tblInfo")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        flag = False
    else:
        locator = (By.ID, "news-article")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        flag = 3
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
    if flag == True:
        div = soup.find('div',class_="ewb-info-bd")
    elif flag == 3:
        div = soup.find('div',class_="news-article")
    else:
        div = soup.find("table", id="tblInfo")
    return div


data = [
    ["zfcg_zhaobiao_gg",
     "http://ggzy.jz.gov.cn/jyxx/077001/077001001/1.html",
     ["name", "ggstart_time", "href", "info"],f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://ggzy.jz.gov.cn/jyxx/077001/077001002/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://ggzy.jz.gov.cn/jyxx/077001/077001003/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_gg",
     "http://ggzy.jz.gov.cn/jyxx/077002/077002001/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://ggzy.jz.gov.cn/jyxx/077002/077002002/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://ggzy.jz.gov.cn/jyxx/077002/077002003/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["yiliao_zhaobiao_gg",
     "http://ggzy.jz.gov.cn/jyxx/077005/077005001/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["yiliao_zhongbiao_gg",
     "http://ggzy.jz.gov.cn/jyxx/077005/077005002/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp,**args):
    est_meta(conp, data=data, diqu="辽宁省锦州市",**args)
    est_html(conp, f=f3,**args)


if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "liaoning", "jinzhou"])
    # url = "http://ggzy.jz.gov.cn/jyxx/077002/077002001/1.html"
    # driver = webdriver.Chrome()
    # driver.get(url)
    #
    # for i in range(1,118):f1(driver,i)
    # driver.quit()