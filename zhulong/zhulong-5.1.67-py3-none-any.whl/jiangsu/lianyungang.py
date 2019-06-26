import re

from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong.util.etl import est_html, est_meta, add_info
import time

_name_ = 'lianyungang'


def f1(driver, num):
    locator = (By.XPATH, "//tr[@class='ewb-trade-tr'][1]/td/a")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    try:
        locator = (By.ID, 'index')
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
        cnum = int(driver.find_element_by_xpath('//*[@id="index"]').text.split('/')[0])
    except:
        cnum = 1
    val = driver.find_element_by_xpath("//tr[@class='ewb-trade-tr'][1]/td[2]/a").get_attribute("href")[-50:]

    if cnum != int(num):
        time.sleep(1)
        driver.find_element_by_id('target').clear()
        driver.find_element_by_id('target').send_keys(num)
        driver.find_element_by_xpath("//a[@onclick='skip()']").click()
        locator = (By.XPATH, "//tr[@class='ewb-trade-tr'][1]/td[2]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    locator = (By.XPATH, "//tr[@class='ewb-trade-tr']")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//tr[@class='ewb-trade-tr']")
    for content in content_list:
        name = content.xpath("./td[2]/a/text()")[0]
        ggstart_time = content.xpath('./td[4]/text()')[0]
        if ggstart_time == '':
            ggstart_time = '0000-00-00'
        url = "http://spzx.lyg.gov.cn" + content.xpath("./td[2]/a/@href")[0]
        temp = [name, ggstart_time, url]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    try:
        locator = (By.XPATH, '//*[@id="index"]')
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
        total_page = driver.find_element_by_xpath('//*[@id="index"]').text.split('/')[1]
    except:
        total_page = 1
    driver.quit()
    return int(total_page)


def before(f, xmtype, ggtype):
    def wrap(*args):
        driver = args[0]
        switch(driver, xmtype, ggtype)
        return f(*args)

    return wrap


type = {
    "建设工程": [
        "search2('001001','','')",
        {
            "评定分离": "search2('001001006','','')",
            "招标公告": "search2('001001001','','')",
            "资格预审未入围": "search2('001001002','','')",
            "最高限价": "search2('001001003','','')",
            "评标结果公示": "search2('001001004','','')",
            "中标结果公告": "search2('001001005','','')",
            "预选招标": "search2('001001007','','')",
        }
    ],
    "交通工程": [
        "search2('001002','','')",
        {
            "招标公告": "search2('001002001','','')",
            "中标结果公告": "search2('001002002','','')",
        }
    ],
    "水利工程": [
        "search2('001003','','')",
        {
            "招标公告": "search2('001003001','','')",
            "中标结果公告": "search2('001003002','','')",
        }
    ],
    "政府采购": [
        "search2('001004','','')",
        {
            "采购公告": "search2('001004001','','')",
            "更正公告": "search2('001004006','','')",
            "废标公告": "search2('001004002','','')",
            "成交公告": "search2('001004004','','')",
        }
    ],
    "医药采购": [
        "search2('001008','','')",
        {
            "招标公告": "search2('001008001','','')",
            "中标公告": "search2('001008002','','')",
        }
    ],
    "其他行业": [
        "search2('001007','','')",
        {
            "招标公告": "search2('001007001','','')",
            "中标公告": "search2('001007002','','')",
        }
    ], }


def switch(driver, xmtype, ggtype):
    locator = (By.ID, 'index')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))

    driver.execute_script(type[xmtype][1][ggtype])


def f3(driver, url):
    driver.get(url)
    try:
        locator = (By.CLASS_NAME, "article-info")
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        flag = True
    except:
        locator = (By.CLASS_NAME, "ewb-container clearfix")
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
        div = soup.find('div', class_='article-info')
    else:
        div = soup.find('div', class_='ewb-container clearfix')
    return div


data = [
    # 工程建设
    ["gcjs_yucai_gg", "http://spzx.lyg.gov.cn/lygweb/jyxx/001001/001001007/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    ["gcjs_zhaobiao_gg", "http://spzx.lyg.gov.cn/lygweb/jyxx/001001/001001001/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    ["gcjs_zgysjg_gg", "http://spzx.lyg.gov.cn/lygweb/jyxx/001001/001001002/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    ["gcjs_kongzhijia_gg", "http://spzx.lyg.gov.cn/lygweb/jyxx/001001/001001003/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],

    ["gcjs_zhongbiao_gg", "http://spzx.lyg.gov.cn/lygweb/jyxx/001001/001001005/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://spzx.lyg.gov.cn/lygweb/jyxx/001001/001001006/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    # 交通
    #
    ["gcjs_jiaotong_zhaobiao_gg", "http://spzx.lyg.gov.cn/lygweb/jyxx/001002/001002001/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    ["gcjs_jiaotong_zhongbiao_gg", "http://spzx.lyg.gov.cn/lygweb/jyxx/001002/001002002/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    # # 水利
    #
    ["gcjs_shuili_zhaobiao_gg", "http://spzx.lyg.gov.cn/lygweb/jyxx/001003/001003001/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],

    ["gcjs_gqita_shuili_zhong_zhonghx_gg", "http://spzx.lyg.gov.cn/lygweb/jyxx/001003/001003002/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    # # 政府采购
    #
    ["zfcg_zhaobiao_gg", "http://spzx.lyg.gov.cn/lygweb/jyxx/001004/001004001/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    ["zfcg_biangeng_gg", "http://spzx.lyg.gov.cn/lygweb/jyxx/001004/001004006/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    ["zfcg_zhongbiao_gg", "http://spzx.lyg.gov.cn/lygweb/jyxx/001004/001004002/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    ["zfcg_liubiao_gg", "http://spzx.lyg.gov.cn/lygweb/jyxx/001004/001004004/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    ["zfcg_yucai_gg", "http://spzx.lyg.gov.cn/lygweb/jyxx/001004/001004003/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],

    ["yiliao_zhaobiao_gg", "http://spzx.lyg.gov.cn/lygweb/jyxx/001008/001008001/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    ["yiliao_zhongbiao_gg", "http://spzx.lyg.gov.cn/lygweb/jyxx/001008/001008002/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    ["jqita_zhaobiao_gg", "http://spzx.lyg.gov.cn/lygweb/jyxx/001007/001007001/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
    ["jqita_gqita_zhong_zhonghx_gg", "http://spzx.lyg.gov.cn/lygweb/jyxx/001007/001007002/tradeInfo.html",
     ["name", "ggstart_time", "href", "info"],
     f1, f2],
]


def work(conp, **kwargs):
    est_meta(conp, data=data, diqu="江苏省连云港市", **kwargs)
    est_html(conp, f=f3, **kwargs)


if __name__ == '__main__':
    conp = ["postgres", "since2015", "192.168.3.171", "jiangsu", "lianyungang"]
    work(conp, num=8)
