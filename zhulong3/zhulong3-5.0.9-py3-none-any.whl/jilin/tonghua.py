import re
import math
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

_name_ = 'jilin_tonghua'


def f1(driver, num):
    locator = (By.XPATH, '//input[@id="num"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath('//input[@id="num"]').get_attribute("value")

    locator = (By.XPATH, '//div[@class="newslist"]/ul/li')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//div[@class="newslist"]/ul/li[1]/a').get_attribute('href')[-20:]

    if int(cnum) != int(num):
        url = re.sub(r"index[_\d]*\.html","index%s.html"%('_'+str(num-1) if str(num)!='1' else ''),driver.current_url)
        driver.get(url)
        locator = (By.XPATH, '//div[@class="newslist"]/ul/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="newslist"]/ul/li')
    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()
        url = "http://www.tonghua.gov.cn/cjj/zbtb"+content.xpath("./a/@href")[0].strip('.')
        ggstart_time = content.xpath("./span/text()")[0].strip().strip('[').strip(']')
        temp = [name, ggstart_time,url]
        data.append(temp)
        # print('temp',temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="newslist"]/div')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_temp = driver.find_element_by_xpath('//div[@class="newslist"]/div').text
    total_page = int(re.findall('共(\d+)页',total_temp)[0])
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='xyh_xxynrq']")
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
    div = soup.find('div', class_='xyh_xxynrq')
    return div


data = [
    ["gcjs_gqita_zhao_zhong_bu_bian_gg",
     "http://www.tonghua.gov.cn/cjj/zbtb/index.html",
     ["name", "ggstart_time", "href","info"],f1,f2],


]

def work(conp, **args):
    est_meta(conp, data=data, diqu="吉林省通化市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "jilin_tonghua"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://www.tonghua.gov.cn/cjj/zbtb/index.html")
    # f1(driver,25)
    # f1(driver,5)
    # f1(driver,1)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://www.tonghua.gov.cn/cjj/zbtb/201810/t20181029_316088.html'))
    # driver.close()
