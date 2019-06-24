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
from zhulong3.util.etl import est_html, est_meta, add_info
import time

_name_ = 'liaoning_shenghui'


def f1(driver, num):
    locator = (By.XPATH, "//font[@color='red']")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath("//font[@color='red']/b").text
    locator = (By.XPATH, '//table[contains(@id,"more2_DataGrid")]/tbody/tr')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//table[contains(@id,"more2_DataGrid")]/tbody/tr[1]/td[2]/a').get_attribute("href")[-50:]
    locator = (By.XPATH, '//table[contains(@id,"more2_DataGrid")]/tbody/tr')
    if int(cnum) != int(num):
        driver.execute_script(
            "javascript:__doPostBack('%s2$Pager','%s')" % (re.findall(r"fo\/(\w+).aspx", driver.current_url)[0], num))
        locator = (By.XPATH, '//table[contains(@id,"more2_DataGrid")]/tbody/tr[1]/td[2]/a[not(contains(@href,"%s"))]' % val)
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table[contains(@id,"more2_DataGrid")]/tbody/tr')
    for content in content_list:
        name = content.xpath("./td[2]/a")[0].xpath('string(.)').strip()
        try:
            ggstart_time = content.xpath("./td[last()]/text()")[0].strip()
        except:ggstart_time = ''
        url = 'http://www.lnzb.cn'+content.xpath("./td[2]/a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//font[@color='blue']")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_page = driver.find_element_by_xpath("//font[@color='blue'][2]/b").text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@id='tblInfo']")
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
    div = soup.find('table', id='tblInfo')
    return div


data = [
    ["gcjs_zhaobiao_kcsj_gg",
     "http://www.lnzb.cn/lnzbtb/ShowInfo/zbggmore.aspx?categorynum=003001001&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'勘察设计'}), f2],
    ["gcjs_zhaobiao_jl_gg",
     "http://www.lnzb.cn/lnzbtb/ShowInfo/zbggmore.aspx?categorynum=003001002&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'监理'}), f2],
    ["gcjs_zhaobiao_sg_gg",
     "http://www.lnzb.cn/lnzbtb/ShowInfo/zbggmore.aspx?categorynum=003001003&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'施工'}), f2],
    ["gcjs_zhaobiao_clsb_gg",
     "http://www.lnzb.cn/lnzbtb/ShowInfo/zbggmore.aspx?categorynum=003001004&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'材料设备'}), f2],
    ["gcjs_zhaobiao_qt_gg",
     "http://www.lnzb.cn/lnzbtb/ShowInfo/zbggmore.aspx?categorynum=003001005&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'其他'}), f2],

    ["gcjs_zhongbiaohx_kcsj_gg",
     "http://www.lnzb.cn/lnzbtb/ShowInfo/zbgsmore.aspx?categorynum=003002001&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'勘察设计'}), f2],
    ["gcjs_zhongbiaohx_jl_gg",
     "http://www.lnzb.cn/lnzbtb/ShowInfo/zbgsmore.aspx?categorynum=003002002&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'监理'}), f2],
    ["gcjs_zhongbiaohx_sg_gg",
     "http://www.lnzb.cn/lnzbtb/ShowInfo/zbgsmore.aspx?categorynum=003002003&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'施工'}), f2],
    ["gcjs_zhongbiaohx_clsb_gg",
     "http://www.lnzb.cn/lnzbtb/ShowInfo/zbgsmore.aspx?categorynum=003002004&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'材料设备'}), f2],
    ["gcjs_zhongbiaohx_qt_gg",
     "http://www.lnzb.cn/lnzbtb/ShowInfo/zbgsmore.aspx?categorynum=003002005&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'其他'}), f2],

    ["gcjs_zhongbiao_kcsj_gg",
     "http://www.lnzb.cn/lnzbtb/ShowInfo/zbjgmore.aspx?categorynum=003003001&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'勘察设计'}), f2],
    ["gcjs_zhongbiao_jl_gg",
     "http://www.lnzb.cn/lnzbtb/ShowInfo/zbjgmore.aspx?categorynum=003003002&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'监理'}), f2],
    ["gcjs_zhongbiao_sg_gg",
     "http://www.lnzb.cn/lnzbtb/ShowInfo/zbjgmore.aspx?categorynum=003003003&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'施工'}), f2],
    ["gcjs_zhongbiao_clsb_gg",
     "http://www.lnzb.cn/lnzbtb/ShowInfo/zbjgmore.aspx?categorynum=003003004&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'材料设备'}), f2],
    ["gcjs_zhongbiao_qt_gg",
     "http://www.lnzb.cn/lnzbtb/ShowInfo/zbjgmore.aspx?categorynum=003003005&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'其他'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="辽宁省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "liaoning"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://www.lnzb.cn/lnzbtb/ShowInfo/zbggmore.aspx?categorynum=003001001&QuYu=")
    # f1(driver,10)
    # f1(driver,5)
    # f1(driver,30)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://www.lnzb.cn/lnzbtb/GongGaoPersonalize/ZBGG_Detail.aspx?InfoID=0022974b-86ee-4875-bbfd-65e738a473dc&CategoryNum=003001004'))
    # driver.close()