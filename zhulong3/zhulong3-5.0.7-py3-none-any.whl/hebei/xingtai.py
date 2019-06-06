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

_name_ = 'hebei_xingtai'


def f1(driver, num):
    locator = (By.XPATH, '//*[@id="div2_1"]/table/tbody//table[2]/tbody/tr/td')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath('//*[@id="div2_1"]/table/tbody//table[2]/tbody/tr/td/strong[2]').text
    locator = (By.XPATH, '//*[@id="div2_1"]//tbody//table[1]//tr[position() mod 2=1]')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//*[@id="div2_1"]//tbody//table[1]//tr[position() mod 2=1][1]//td/span/a').get_attribute("href")[-20:]
    # print("cnum",cnum,"val",val)
    if int(cnum) != int(num):             # index_
        url = re.sub(r"Page=\d+",'Page='+str(num),driver.current_url)
        # print(url)
        driver.get(url)
        locator = (By.XPATH, '//*[@id="div2_1"]//tbody//table[1]//tr[position() mod 2=1][1]//td/span/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, '//*[@id="div2_1"]//tbody//table[1]//tr[position() mod 2=1]')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//*[@id="div2_1"]//tbody//table[1]//tr[position() mod 2=1]')
    for content in content_list:
        name = content.xpath("./td/span/a/text()")[0].strip()
        ggstart_time = content.xpath("./td[last()]/span/text()")[0].strip().replace('.','-')
        url = 'http://www.xtjsj.gov.cn/'+content.xpath("./td/span/a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//*[@id="div2_1"]/table/tbody//table[2]/tbody/tr/td')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    page_temp = driver.find_element_by_xpath('//*[@id="div2_1"]/table/tbody//table[2]/tbody/tr/td').text
    total_page = re.findall("\/(\d+) ", page_temp)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)                    #cxdalist_hqbcon
    time.sleep(0.1)
    locator = (By.XPATH, '//*[@id="div2_1"]/table/tbody/tr/td/div')
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
    div = soup.find('div', id='div2_1')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.xtjsj.gov.cn/bsinfolist.asp?sortid=5&Page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://www.xtjsj.gov.cn/bsinfolist.asp?sortid=6&Page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="河北省邢台市", **args)
    est_html(conp, f=f3, **args)



if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "hebei_xingtai"]
    work(conp,num=4,headless=False,pageloadstrategy='none')
    # driver = webdriver.Chrome()
    # driver.get("http://www.xtjsj.gov.cn/bsinfolist.asp?sortid=5&Page=1")
    # f1(driver,5)
    # f1(driver,1)
    # print(f3(driver, 'http://www.xtjsj.gov.cn/bsinfoshow.Asp?ID=2014'))
    # print(f2(driver))

