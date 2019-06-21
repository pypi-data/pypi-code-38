import re
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong.util.etl import est_html, est_meta, add_info
import requests
import time

_name_="dongtai"
def f3(driver, url):
    driver.get(url)
    locator = (By.CLASS_NAME, "g-atr-main800")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
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
    div = soup.find('div',class_='g-atr-main800')

    return div

def f1(driver, num):
    locator = (By.CLASS_NAME, 'default_pgContainer')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    val = driver.find_element_by_xpath('//div[@class="default_pgContainer"]/li[1]/a').get_attribute("href")[-30:]
    cnum = driver.current_url.split("=")[-1]
    if int(cnum) != int(num):

        url = "=".join(driver.current_url.split("=")[:-1]) + "=" + str(num)
        driver.get(url)

        locator = (By.XPATH, '//div[@class="default_pgContainer"]/li[1]/a[not(contains(@href,"%s"))]' % val)

        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
    locator =(By.XPATH,'//div[@class="default_pgContainer"]/li')
    WebDriverWait(driver,30).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="default_pgContainer"]/li')
    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        url = "http://www.dongtai.gov.cn" + content.xpath("./a/@href")[0]
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None

    return df

def f2(driver):
    try:
        locator = (By.CLASS_NAME, 'default_pgTotalPage')
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
        total_page = int(driver.find_element_by_class_name('default_pgTotalPage').text)
    except:
        total_page = 1
    driver.quit()
    return total_page

data = [

    # ["gcjs_zhaobiao_gg", "http://www.dongtai.gov.cn/col/col1538/index.html?uid=7016&pageNum=1",
    #  ["name", "ggstart_time", "href", "info"], f1, f2],
    # ["gcjs_kongzhijia_gg", "http://www.dongtai.gov.cn/col/col1541/index.html?uid=7016&pageNum=1",
    #  ["name", "ggstart_time", "href", "info"], f1, f2],
    # ["gcjs_zhongbiaohx_gg", "http://www.dongtai.gov.cn/col/col1542/index.html?uid=7016&pageNum=1",
    #  ["name", "ggstart_time", "href", "info"], f1, f2],
    # ["gcjs_zhongbiao_gg", "http://www.dongtai.gov.cn/col/col1543/index.html?uid=7016&pageNum=1",
    #  ["name", "ggstart_time", "href", "info"], f1, f2],
    # ["gcjs_dayi_gg", "http://www.dongtai.gov.cn/col/col1540/index.html?uid=7016&pageNum=1",
    #  ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://dongtai.yancheng.gov.cn/col/col7372/index.html?uid=25630&pageNum=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # ["zfcg_liubiao_gg", "http://www.dongtai.gov.cn/col/col1549/index.html?uid=7016&pageNum=1",
    #  ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://dongtai.yancheng.gov.cn/col/col7837/index.html?uid=25630&pageNum=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    # ["gcjs_zhaobiao_feiruchang_gg", "http://www.dongtai.gov.cn/col/col1550/index.html?uid=7016&pageNum=1",
    #  ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"非入场"}), f2],
    # ["gcjs_dayi_feiruchang_gg", "http://www.dongtai.gov.cn/col/col1552/index.html?uid=7016&pageNum=1",
    #  ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"非入场"}), f2],
    # ["gcjs_zhongbiao_feiruchang_gg", "http://www.dongtai.gov.cn/col/col1553/index.html?uid=7016&pageNum=1",
    #  ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"非入场"}), f2],

]


def work(conp,**kwargs):
    est_meta(conp, data=data, diqu="江苏省东台市",**kwargs)
    est_html(conp, f=f3,**kwargs)
#
# 江苏 - 东台 只能请求前三页的内容
# date：2019年4月4日17:19:56
# 网站变更 只剩两张表

if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "jiangsu", "dongtai"])

    # url = "dataproxy.jsp" + '?startrecord=' +'1' +'&endrecord='+15*1+'&perpage='+15