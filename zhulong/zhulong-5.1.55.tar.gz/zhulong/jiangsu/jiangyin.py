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

_name_='jiangyin'
def f3(driver, url):
    driver.get(url)
    locator = (By.CLASS_NAME, "ind35")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))

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
    div = soup.find('div', class_='ind35')
    return div


def f1(driver, num):
    # zfcg_yucai_gg和gcjs_liubiao_gg 两个表都是shtml结尾。liubiao需要翻页，yucai内容不够不要翻页，后期内容多了，或许需要修改js翻页代码。
    # if "shtml" in driver.current_url:
    locator = (By.XPATH, '//div[@class="ind32"]/ul/li')
    WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//div[@class="ind32"]/ul/li/a').get_attribute("href")[-20:]

    locator = (By.CLASS_NAME, "channelpages")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum = int(driver.find_element_by_xpath("//div[@class='channelpages']/p/span[1]").text)
    if int(num) != cnum:
        url = driver.current_url
        if int(num) != 1:
            url = url.rsplit("/",maxsplit=1)[0] + "/index_"+ str(num) + ".shtml"
        else:
            url = url.rsplit("/",maxsplit=1)[0] + "/index"+".shtml"
        driver.get(url)
        locator = (By.XPATH, '//div[@class="ind32"]/ul/li/a[not(contains(@href,"%s"))]'%val)
        WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located(locator))
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="ind32"]/ul/li')
    data = []
    for content in content_list:
        name = content.xpath("./a/text()")[0]
        ggstart_time = content.xpath("./span/text()")[0]
        url = "http://www.jiangyin.gov.cn" + content.xpath("./a/@href")[0]
        temp = [name, ggstart_time, url]
        data.append(temp)

    df = pd.DataFrame(data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.CLASS_NAME, "channelpages")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = int(driver.find_element_by_xpath("//div[@class='channelpages']/p/span[2]").text)
    driver.quit()
    return total


data = [

    ["gcjs_zhaobiao_gg","http://www.jiangyin.gov.cn/ggzy/jsgc/ggxx/zbgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_kongzhijia_gg","http://www.jiangyin.gov.cn/ggzy/jsgc/ggxx/zgxjgs/index.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_biangeng_gg","http://www.jiangyin.gov.cn/ggzy/jsgc/ggxx/bggg/index.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg","http://www.jiangyin.gov.cn/ggzy/jsgc/jggsgg/zbjggg/index.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg","http://www.jiangyin.gov.cn/ggzy/jsgc/jggsgg/pbjggs/index.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_liu_zhonghx_zgysjg_gg","http://www.jiangyin.gov.cn/ggzy/jsgc/jggsgg/qtgsgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["zfcg_yucai_gg", "http://www.jiangyin.gov.cn/ggzy/zfcg/ggxx/cgyg/index.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_gg","http://www.jiangyin.gov.cn/ggzy/zfcg/ggxx/zbcggg/index.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg","http://www.jiangyin.gov.cn/ggzy/zfcg/ggxx/cgjggg/index.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg","http://www.jiangyin.gov.cn/ggzy/zfcg/ggxx/gzcqgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_baojiaxuqiu_gg", "http://www.jiangyin.gov.cn/ggzy/zfcg/ggxx/bjxqgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"报价需求"}), f2],
    ["zfcg_gqita_baojiajieguo_gg", "http://www.jiangyin.gov.cn/ggzy/zfcg/ggxx/bjjggg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"报价结果"}), f2],
]


def work(conp,**kwargs):
    est_meta(conp, data=data, diqu="江苏省江阴市",**kwargs)
    est_html(conp, f=f3,**kwargs)


if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "jiangsu", "jiangyin"])


