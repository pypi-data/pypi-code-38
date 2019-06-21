import json
import re
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
import pandas as pd
from zhulong.util.etl import est_meta, est_html

_name_ = "tongliao"
global xxtype_signal

def f1(driver, num):
    url = "http://ggzy.tongliao.gov.cn/EpointWebBuilder_tlsggzy/jyxxInfoAction.action"
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Content-Type": "application/json;charset=utf-8",
        "Host": "ggzy.tlzw.gov.cn",
        "Referer": "http://ggzy.tongliao.gov.cn/tlsggzy/jsgc/subpage.html",
        "X-Requested-With": "XMLHttpRequest",
        "Cookie": "JSESSIONID=599B0B278BE8172522C3069A64C09FE3",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36",
        "Connection": "keep-alive",
    }
    params = {
        "cmd": "getInfolist",
        "xxtype": xxtype_signal,
        "pageSize": 12,
        "pageIndex": num - 1
    }

    response = requests.get(url, params=params, headers=headers)
    body_string = response.content.decode().encode("latin-1").decode("unicode_escape")
    body_string = re.findall('Table\" \:\[(.+)\]', body_string)[0]
    name_list = re.findall('realtitle":\"(.+?)\"', body_string)
    ggstart_time_list = re.findall('infodate":\"(.+?)\"', body_string)
    url_list = re.findall('infourl":\"(.+?)\"', body_string)
    data = []
    for name, ggstart_time, url in zip(name_list, ggstart_time_list, url_list):
        name = re.sub(' ','',name)
        url = "http://ggzy.tongliao.gov.cn" + url.replace('\\', '').replace(' ', '')
        temp = [name, ggstart_time, url]
        data.append(temp)
        print(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    driver.refresh()
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@data-role='tab-content' and @class='']//ul[@class='m-pagination-page']")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    total_page = driver.find_element_by_xpath("//div[@data-role='tab-content' and @class='']//ul[@class='m-pagination-page']/li[last()]/a").text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='ewb-article']")
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
    div = soup.find('div', class_='ewb-article')
    # print(div)
    return div


def switch(driver, ggtype, xmtype):
    global xxtype_signal

    locator = (By.XPATH, "//div[@data-role='tab-content' and @class='']//ul[@class='m-pagination-page']/li[last()]")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    val = driver.find_element_by_xpath("//div[@data-role='tab-content' and @class='']//ul[@class='m-pagination-page']/li[last()]").text
    if ggtype != "建设工程":
        driver.find_element_by_xpath("//ul[@class='clearfix']/li[contains(string(),'%s')]" % ggtype).click()
        locator = (By.XPATH, "//div[@data-role='tab-content' and @class='']//ul[@class='m-pagination-page']/li[last()][not(contains(string(),'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    val = driver.find_element_by_xpath("//div[@data-role='tab-content' and @class='']//ul[@class='m-pagination-page']/li[last()]").text

    driver.find_element_by_xpath("//div[@data-role='tab-content' and @class='']/div[3]/a[contains(string(),'%s')]" % xmtype).click()
    locator = (By.XPATH, "//div[@data-role='tab-content' and @class='']//ul[@class='m-pagination-page']/li[last()][not(contains(string(),'%s'))]" % val)
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))


    xxtype_signal = driver.find_element_by_xpath("//div[@data-role='tab-content' and @class='']/div[3]/a[contains(string(),'%s')]" % xmtype).get_attribute("value")

def before(f, ggtype, xmtype):
    def wrap(*args):
        driver = args[0]
        switch(driver, ggtype, xmtype)
        return f(*args)

    return wrap


data = [
    ["gcjs_zhaobiao_gg",
     "http://ggzy.tongliao.gov.cn/tlsggzy/jsgc/subpage.html",
     ["name", "ggstart_time", "href", "info"], before(f1, "建设工程", "招标公告"), before(f2, "建设工程", "招标公告")],
    ["gcjs_biangeng_gg",
     "http://ggzy.tongliao.gov.cn/tlsggzy/jsgc/subpage.html",
     ["name", "ggstart_time", "href", "info"], before(f1, "建设工程", "变更公告"), before(f2, "建设工程", "变更公告")],
    ["gcjs_zhongbiaohx_gg",
     "http://ggzy.tongliao.gov.cn/tlsggzy/jsgc/subpage.html",
     ["name", "ggstart_time", "href", "info"], before(f1, "建设工程", "中标候选人公示"), before(f2, "建设工程", "中标候选人公示")],

    ["zfcg_zhaobiao_gg",
     "http://ggzy.tongliao.gov.cn/tlsggzy/jsgc/subpage.html",
     ["name", "ggstart_time", "href", "info"], before(f1, "政府采购", "采购公告"), before(f2, "政府采购", "采购公告")],
    ["zfcg_biangeng_gg",
     "http://ggzy.tongliao.gov.cn/tlsggzy/jsgc/subpage.html",
     ["name", "ggstart_time", "href", "info"], before(f1, "政府采购", "变更"), before(f2, "政府采购", "变更")],
    ["zfcg_zhongbiao_gg",
     "http://ggzy.tongliao.gov.cn/tlsggzy/jsgc/subpage.html",
     ["name", "ggstart_time", "href", "info"], before(f1, "政府采购", "中标"), before(f2, "政府采购", "中标")],


]


def work(conp, **kwargs):
    est_meta(conp, data=data, diqu="内蒙古自治区通辽市", **kwargs)
    est_html(conp, f=f3, **kwargs)


#
# 内蒙古- 通辽 网站打不开
# date ：2019年4月4日17:28:32
#


if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "neimenggu", "tongliao"])
    # driver =webdriver.Chrome()
    # driver.get("http://ggzy.tongliao.gov.cn/tlsggzy/jsgc/subpage.html")
    # for i in range(1,50):
    #     before(f1, "建设工程", "变更公告")(driver,i)
    #
    # print(before(f2, "建设工程", "变更公告")(driver))