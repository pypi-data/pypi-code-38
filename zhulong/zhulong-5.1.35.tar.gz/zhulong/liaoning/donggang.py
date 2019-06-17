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
from zhulong.util.etl import est_html, est_meta, add_info
import time

_name_='donggang'
def f1(driver, num):

    locator = (By.XPATH,"//div[@class='zw']/ul/li")
    WebDriverWait(driver,20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath("//div[@class='zw']/ul/li[1]/a").get_attribute("href")[-20:]
    cnum = re.findall("Page=(\d+)",driver.current_url)[0]
    if int(cnum) != int(num):
        url = driver.current_url.split("&")[0] + "&Page=" + str(num)
        driver.get(url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        locator = (
            By.XPATH, '//div[@class="zw"]/ul/li[1]/a[not(contains(string(),"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@class='zw']/ul/li")
    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        url = "http://www.donggang.gov.cn"+content.xpath("./a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df

def f2(driver):
    if WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH,"//div[@class='abcde']/ul"))).text != '':
        total_page = WebDriverWait(driver,20).until(EC.visibility_of_element_located((By.XPATH,"//div[@class='abcde']/ul/li[last()-1]/a"))).text
    else:
        total_page = 1
    driver.quit()
    return int(total_page)

def f3(driver, url):
    driver.get(url)
    if "list_er list_er1" in driver.page_source:
        locator = (By.XPATH, "//div[@class='list_er list_er1']")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        flag = 1
    else:
        locator = (By.CLASS_NAME, "new_lz")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        flag =2
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
    if flag ==1:
        div = soup.find('div',class_="list_er list_er1")
    else:
        div = soup.find('div',class_="new_lz")
    # print(div)
    return div


data = [
    ["zfcg_zhaobiao_gg",
     "http://www.donggang.gov.cn/links/?pid=463&Page=1",
     ["name", "ggstart_time", "href", "info"],f1, f2],
    ["zfcg_biangeng_gg",
     "http://www.donggang.gov.cn/links/?pid=464&Page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://www.donggang.gov.cn/links/?pid=465&Page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["gcjs_gqita_fangjiangongcheng_gg",
     "http://www.donggang.gov.cn/links/?pid=459&Page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"gctype":"房建"}), f2],
    ["gcjs_gqita_jiaotong_gg",
     "http://www.donggang.gov.cn/links/?pid=460&Page=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{"gctype":"交通"}), f2],

    ["gcjs_gqita_shuili_gg",
     "http://www.donggang.gov.cn/links/?pid=461&Page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"gctype":"水利"}), f2],
    ["gcjs_gqita_zhao_zhong_gg",
     "http://www.donggang.gov.cn/links/?pid=1008&Page=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp,**args):
    est_meta(conp, data=data, diqu="辽宁省东港市",**args)
    est_html(conp, f=f3,**args)


if __name__ == "__main__":
    conp=["postgres", "since2015", "192.168.4.175", "liaoning", "donggang"]
    work(conp=conp)
    # import sys
    # arg=sys.argv
    # if len(arg) >3:
    #     work(conp,num=int(arg[1]),total=int(arg[2]),html_total=int(arg[3]))
    # elif len(arg) == 2:
    #     work(conp, html_total=int(arg[1]))
    # else:
    #     work(conp)
