import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
import pandas as pd
from zhulong.util.etl import est_meta, est_html

_name_ = "baotou"


def f1(driver, num):

    locator = (By.XPATH, "//ul[@class='ewb-list']/li/a")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//ul[@class='ewb-list']/li[1]/a").get_attribute("href")
    if "007001005" not in driver.current_url:
        locator = (By.ID, "index")
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        cnum = re.findall('(\d+)\/',driver.find_element_by_id("index").text)[0]
    else:
        try:
            locator = (By.ID, "index")
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
            cnum = re.findall('(\d+)\/', driver.find_element_by_id("index").text)[0]
        except:
            cnum = 1
    # return
    if int(cnum) != int(num):
        url = '/'.join(driver.current_url.split('/')[:-1])+"/"+str(num)+".html"
        driver.get(url)
        # print(num,url)
        locator = (By.XPATH, "//ul[@class='ewb-list']/li[1]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//ul[@class='ewb-list']/li")
    for content in content_list:
        name = content.xpath("./a")[0].xpath("string(.)").strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        url = "http://www.btggzyjy.cn" + content.xpath("./a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):

    if "007001005" not in driver.current_url:
        locator = (By.ID, "index")
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        total_page = re.findall('\/(\d+)', driver.find_element_by_id("index").text)[0]
    else:
        try:
            locator = (By.ID, "index")
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
            total_page = re.findall('\/(\d+)', driver.find_element_by_id("index").text)[0]
        except:
            total_page = 1
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    if "404 Not Found" in driver.page_source:return "404 Not Found"
    locator = (By.XPATH, "//div[@class='ewb-row']")
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
    div1 = soup.find('div', class_='ewb-main')
    div = div1.find('div', class_="ewb-row")
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.btggzyjy.cn/jygk/007001/007001001/secondPage.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_biangeng_gg",
     "http://www.btggzyjy.cn/jygk/007001/007001005/secondPage.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://www.btggzyjy.cn/jygk/007001/007001003/secondPage.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://www.btggzyjy.cn/jygk/007001/007001004/secondPage.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://www.btggzyjy.cn/jygk/007002/007002001/secondPage.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://www.btggzyjy.cn/jygk/007002/007002002/secondPage.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://www.btggzyjy.cn/jygk/007002/007002003/secondPage.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **kwargs):
    est_meta(conp, data=data, diqu="内蒙古自治区包头市", **kwargs)
    est_html(conp, f=f3, **kwargs)


if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "neimenggu", "baotou"])

    # driver = webdriver.Chrome()
    # print(f3(driver, "http://www.btggzyjy.cn/jygk/007002/007002002/20180928/1368676.html"))