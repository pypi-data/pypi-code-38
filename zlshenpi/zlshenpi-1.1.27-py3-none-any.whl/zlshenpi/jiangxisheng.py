import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zlshenpi.util.etl import add_info, est_meta, est_html, est_tbs, add_info, est_meta_large
import sys
import time
import json
_name_ = "jiangxisheng"

def f1(driver, num):
    locator = (By.XPATH, "//div[@id='div_business_list']/table[@class='table table-bordered table-hover']/tbody/tr")
    val = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text
    # print(val)
    locator = (By.XPATH, "//div[@class='pages']/span")
    cnum = int(WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text)

    num += 120
    total_page = int(
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@class='pages']/a[last()-1]"))).text.split('.')[-1])

    if num >= total_page:
        return pd.DataFrame([])

    if num != int(cnum):
        driver.execute_script('bltable.pageIndex(%s);onQuery()' % num)
        locator = (By.XPATH, """//div[@id="div_business_list"]/table[@class='table table-bordered table-hover']/tbody/tr[not(contains(string(), "%s"))]""" % val)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    body = etree.HTML(page)
    contents = body.xpath("//div[@id='div_business_list']/table[@class='table table-bordered table-hover']/tbody/tr")
    data = []
    for content in contents:
        try:
            name = content.xpath('./td[2]/a/text()')[0].strip()
        except:name = "None"
        href = 'None'
        xm_code = content.xpath("./td[1]/a/text()")[0].strip()
        status = content.xpath('./td[last()]/text()')[0].strip()
        shenpi_name = content.xpath('./td[3]/text()')[0].strip()

        ggstart_time = content.xpath('./td[last()-1]/text()')[0].strip()
        info = json.dumps({"status": status, 'shenpi_name': shenpi_name, "xm_code": xm_code,'hreftype':'不可抓网页'}, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="pages"]/a[last()-1]')
    total_page = int(WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.split('.')[-1])
    driver.quit()
    return total_page


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='block_content']|//div[@class='uc-content frr']")
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find('div', class_="block_content")
    if not div:
        div=soup.find('div',class_="uc-content frr")
    return div


data = [
    ["xm_jieguo_gg",
     "http://tzxm.jxzwfww.gov.cn/icity/ipro/publicity",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="江西省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlshenpi", "jiangxisheng"],num=1)
    # driver = webdriver.Chrome()
    # for d in data:
    #     driver.get(d[1])
        # print(d[1])
        # for i in range(3970,3980):
        #     print(f1(driver, i))
    # print(f2(driver))
