import json
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

_name_ = 'jilin_shenghui'


def f1(driver, num):
    locator = (By.XPATH, "//li[@class='page-number active']")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath("//li[@class='page-number active']/a").text
    locator = (By.XPATH, '//table[contains(@id,"Table")]/tbody/tr[1]/td[2]')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//table[contains(@id,"Table")]/tbody/tr[1]/td[2]').text
    locator = (By.XPATH, '//table[contains(@id,"Table")]/tbody/tr')

    time.sleep(3)
    while int(cnum) != int(num):
        locator = (By.XPATH, "//li[@class='page-next']/a")
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        element = driver.find_element_by_xpath("//li[@class='page-next']/a")
        driver.execute_script("arguments[0].click()",element)

        cnum = driver.find_element_by_xpath("//li[@class='page-number active']/a").text
        locator = (By.XPATH, '//table[contains(@id,"Table")]/tbody/tr[1]/td[2][not(contains(@href,"%s"))]' % val)
        # locator = (By.XPATH,"//div[@style='top: 41px; display: block;']")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    prepare(driver)
    content_list = body.xpath('//table[contains(@id,"Table")]/tbody/tr')
    for i,content in enumerate(content_list):
        name = content.xpath("./td[1]/text()")[0].strip()
        project_code = content.xpath("./td[2]/text()")[0].strip()
        project_type = content.xpath("./td[3]/text()")[0].strip()
        project_area = content.xpath("./td[4]/text()")[0].strip()
        ggstart_time = content.xpath("./td[last()-1]/text()")[0].strip()
        url = get_url(driver,i)
        info = json.dumps({"project_code":project_code,"project_type":project_type,'project_area':project_area})

        temp = [name, ggstart_time,url,info]
        data.append(temp)
        # print('temp',temp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, "//li[@class='page-last']/a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_page = driver.find_element_by_xpath("//li[@class='page-last']/a").text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='container']")
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
    div = soup.find('div', class_='container')
    return div




def prepare(driver):
    """

    :return:
    """
    if 'iframe_manage' in driver.page_source:
        frame = driver.find_element_by_id("iframe_manage")
        driver.switch_to_frame(frame)
    locator = (By.XPATH,"//span[@class='page-size']")
    WebDriverWait(driver,10).until(EC.visibility_of_element_located(locator))
    page_size = driver.find_element_by_xpath("//span[@class='page-size']").text
    if int(page_size)!= 100:
        click1 = driver.find_element_by_xpath("//button[@class='btn btn-default btn-outline dropdown-toggle']")
        driver.execute_script('arguments[0].click()',click1)
        click2 = driver.find_element_by_xpath('//li[@role="menuitem"]/a[contains(text(),"100")]')
        driver.execute_script('arguments[0].click()',click2)


def get_url(driver,i):
    time.sleep(2)
    driver.find_element_by_xpath('//table[contains(@id,"Table")]/tbody/tr[%s]/td[last()]/a'%(i+1)).click()
    windows = driver.window_handles
    driver.switch_to_window(windows[-1])
    url = driver.current_url
    driver.close()
    driver.switch_to_window(driver.window_handles[0])
    prepare(driver)
    return url

def before(f):
    def inner(*args):
        driver = args[0]
        prepare(driver)
        return f(*args)
    return inner

data = [
    ["gcjs_zhaobiao_gg",
     "http://www.jljsw.gov.cn/zbgg/index.jhtml",  # http://www.jljsw.gov.cn:20001/web/bblistdata?sortOrder=desc&pageSize=14&pageNumber=1&_=1551778523007
     ["name", "ggstart_time", "href" ,"info"], before(f1), before(f2)],
    ["gcjs_biangeng_gg",
     "http://www.jljsw.gov.cn/bggg/index.jhtml",  # http://www.jljsw.gov.cn:20001/web/alterationShow/list?sortOrder=desc&pageSize=14&pageNumber=1&_=1551778604885
     ["name", "ggstart_time", "href" ,"info"], before(f1), before(f2)],
    ["gcjs_zhongbiaohx_gg",
     "http://www.jljsw.gov.cn/zbhxrgs/index.jhtml", # http://www.jljsw.gov.cn:20001/web/candidateShow/list?sortOrder=desc&pageSize=14&pageNumber=1&_=1551778629317
     ["name", "ggstart_time", "href" ,"info"], before(f1), before(f2)],
    ["gcjs_zhongbiao_gg",
     "http://www.jljsw.gov.cn/zbjggs/index.jhtml",  # http://www.jljsw.gov.cn:20001/web/resultInfo/list?sortOrder=desc&pageSize=14&pageNumber=1&projectName=&dataType=&region=&_=1551778705090
     ["name", "ggstart_time", "href" ,"info"], before(f1), before(f2)],


]

def work(conp, **args):
    est_meta(conp, data=data, diqu="吉林省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "jilin"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://www.jljsw.gov.cn/zbgg/index.jhtml")
    # before(f1)(driver,30)
    # print(before(f2)(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://www.lnzb.cn/lnzbtb/InfoDetail/Default.aspx?InfoID=62d0542a-bc1b-4ae7-ba67-24f1a46478b2&CategoryNum=003002001'))
    # driver.close()
