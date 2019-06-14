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

_name_ = 'hebei_langfang'


def f1(driver, num):
    locator = (By.XPATH, "//span[@class='page_current']")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath("//span[@class='page_current']/strong").text
    locator = (By.XPATH, "//ul[@class='ks_hyxw ks_hyxw_2']")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//ul[@class='ks_hyxw ks_hyxw_2']/li[1]/a").get_attribute("href")[-40:]
    # print("cnum",cnum,"val",val,'num',num)
    if int(cnum) != int(num):             # index_
        url = re.sub(r"index[_\d]{0,5}\.html","%s%s.html"%('index_' if str(num-1)!='0' else 'index',str(num-1) if str(num-1)!='0' else ''),driver.current_url)
        # print(url)
        driver.get(url)
        locator = (By.XPATH, '//ul[@class="ks_hyxw ks_hyxw_2"]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, '//ul[@class="ks_hyxw ks_hyxw_2"]/li')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    current_url = driver.current_url
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//ul[@class="ks_hyxw ks_hyxw_2"]/li')
    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        url = 'http://www.lfsjs.gov.cn/zwgk/jgks/gcztbglbgs/ywgs/%s'%('zbgg' if 'zbgg' in current_url else 'zbgs')+content.xpath("./a/@href")[0].strip('.')
        if url.count('www')>1:url = 'http://www'+url.rsplit('www')[-1]
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//span[@class='page_total']")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    page_temp = driver.find_element_by_xpath("//span[@class='page_total']").text
    # print(page_temp)
    total_page = re.findall("共(\d+)页", page_temp)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    time.sleep(0.1)
    if "Not Found" in driver.page_source:
        return "Not Found"
    #cxdalist_hqbcon
    locator = (By.XPATH, "//div[@class='wz_content']")
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
    div = soup.find('div', class_='wz_content')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.lfsjs.gov.cn/zwgk/jgks/gcztbglbgs/ywgs/zbgg/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://www.lfsjs.gov.cn/zwgk/jgks/gcztbglbgs/ywgs/zbgs/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="河北省廊坊市", **args)
    est_html(conp, f=f3, **args)




if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "hebei_langfang"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://www.lfsjs.gov.cn/zwgk/jgks/gcztbglbgs/ywgs/zbgg/index.html")
    # f1(driver,5)
    # time.sleep(2)
    # f1(driver,27)
    # f1(driver,1)
    # time.sleep(2)
    #
    # driver.get("http://www.lfsjs.gov.cn/zwgk/jgks/gcztbglbgs/ywgs/zbgs/index.html")
    # time.sleep(2)
    # f1(driver, 21)
    # time.sleep(2)
    # f1(driver, 7)
    # f1(driver, 1)
    #
    # print(f2(driver))
    # print(f3(driver, 'http://www.lfsjs.gov.cn/zwgk/jgks/gcztbglbgs/ywgs/zbgg/201901/20190122/j_2019012208392900022573.html'))
    # driver.close()
