import re

from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong.util.etl import est_meta, est_html
import time

_name_ = 'anshan'


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='ewb-info-bd']/ul/li[1]/a")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    val = driver.find_element_by_xpath("//div[@class='ewb-info-bd']/ul/li[1]/a").get_attribute("href")[-40:]
    locator = (By.ID, "index")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    cnum = driver.find_element_by_xpath('//*[@id="index"]').text.split('/')[0]
    # //*[@id="zbggmore2_Pager"]/table/tbody/tr/td[1]/font[3]/b
    if int(cnum) != int(num):
        url = re.sub(r'\/\d+\.','/'+str(num)+'.',driver.current_url)
        driver.get(url)
        locator = (By.XPATH, "//div[@class='ewb-info-bd']/ul/li[1]/a")
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        locator = (
            By.XPATH, "//div[@class='ewb-info-bd']/ul/li[1]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//ul[@class='ewb-info-items']/li")
    data = []
    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()
        new_url = "http://www.asggzyjy.cn" + content.xpath("./a/@href")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        temp = [name, ggstart_time, new_url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df



def f2(driver):
    locator = (By.ID, "index")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    total_page = driver.find_element_by_xpath('//*[@id="index"]').text.split('/')[1]

    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    try:
        locator = (By.CLASS_NAME, "ewb-info")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        flag = True
    except:
        locator = (By.ID, "tblInfo")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        flag = False
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
    if flag:
        div = soup.find('div', class_='ewb-info')
    else:
        div = soup.find('table', class_='tblInfo')
    return div


data = [
    # 城市建设
    ["gcjs_zhaobiao_gg",
     "http://www.asggzyjy.cn/gcjs/014001/1.html", ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://www.asggzyjy.cn/gcjs/014002/1.html", ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://www.asggzyjy.cn/gcjs/014003/1.html", ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://www.asggzyjy.cn/zfcg/015001/1.html", ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://www.asggzyjy.cn/zfcg/015002/1.html", ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="辽宁省鞍山市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "liaoning", "anshan"])
    # url = "http://www.asggzyjy.cn/gcjs/014001/1.html"
    # driver = webdriver.Chrome()
    # driver.get(url)
    # for i in range(1,141):f1(driver,i)
    # driver.quit()