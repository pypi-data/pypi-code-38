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

_name_='panjin'
def f1(driver, num):
    locator = (By.XPATH,'//div[contains(@id,"iframe")]/ul/li')
    WebDriverWait(driver,20).until(EC.presence_of_all_elements_located(locator))
    if "jtgc" not in driver.current_url and "slgc" not in driver.current_url:
        locator = (By.XPATH,'//div[@class="ewb-page"]//span[contains(@id,"index")]')
        WebDriverWait(driver,20).until(EC.presence_of_element_located(locator))
        cnum_temp = driver.find_element_by_xpath('//div[@class="ewb-page"]//span[contains(@id,"index")]').text
        cnum = cnum_temp.split('/')[0]
    else:
        try:
            locator = (By.XPATH,'//div[@class="ewb-page"]//span[contains(@id,"index")]')
            WebDriverWait(driver,20).until(EC.presence_of_element_located(locator))
            cnum_temp = driver.find_element_by_xpath('//div[@class="ewb-page"]//span[contains(@id,"index")]').text
            cnum = cnum_temp.split('/')[0]
        except:
            cnum = 1
    val = driver.find_element_by_xpath('//div[contains(@id,"iframe")]/ul/li[1]/a').get_attribute("href")[-20:]
    if int(cnum) != int(num):
        url = re.sub('\d+\.html',str(num)+'.html',driver.current_url)
        driver.get(url)
        locator = (
            By.XPATH, '//div[contains(@id,"iframe")]/ul/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[contains(@id,"iframe")]/ul/li')
    for content in content_list:
        name = content.xpath("./a/@title")[0].strip().strip('[').strip(']')
        ggstart_time = content.xpath("./span/text()")[0].strip()
        url = "http://202.97.171.175"+content.xpath("./a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    if len(data) == 1:data.append(['此条数据负责占位子','',''])
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df

def f2(driver):
    if "jtgc" not in driver.current_url and "slgc" not in driver.current_url:
        locator = (By.XPATH,'//div[@class="ewb-page"]//span[contains(@id,"index")]')
        WebDriverWait(driver,20).until(EC.presence_of_element_located(locator))
        total_temp = driver.find_element_by_xpath('//div[@class="ewb-page"]//span[contains(@id,"index")]').text
        total_page = total_temp.split('/')[1]
    else:
        try:
            locator = (By.XPATH,'//div[@class="ewb-page"]//span[contains(@id,"index")]')
            WebDriverWait(driver,20).until(EC.presence_of_element_located(locator))
            total_temp = driver.find_element_by_xpath('//div[@class="ewb-page"]//span[contains(@id,"index")]').text
            total_page = total_temp.split('/')[1]
        except:
            total_page = 1
    driver.quit()
    return int(total_page)

def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='news-article']")
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
    div = soup.find('div',class_="news-article")
    # print(div)
    return div


data = [
    ["zfcg_zhaobiao_gg",
     "http://202.97.171.175/zfcg/007001/1.html",
     ["name", "ggstart_time", "href", "info"],f1, f2],
    ["zfcg_biangeng_gg",
     "http://202.97.171.175/zfcg/007002/1.html",
     ["name", "ggstart_time", "href", "info"],f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://202.97.171.175/zfcg/007003/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["gcjs_zhaobiao_gg",
     "http://202.97.171.175/jsgc/008001/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://202.97.171.175/jsgc/008003/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://202.97.171.175/jsgc/008004/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_jiaotong_zhaobiao_gg",
     "http://202.97.171.175/jtgc/010001/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_jiaotong_zhongbiao_gg",
     "http://202.97.171.175/jtgc/010003/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_jiaotong_zhongbiaohx_gg",
     "http://202.97.171.175/jtgc/010004/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["gcjs_shuili_zhaobiao_gg",
     "http://202.97.171.175/slgc/011001/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuili_zhongbiao_gg",
     "http://202.97.171.175/slgc/011003/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuili_zhongbiaohx_gg",
     "http://202.97.171.175/slgc/011004/1.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],


]


def work(conp,**args):
    est_meta(conp, data=data, diqu="辽宁省盘锦市",**args)
    est_html(conp, f=f3,**args)


if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "liaoning", "panjin"])
    # driver = webdriver.Chrome()
    # driver.get("http://202.97.171.175/jtgc/010002/1.html")
    # for i in range(1,2):f1(driver,i)
    # print(f2(driver))

