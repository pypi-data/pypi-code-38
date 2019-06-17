import re
from dateutil.parser import parse
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

_name_='huludao'
def f1(driver, num):
    if "404 Not Found" in driver.page_source:return
    if "thirdpage" in driver.current_url:
        cnum = 1
    else:
        locator = (By.XPATH,'//li[@class="ewb-page-li "]')
        WebDriverWait(driver,20).until(EC.presence_of_element_located(locator))
        cnum = driver.find_element_by_xpath('//li[@class="ewb-page-li current"]').text
    locator = (By.XPATH, '//ul[@class="wb-data-item"]/li/div/a')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//ul[@class="wb-data-item"]/li/div/a').get_attribute("href")[-20:]
    if int(cnum) != int(num):
        url = '/'.join(driver.current_url.split("/")[:-1]) + "/" + str(num) +".html"
        driver.get(url)
        locator = (
            By.XPATH, '//ul[@class="wb-data-item"]/li/div/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    locator = (By.CLASS_NAME, 'wb-data-item')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//ul[@class="wb-data-item"]/li')
    for content in content_list:
        name = content.xpath("./div/a")[0].xpath("string(.)").strip()
        ggstart_time = str(parse(content.xpath("./div/a/@href")[0].strip().split('/')[4])).split(" ")[0]
        url = "http://www.hldggzyjyzx.com.cn"+content.xpath("./div/a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df

def f2(driver):
    try:
        locator = (By.XPATH,'//li[@class="ewb-page-li "][last()]')
        WebDriverWait(driver,20).until(EC.presence_of_element_located(locator))
        total_page = driver.find_element_by_xpath('//li[@class="ewb-page-li "][last()]').text
    except:
        total_page = 1
    driver.quit()
    return int(total_page)

def f3(driver, url):
    driver.get(url)
    locator = (By.CLASS_NAME, "ewb-con")
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
    div = soup.find('div',class_="ewb-con")
    # print(div)
    return div


data = [
    ["zfcg_zhaobiao_gg",
     "http://www.hldggzyjyzx.com.cn/jyxx/003002/003002001/thirdpage.html",
     ["name", "ggstart_time", "href", "info"],f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://www.hldggzyjyzx.com.cn/jyxx/003002/003002003/thirdpage.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://www.hldggzyjyzx.com.cn/jyxx/003002/003002002/thirdpage.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["gcjs_zhaobiao_gg",
     "http://www.hldggzyjyzx.com.cn/jyxx/003001/003001001/thirdpage.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://www.hldggzyjyzx.com.cn/jyxx/003001/003001003/thirdpage.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://www.hldggzyjyzx.com.cn/jyxx/003001/003001004/thirdpage.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp,**args):
    est_meta(conp, data=data, diqu="辽宁省葫芦岛市",**args)
    est_html(conp, f=f3,**args)
#
# 辽宁- 葫芦岛  网站打不开。
# date ：2019年4月4日17:13:41
#
# 2019年4月10日17:50:37  又好了。

if __name__ == "__main__":

    conp=["postgres", "since2015", "192.168.3.171", "liaoning", "huludao"]
    work(conp,num=4,total=10)