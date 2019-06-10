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

_name_ = 'hebei_tangshan'


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='tiaozhuanye']/div")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    page_temp = driver.find_element_by_xpath("//div[@class='tiaozhuanye']/div").text
    cnum = re.findall("(\d+)\/", page_temp)[0]
    locator = (By.XPATH, "//div[@class='rightcontent_bottom border']/ul/li")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//div[@class='rightcontent_bottom border']/ul/li[1]/a").get_attribute("href")[-30:]
    # print("cnum",cnum,"val",val)
    if int(cnum) != int(num):             # index_
        url = re.sub(r"index[_\d]{0,5}\.html","%s%s.html"%('index_' if str(num)!='1' else 'index',str(num) if str(num)!='1' else ''),driver.current_url)
        # print(url)
        driver.get(url)
        locator = (By.XPATH, '//div[@class="rightcontent_bottom border"]/ul/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@class='rightcontent_bottom border']/ul/li")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@class='rightcontent_bottom border']/ul/li")
    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        url = 'http://zhujianju.tangshan.gov.cn'+content.xpath("./a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='tiaozhuanye']")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    page_temp = driver.find_element_by_xpath("//div[@class='tiaozhuanye']/div").text
    total_page = re.findall("\/(\d+)页", page_temp)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)                    #cxdalist_hqbcon
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


data = [
    ["gcjs_zhaobiao_gg",
     "http://zhujianju.tangshan.gov.cn/tszjj/zjjzhaobiaogonggao/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://zhujianju.tangshan.gov.cn/tszjj/zjjzhongbiaogonggao/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="河北省唐山市", **args)
    est_html(conp, f=f3, **args)



if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "hebei_tangshan"]
    work(conp,num=4,headless=False,pageloadstrategy='none')
    # driver = webdriver.Chrome()
    # driver.get("http://zhujianju.tangshan.gov.cn/tszjj/zjjzhaobiaogonggao/index.html")
    # f1(driver,5)
    # f1(driver,1)
    # print(f3(driver, 'http://zhujianju.tangshan.gov.cn/tszjj/zjjzhaobiaogonggao/20181114/655133.html'))
    # print(f2(driver))

