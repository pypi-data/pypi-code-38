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

_name_ = 'jilin_siping'


def f1(driver, num):
    locator = (By.XPATH, '//div[@id="pages"]/span')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath('//div[@id="pages"]/span').text

    locator = (By.XPATH, '//ul[@class="list1 lh28 f12 bian"]/li')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//ul[@class="list1 lh28 f12 bian"]/li[1]/a').get_attribute('href')[-20:]
    if int(cnum) != int(num):
        url = re.sub(r"\/[index\d]*\.html","%s%s.html"%('/' if str(num)!='1' else '/index',str(num) if str(num)!='1' else ''),driver.current_url)
        driver.get(url)
        locator = (By.XPATH, '//ul[@class="list1 lh28 f12 bian"]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//ul[@class="list1 lh28 f12 bian"]/li[position() mod 2 = 1]')
    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()
        url = content.xpath("./a/@href")[0].strip('.')
        ggstart_time = content.xpath("./span/text()")[0].strip('[').strip(']').split(' ')[0]
        temp = [name, ggstart_time,url]
        data.append(temp)
        # print('temp',temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@id="pages"]/a[1]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_temp = driver.find_element_by_xpath('//div[@id="pages"]/a[1]').text
    total_item = int(re.findall('(\d+)条',total_temp)[0])
    total_page = math.ceil(total_item/10)
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='Article']")
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
    div = soup.find('div', id='Article')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.spjzy.com/html/gcztb/zbgg/index.html",
     ["name", "ggstart_time", "href","info"],f1,f2],
    ["gcjs_zhongbiao_gg",
     "http://www.spjzy.com/html/gcztb/zbxx/index.html",
     ["name", "ggstart_time", "href","info"],f1,f2],

]

def work(conp, **args):
    est_meta(conp, data=data, diqu="吉林省四平市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "jilin_siping"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://www.spjzy.com/html/gcztb/zbgg/index.html")
    # f1(driver,3)
    # f1(driver,5)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://www.spjzy.com/html/2015/zbgg_0915/650.html'))
    # driver.close()
