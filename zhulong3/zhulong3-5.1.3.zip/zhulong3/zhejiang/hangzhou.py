import json
import math
import re

import requests
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong3.util.etl import est_html, est_meta, add_info
import time

_name_ = 'zhejiang_hangzhou'


def f1(driver, num):
    locator = (By.XPATH, '//*[@id="_ctl3_labelCurrentPage"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = re.findall(r"\'(.*?)\'",driver.find_element_by_xpath('//table[@id="_ctl3_GridInfo"]/tbody/tr[1]/td/div/a').get_attribute(
                         "onclick"))[0][-50:]
    cnum = driver.find_element_by_xpath('//*[@id="_ctl3_labelCurrentPage"]').text
    locator = (By.XPATH, '//table[@id="_ctl3_GridInfo"]/tbody/tr')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    if int(cnum) != int(num):
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,'//input[@id="_ctl3_txtGotoPage"]')))
        input1 = driver.find_element_by_xpath('//input[@id="_ctl3_txtGotoPage"]')
        input1.clear()
        input1.send_keys(num)
        driver.find_element_by_id("_ctl3_btnGotoPage").click()
        locator = (By.XPATH, "//table[@id='_ctl3_GridInfo']/tbody/tr[1]/td/div/a[not(contains(@onclick,'%s'))]" % val)

    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table[@id="_ctl3_GridInfo"]/tbody/tr')
    for i, content in enumerate(content_list):
        name = re.sub("\s", ' ', content.xpath("./td/div/a/@title")[0].strip())
        href_temp = content.xpath("./td/div/a/@href")[0].strip()
        # 这个网站有多个链接拼接方式
        # 一种是从href中取链接
        # 一种是从onclick中取链接，onclick_temp 正则出来的长度有几种：一种是4 一种是1 一种是5
        # print(href_temp)
        try:
            onclick_temp = re.findall(r"\'(.*?)\'", content.xpath("./td/div/a/@onclick")[0].strip())
        except:
            onclick_temp = [1,2,3]
        url = ("http://www.hzzbw.net/%s" % (content.xpath("./td/div/a/@href")[
                                                0].strip())) if href_temp != '#' else "http://www.hzzbw.net/DesktopModules/Winstar.Project.ZbbInfoShow/ZBJGDetails.aspx?ProjectID=%s" % (
        onclick_temp[0]) if len(
            onclick_temp) == 1 else "http://www.hzzbw.net/DesktopModules/Winstar.Project.ZbbInfoShow/ZBGSInfoDetail.aspx?ProjectID=%s&DataType=%s&fromtype=%s" % (
        onclick_temp[0], onclick_temp[2], onclick_temp[3]) if len(onclick_temp) == 4 else "http://www.hzzbw.net/%s" % onclick_temp[0]

        area = content.xpath("./td[last()]/text()")[0].strip()
        ggstart_time = content.xpath("./td/div/a/span/text()")[0].strip().strip('(').strip(')')
        info = json.dumps({"area":area},ensure_ascii=False)
        temp = [name, ggstart_time, url, info]
        data.append(temp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//*[@id="_ctl3_labelTotalPage"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_page = driver.find_element_by_xpath('//*[@id="_ctl3_labelTotalPage"]').text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@id="detailsContent"]|//div[@id="detailsLi"]')
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))

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

    div = soup.find('div', id='detailsContent')
    if not div:
        div = soup.find('div', id='detailsLi')
    return div


data1 = [
    ["gcjs_zhaobiao_sbj_gg",
     "http://www.hzzbw.net/DesktopDefault.aspx?tabid=28542264-7d15-406d-b2f8-bd897f548ff5",
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{'area_2':"市本级"}), f2],
    ["gcjs_zhaobiao_kfq_gg",
     "http://www.hzzbw.net/DesktopDefault.aspx?tabid=b184e9ee-ab52-47ce-a661-9fa78ccad48c",
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{'area_2':"开发区"}), f2],
    ["gcjs_zhaobiao_gcq_gg",
     "http://www.hzzbw.net/DesktopDefault.aspx?tabid=c5f30f9b-f8d6-42b9-b22b-fbd239a6a7f2",
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{'area_2':"各城区"}), f2],

    ["gcjs_zhongbiaohx_sbj_gg",
     "http://www.hzzbw.net/DesktopDefault.aspx?tabid=09446b63-068d-4d24-940b-9b8e82119fe0",  # unormal  21  page2
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{'area_2':"市本级"}), f2],
    ["gcjs_zhongbiaohx_kfq_gg",
     "http://www.hzzbw.net/DesktopDefault.aspx?tabid=2824210c-b4a8-41f6-b838-4e5c52cbde5f",  # unormal  20
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{'area_2':"开发区"}), f2],
    ["gcjs_zhongbiaohx_gcq_gg",
     "http://www.hzzbw.net/DesktopDefault.aspx?tabid=abc8ac8d-d216-4b85-b6af-100932c33668",  # unormal  20
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{'area_2':"各城区"}), f2],

    ["gcjs_zhongbiao_sbj_gg",
     "http://www.hzzbw.net/DesktopDefault.aspx?tabid=58871a0c-7328-410f-b43d-70ada2c675e3",  # id
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{'area_2':"市本级"}), f2],
    ["gcjs_zhongbiao_kfq_gg",
     "http://www.hzzbw.net/DesktopDefault.aspx?tabid=b5b49914-a76e-4e44-baa9-e372449b8989",
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{'area_2':"开发区"}), f2],
    ["gcjs_zhongbiao_gcq_gg",
     "http://www.hzzbw.net/DesktopDefault.aspx?tabid=585a5846-516e-4a76-9e2f-dbbdab335a81",
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{'area_2':"各城区"}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data1, diqu="浙江省杭州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "zhejiang_hangzhou"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://www.hzzbw.net/DesktopDefault.aspx?tabid=b184e9ee-ab52-47ce-a661-9fa78ccad48c")
    # f1(driver, 2)
    # driver.get("http://www.hzzbw.net/DesktopDefault.aspx?tabid=09446b63-068d-4d24-940b-9b8e82119fe0")
    # f1(driver, 3)
    # driver.get("http://www.hzzbw.net/DesktopDefault.aspx?tabid=58871a0c-7328-410f-b43d-70ada2c675e3")
    # f1(driver, 10)
    # print(f2(driver))
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://www.jszb.com.cn/jszb/YW_info/ZhaoBiaoGG/ViewReportDetail.aspx?RowID=658544&categoryNum=012&siteid=1'))
    # driver.close()
