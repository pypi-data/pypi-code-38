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

_name_ = 'hebei_shijiazhuang'


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='fenye']")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    page_temp = driver.find_element_by_xpath("//div[@class='fenye']").text
    cnum = re.findall("(\d+?)\/", page_temp)[0]

    locator = (By.XPATH, "//div[@class='cxdalist_hqbcon']/ul/li")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//div[@class='cxdalist_hqbcon']/ul/li[1]/h4/a").get_attribute("href")[-30:]
    # print("cnum",cnum,"val",val)
    if int(cnum) != int(num):
        url = re.sub("PageNo=\d+","PageNo="+str(num),driver.current_url)
        # print(url)
        driver.get(url)
        locator = (By.XPATH, '//div[@class="cxdalist_hqbcon"]/ul/li[1]/h4/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, '//div[@class="cxdalist_hqbcon"]/ul/li')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="cxdalist_hqbcon"]/ul/li')
    for content in content_list:
        name = content.xpath("./h4/a")[0].xpath("string(.)")
        ggstart_time = content.xpath("./div/text()")[0].strip().split('：')[1]
        url = 'http://www.sjzfgj.gov.cn'+content.xpath("./h4/a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='fenye']")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    page_temp = driver.find_element_by_xpath("//div[@class='fenye']").text
    total_page = re.findall("\/(\d+)", page_temp)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    #cxdalist_hqbcon
    locator = (By.XPATH, "//div[@class='cxdalist_hqbcon']")
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
    div = soup.find('div', class_='cxdalist_hqbcon')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.sjzfgj.gov.cn/plus/list.php?tid=118&TotalResult=2445&PageNo=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="河北省石家庄市", **args)
    est_html(conp, f=f3, **args)



if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "hebei_shijiazhuang"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://www.sjzfgj.gov.cn/plus/list.php?tid=118&TotalResult=2445&PageNo=1")
    # f1(driver,1)
    # f1(driver,100)
    # print(f3(driver, 'http://www.sjzfgj.gov.cn/html/zwgk/gsgg/2019/0201/5384.html'))
    # print(f2(driver))

