import math
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

_name_ = 'jiangsu_changzhou'


def f1(driver, num):
    locator = (By.XPATH, '//font[@color="red"][1]/b')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    val = driver.find_element_by_xpath('//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a|//td[contains(@id,"tdcontent")]//tbody/tr[1]/td[2]/a').get_attribute("href")[-30:]
    cnum = driver.find_element_by_xpath('//font[@color="red"][1]/b').text
    locator = (By.XPATH, '//*[@id="MoreInfoList1_DataGrid1"]//tr|//td[contains(@id,"tdcontent")]//tbody/tr')

    # print('cnum',cnum,'num',num,'val',val)
    if int(cnum) != int(num):
        if "zbsl" in driver.current_url:
            driver.execute_script("javascript:__doPostBack('MoreInfoList_zbsl1$Pager','%s')"%num)
        if "slzb" in driver.current_url:
            driver.execute_script("javascript:__doPostBack('MoreInfoList_slzb$Pager','%s')"%num)
        else:
            driver.execute_script("javascript:__doPostBack('MoreInfoList1$Pager','%s')" % num)

        locator = (By.XPATH, '//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a[not(contains(@href,"%s"))]|//td[contains(@id,"tdcontent")]//tbody/tr[1]/td[2]/a[not(contains(@href,"%s"))]' %(val,val))
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//*[@id="MoreInfoList1_DataGrid1"]//tr|//td[contains(@id,"tdcontent")]//tbody/tr')
    for content in content_list:
        try:
            name = content.xpath("./td[2]/a/text()")[0].strip()
        except:
            name = "空"
        url = "http://www.czgcjy.com" + content.xpath("./td[2]/a/@href")[0].strip()
        ggstart_time = content.xpath("./td[last()]/text()")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    try:
        locator = (By.XPATH, "//font[@color='blue'][2]/b")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        total_page = driver.find_element_by_xpath("//font[@color='blue'][2]/b").text
    except:
        locator = (By.XPATH, "//font[2]/font[@color='blue']/b")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        total_page = driver.find_element_by_xpath("//font[2]/font[@color='blue']/b").text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    try:
        locator = (By.XPATH, '//table[@id="tblInfo"]')
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        flag=1
    except:
        locator = (By.XPATH, '/html/body/table[2]/tbody/tr[3]/td/table/tbody/tr/td[2]/table')
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        flag=2
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
    if flag==1:

        div = soup.find('table', id='tblInfo')
    elif flag == 2:
        div = soup.findAll('table')[1]
    return div



data = [
    ["gcjs_zhaobiao_sg_gg",
     "http://www.czgcjy.com/czztb/jyxx/010001/010001001/MoreInfo.aspx?CategoryNum=010001001",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'施工'}), f2],
    ["gcjs_zhaobiao_jl_gg",
     "http://www.czgcjy.com/czztb/jyxx/010001/010001002/MoreInfo.aspx?CategoryNum=010001002",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'监理'}), f2],
    ["gcjs_zhaobiao_kcsj_gg",
     "http://www.czgcjy.com/czztb/jyxx/010001/010001003/MoreInfo.aspx?CategoryNum=010001003",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'勘察设计'}), f2],
    ["gcjs_zhaobiao_clsb_gg",
     "http://www.czgcjy.com/czztb/jyxx/010001/010001004/MoreInfo.aspx?CategoryNum=010001004",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'材料设备'}), f2],
    ["gcjs_zhaobiao_sl_gg",
     "http://www.czgcjy.com/czztb/showinfo/moreinfo_zbsl.aspx/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'水利'}), f2],
    ["gcjs_zhaobiao_qt_gg",
     "http://www.czgcjy.com/czztb/jyxx/010001/010001005/MoreInfo.aspx?CategoryNum=010001005",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'其他'}), f2],

    ["gcjs_zhongbiao_1_sg_gg",
     "http://www.czgcjy.com/czztb/jyxx/010006/010006001/MoreInfo.aspx?CategoryNum=010006001",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'施工'}), f2],
    ["gcjs_zhongbiao_1_jl_gg",
     "http://www.czgcjy.com/czztb/jyxx/010006/010006002/MoreInfo.aspx?CategoryNum=010006002",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'监理'}), f2],
    ["gcjs_zhongbiao_1_kcsj_gg",
     "http://www.czgcjy.com/czztb/jyxx/010006/010006003/MoreInfo.aspx?CategoryNum=010006003",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'勘察设计'}), f2],
    ["gcjs_zhongbiao_1_clsb_gg",
     "http://www.czgcjy.com/czztb/jyxx/010006/010006004/MoreInfo.aspx?CategoryNum=010006004",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'材料设备'}), f2],
    ["gcjs_zhongbiao_1_qt_gg",
     "http://www.czgcjy.com/czztb/jyxx/010006/010006005/MoreInfo.aspx?CategoryNum=010006005",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'其他'}), f2],



    ["gcjs_zgysjg_sg_gg",
     "http://www.czgcjy.com/czztb/jyxx/010003/010003001/MoreInfo.aspx?CategoryNum=010003001",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'施工'}), f2],
    ["gcjs_zgysjg_jl_gg",
     "http://www.czgcjy.com/czztb/jyxx/010003/010003002/MoreInfo.aspx?CategoryNum=010003002",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'监理'}), f2],
    ["gcjs_zgysjg_kcsj_gg",
     "http://www.czgcjy.com/czztb/jyxx/010003/010003003/MoreInfo.aspx?CategoryNum=010003003",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'勘察设计'}), f2],
    ["gcjs_zgysjg_clsb_gg",
     "http://www.czgcjy.com/czztb/jyxx/010003/010003004/MoreInfo.aspx?CategoryNum=010003004",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'材料设备'}), f2],
    ["gcjs_zgysjg_qt_gg",
     "http://www.czgcjy.com/czztb/jyxx/010003/010003005/MoreInfo.aspx?CategoryNum=010003005",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'其他'}), f2],



    ["gcjs_zhaobiao_zjfb_gg",
     "http://www.czgcjy.com/czztb/jyxx/010005/010005001/MoreInfo.aspx?CategoryNum=010005001",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"Tag":'直接发包'}), f2],
    ["gcjs_gqita_pmchange_gg",
     "http://www.czgcjy.com/czztb/jyxx/010005/010005002/MoreInfo.aspx?CategoryNum=010005002",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"Tag":'项目经理变更'}), f2],



    ["gcjs_zhongbiao_sg_gg",
     "http://www.czgcjy.com/czztb/jyxx/010002/010002001/MoreInfo.aspx?CategoryNum=010002001",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'施工'}), f2],
    ["gcjs_zhongbiao_jl_gg",
     "http://www.czgcjy.com/czztb/jyxx/010002/010002002/MoreInfo.aspx?CategoryNum=010002002",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'监理'}), f2],
    ["gcjs_zhongbiao_kcsj_gg",
     "http://www.czgcjy.com/czztb/jyxx/010002/010002003/MoreInfo.aspx?CategoryNum=010002003",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'勘察设计'}), f2],
    ["gcjs_zhongbiao_clsb_gg",
     "http://www.czgcjy.com/czztb/jyxx/010002/010002004/MoreInfo.aspx?CategoryNum=010002004",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'材料设备'}), f2],
    ["gcjs_zhongbiao_sl_gg",
     "http://www.czgcjy.com/czztb/showinfo/moreinfo_slzb.aspx/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'水利'}), f2],
    ["gcjs_zhongbiao_qt_gg",
     "http://www.czgcjy.com/czztb/jyxx/010002/010002005/MoreInfo.aspx?CategoryNum=010002005",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":'其他'}), f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="江苏省常州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "jiangsu_changzhou"]
    work(conp,pageloadstrategy='none')
    # driver = webdriver.Chrome()
    # driver.get("http://www.czgcjy.com/czztb/showinfo/moreinfo_zbsl.aspx/")
    # for i in range(1,22):f1(driver, i)
