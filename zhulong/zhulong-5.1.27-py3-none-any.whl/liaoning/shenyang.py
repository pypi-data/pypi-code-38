import re

from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong.util.etl import est_meta, est_html, add_info
import time

_name_ = "shenyang"
def f1(driver, num):
    locator = (By.XPATH, '//*[contains(@id,"DataGrid1")]/tbody/tr[1]/td[2]/a')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    val = driver.find_element_by_xpath('//*[contains(@id,"DataGrid1")]/tbody/tr[1]/td[2]/a').get_attribute("href")[-50:]
    cnum = driver.find_element_by_xpath('//*[contains(@id,"Pager")]/table/tbody/tr/td[1]/font[3]/b').text
    if int(cnum) != int(num):
        js_part = driver.find_element_by_xpath('//td[@align="notset"]/a[last()]').get_attribute("href")
        js = re.sub(r",\'\d+\'",",'%s'"%num,js_part)
        driver.execute_script(js)
        locator = (By.XPATH, '//*[contains(@id,"DataGrid1")]/tbody/tr[1]/td[2]/a')
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        locator = (
            By.XPATH, '//*[contains(@id,"DataGrid1")]/tbody/tr[1]/td[2]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//*[contains(@id,"DataGrid1")]/tbody/tr')

    data = []
    for content in content_list:
        name = content.xpath("./td/a/text()")[0].strip()
        new_url = "http://sy1.lnzb.cn" + content.xpath("./td/a/@href")[0].strip()
        ggstart_time = content.xpath("./td[3]/text()")[0].strip()
        temp = [name, ggstart_time, new_url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//*[contains(@id,"Pager")]')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    total_page = driver.find_element_by_xpath('//*[contains(@id,"Pager")]/table/tbody/tr/td[1]/font[2]/b').text

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
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('table', id='tblInfo')
    return div



data = [
    # 公共资源
    ["gcjs_zhaobiao_kcsj_gg",
     "http://sy1.lnzb.cn/syxx/ShowInfo/zbggmore.aspx?categorynum=003001001&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"勘察设计"}), f2],
    ["gcjs_zhaobiao_jl_gg",
     "http://sy1.lnzb.cn/syxx/ShowInfo/zbggmore.aspx?categorynum=003001002&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"监理"}), f2],
    ["gcjs_zhaobiao_sg_gg",
     "http://sy1.lnzb.cn/syxx/ShowInfo/zbggmore.aspx?categorynum=003001003&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"施工"}), f2],
    ["gcjs_zhaobiao_clsb_gg",
     "http://sy1.lnzb.cn/syxx/ShowInfo/zbggmore.aspx?categorynum=003001004&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"材料设备"}), f2],
    ["gcjs_zhaobiao_qita_gg",
     "http://sy1.lnzb.cn/syxx/ShowInfo/zbggmore.aspx?categorynum=003001005&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"其他"}), f2],

    ["gcjs_zhongbiaohx_kcsj_gg",
     "http://sy1.lnzb.cn/syxx/ShowInfo/zbgsmore.aspx?categorynum=003002001&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"勘察设计"}), f2],
    ["gcjs_zhongbiaohx_jl_gg",
     "http://sy1.lnzb.cn/syxx/ShowInfo/zbgsmore.aspx?categorynum=003002002&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"监理"}), f2],
    ["gcjs_zhongbiaohx_sg_gg",
     "http://sy1.lnzb.cn/syxx/ShowInfo/zbgsmore.aspx?categorynum=003002003&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"施工"}), f2],
    ["gcjs_zhongbiaohx_clsb_gg",
     "http://sy1.lnzb.cn/syxx/ShowInfo/zbgsmore.aspx?categorynum=003002004&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"材料设备"}), f2],
    ["gcjs_zhongbiaohx_qita_gg",
     "http://sy1.lnzb.cn/syxx/ShowInfo/zbgsmore.aspx?categorynum=003002005&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"其他"}), f2],

    ["gcjs_zhongbiao_kcsj_gg",
     "http://sy1.lnzb.cn/syxx/ShowInfo/zbjgmore.aspx?categorynum=003003001&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"勘察设计"}), f2],
    ["gcjs_zhongbiao_jl_gg",
     "http://sy1.lnzb.cn/syxx/ShowInfo/zbjgmore.aspx?categorynum=003003002&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"监理"}), f2],
    ["gcjs_zhongbiao_sg_gg",
     "http://sy1.lnzb.cn/syxx/ShowInfo/zbjgmore.aspx?categorynum=003003003&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"施工"}), f2],
    ["gcjs_zhongbiao_clsb_gg",
     "http://sy1.lnzb.cn/syxx/ShowInfo/zbjgmore.aspx?categorynum=003003004&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"材料设备"}), f2],
    ["gcjs_zhongbiao_qita_gg",
     "http://sy1.lnzb.cn/syxx/ShowInfo/zbjgmore.aspx?categorynum=003003005&QuYu=",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"其他"}), f2],

]


def work(conp,**arg):
    est_meta(conp, data=data, diqu="辽宁省沈阳市",**arg)
    est_html(conp, f=f3,**arg)

if __name__ == "__main__":
    # work(conp=["postgres", "since2015", "192.168.3.171", "liaoning", "shenyang"])
    driver = webdriver.Chrome()
    url = 'http://sy1.lnzb.cn/syxx/GongGaoPersonalize/ZBGG_Detail.aspx?InfoID=0002f77d-8096-4c55-b97b-5234efbecc26&CategoryNum=003001003&tdsourcetag=s_pctim_aiomsg'
    print(f3(driver, url))
    # driver.get('http://sy1.lnzb.cn/syxx/ShowInfo/zbgsmore.aspx?categorynum=003002004&QuYu=')
    # for i in range(7,15):f1(driver,i)
    # driver.quit()