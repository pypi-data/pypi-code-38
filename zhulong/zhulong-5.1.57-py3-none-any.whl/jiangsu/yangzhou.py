import re

from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html, add_info
import requests
import time

_name_='yangzhou'
def f1(driver, num):
    driver.implicitly_wait(30)
    locator = (By.XPATH, "//span[@style='float:right;']")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    cnum = int(driver.find_element_by_xpath("//span[@style='float:right;']").text.split()[1])
    before = len(driver.page_source)
    if int(num) != cnum:
        driver.find_element_by_id('currentPage').clear()
        driver.find_element_by_id('currentPage').send_keys(num)
        driver.find_element_by_id('currentPage').send_keys(Keys.ENTER)

        after = len(driver.page_source)
        i = 0
        while before != after:
            before = len(driver.page_source)
            time.sleep(0.1)
            after = len(driver.page_source)
            i += 1
            if i > 5: break
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//ul[@class='item lh jt_dott f14']/li")
    for content in content_list:
        if content.xpath('./a/text()') == []:
            name = None
        else:
            name = content.xpath('./a/text()')[0]
        ggstart_time = content.xpath("./span/text()")[0]
        if int(len(driver.current_url)) < 130:
            url = "http://ggzyjyzx.yangzhou.gov.cn" + content.xpath('./a/@href')[0]
        else:
            url = content.xpath('./a/@href')[0]
        temp = [name, ggstart_time, url]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//span[@style='float:right;']")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))

    total_page = int(driver.find_element_by_xpath("//span[@style='float:right;']").text.split()[-2])
    driver.quit()
    return total_page


def f3(driver, url):
    driver.get(url)

    if url.split('.')[0] == 'http://218':
        try:
            locator = (By.CLASS_NAME, "panel")
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
            flag = True
        except:
            locator = (By.ID, "body")
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
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
            div = soup.find('div', class_='panel')
        else:
            div = soup.find('div', id='body')

    else:
        locator = (By.CLASS_NAME, "contentShow")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

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
        div = soup.find('div', class_='contentShow')
    return div


data = [
    #
    ["gcjs_zhaobiao_gg",
     "http://ggzyjyzx.yangzhou.gov.cn/qtyy/ggzyjyzx/right_list/right_list_jsgc.jsp?categorynum=003007&t=1542016237300",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_yucai_gg",
     "http://ggzyjyzx.yangzhou.gov.cn/qtyy/ggzyjyzx/right_list/right_list_jsgc.jsp?categorynum=003010&t=1542016237300",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_kongzhijia_gg",
     "http://ggzyjyzx.yangzhou.gov.cn/qtyy/ggzyjyzx/right_list/right_list_jsgc.jsp?categorynum=003009&t=1542016237300",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://ggzyjyzx.yangzhou.gov.cn/qtyy/ggzyjyzx/right_list/right_list_jsgc.jsp?categorynum=003014&t=1542016237300",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_dayi_gg",
     "http://ggzyjyzx.yangzhou.gov.cn/qtyy/ggzyjyzx/right_list/right_list_jsgc.jsp?categorynum=003011&t=1554170558638",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://ggzyjyzx.yangzhou.gov.cn/qtyy/ggzyjyzx/right_list/right_list_jsgc.jsp?categorynum=003008&t=1542016237300",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhaobiao_zjfb_gg",
     "http://ggzyjyzx.yangzhou.gov.cn/qtyy/ggzyjyzx/right_list/right_list_jsgc.jsp?categorynum=003015&t=1542016237300",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"method":"直接发包"}), f2],
    ["gcjs_zhaobiao_zhuanye_gg",
     "http://ggzyjyzx.yangzhou.gov.cn/qtyy/ggzyjyzx/right_list/right_list_jsgc.jsp?categorynum=003016&t=1542016237300",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"专业公告"}), f2],
    ["gcjs_zhongbiao_zhuanye_gg",
     "http://ggzyjyzx.yangzhou.gov.cn/qtyy/ggzyjyzx/right_list/right_list_jsgc.jsp?categorynum=003013&t=1542016237300",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"专业公告"}), f2],
    #
    ["zfcg_zhaobiao_gg",
     "http://ggzyjyzx.yangzhou.gov.cn/qtyy/ggzyjyzx/right_list/right_list_zfcg.jsp?categorynum=002001&t=1542016715239",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://ggzyjyzx.yangzhou.gov.cn/qtyy/ggzyjyzx/right_list/right_list_zfcg.jsp?categorynum=002002&t=1542016715239",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["jqita_gqita_bian_liu_gg",
     "http://ggzyjyzx.yangzhou.gov.cn/qtyy/ggzyjyzx/right_list/right_list_zfcg.jsp?categorynum=002003001&t=1543890561570",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"其他公告"}), f2],

    ["gcjs_jiaotong_zhaobiao_gg",
     "http://ggzyjyzx.yangzhou.gov.cn/qtyy/ggzyjyzx/right_list/right_list_cms.jsp?channel_id=71267922cf4040ba9ebabb1743e8a956&t=1542016803512",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_jiaotong_zhongbiaohx_gg",
     "http://ggzyjyzx.yangzhou.gov.cn/qtyy/ggzyjyzx/right_list/right_list_cms.jsp?channel_id=f3d3d84159d342c0b372db3bdae4fc41&t=1542016803512",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_jiaotong_zhongbiao_gg",
     "http://ggzyjyzx.yangzhou.gov.cn/qtyy/ggzyjyzx/right_list/right_list_cms.jsp?channel_id=9046e94e28d947be8700aa4ef85f5bbc&t=1542016803512",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_shuili_zhaobiao_gg",
     "http://ggzyjyzx.yangzhou.gov.cn/qtyy/ggzyjyzx/right_list/right_list_slgc_zbgg.jsp?t=1542017056662",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_shuili_zhong_zhonghx_gg",
     "http://ggzyjyzx.yangzhou.gov.cn/qtyy/ggzyjyzx/right_list/right_list_slgc_zbgs.jsp?t=1542017056662",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["yiliao_zhaobiao_gg",
     "http://ggzyjyzx.yangzhou.gov.cn/qtyy/ggzyjyzx/right_list/right_list_cms.jsp?channel_id=b11e7af511d049128efc01e1a4fe8544&t=1542017127691",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp,**kwargs):
    est_meta(conp, data=data, diqu="江苏省扬州市",**kwargs)
    est_html(conp, f=f3,**kwargs)


if __name__ == "__main__":
    conp=["postgres", "since2015", "192.168.3.171", "jiangsu", "yangzhou"]
    # url = "http://ggzyjyzx.yangzhou.gov.cn/qtyy/ggzyjyzx/right_list/right_list_slgc_zbgs.jsp?t=1542017056662"
    # driver = webdriver.Chrome()
    # driver.get(url)
    # print(f1(driver, 12))