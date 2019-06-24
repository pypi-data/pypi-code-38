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

_name_='dandong'
def f1(driver, num):
    try:
        locator = (By.CLASS_NAME, "ewb-page")
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
        cnum = driver.find_element_by_xpath('//li[@class="ewb-page-li current"]').text
    except:
        cnum = 1
    locator = (By.XPATH, "//ul[@class='ewb-list']/li[1]/a")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//ul[@class='ewb-list']/li[1]/a").get_attribute("href")[-20:]
    if int(cnum) != int(num):
        url = re.sub("\/([\d\w]+)\.html",'/'+str(num)+'.html' if num!=1 else '/tradetab.html',driver.current_url)
        driver.get(url)

        locator = (By.XPATH, "//ul[@class='ewb-list']/li[1]/a")
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        locator = (By.XPATH, "//ul[@class='ewb-list']/li[1]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    locator = (By.CLASS_NAME, 'ewb-list')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('/html/body/div/ul/li')
    for content in content_list:
        name = content.xpath("./a")[0].xpath('string()').strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        url = "http://ddpas.dandong.gov.cn/"+content.xpath("./a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    try:
        WebDriverWait(driver,20).until(EC.visibility_of_element_located((By.XPATH,"//ul")))
        total_tmp = driver.find_element_by_xpath('//li[@class="ewb-page-li ewb-page-noborder ewb-page-num"]/span').text
        total_page = total_tmp.split('/')[1]
    except:
        total_page= 1
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.CLASS_NAME, "ewb-container")
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
    div = soup.find(id="header").find_next_sibling("div",class_="ewb-container")

    return div

data = [
    ["zfcg_zhaobiao_gg",
     "http://ddpas.dandong.gov.cn/ddggzy/jyxx/002001/002001001/tradetab.html",
     ["name", "ggstart_time", "href", "info"],f1, f2],
    ["zfcg_gqita_zhong_liu_gg",
     "http://ddpas.dandong.gov.cn/ddggzy/jyxx/002001/002001005/tradetab.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",#
     "http://ddpas.dandong.gov.cn/ddggzy/jyxx/002001/002001002/tradetab.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_dyly_gg",#
     "http://ddpas.dandong.gov.cn/ddggzy/jyxx/002001/002001003/tradetab.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_gg",
     "http://ddpas.dandong.gov.cn/ddggzy/jyxx/002002/002002001/tradetab.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://ddpas.dandong.gov.cn/ddggzy/jyxx/002002/002002002/tradetab.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://ddpas.dandong.gov.cn/ddggzy/jyxx/002002/002002003/tradetab.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["yiliao_zhaobiao_gg",#
     "http://ddpas.dandong.gov.cn/ddggzy/jyxx/002005/002005001/tradetab.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["yiliao_zhongbiao_gg",#
     "http://ddpas.dandong.gov.cn/ddggzy/jyxx/002005/002005002/tradetab.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp,**args):
    est_meta(conp, data=data, diqu="辽宁省丹东市",**args)
    est_html(conp, f=f3,**args)


if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "liaoning", "dandong"])
