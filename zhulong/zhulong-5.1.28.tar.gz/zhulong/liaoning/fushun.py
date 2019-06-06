import re

from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong.util.etl import est_html, est_gg, est_meta, add_info
import time


_name_="fushun"

def f1(driver, num):
    locator = (By.XPATH, '//div[@id="right"]/table/tbody/tr/td/a')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    val = driver.find_element_by_xpath('//div[@id="right"]/table/tbody/tr[1]/td/a').get_attribute("href")[-60:]
    locator = (By.CLASS_NAME, "huifont")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    cnum = driver.find_element_by_xpath('//td[@class="huifont"]').text.split('/')[0]
    if int(cnum) != int(num):
        driver.execute_script("ShowNewPage('./?Paging={}');".format(num))
        locator = (By.XPATH, '//div[@id="right"]/table/tbody/tr/td/a')
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        locator = (
            By.XPATH, "//div[@id='right']/table/tbody/tr[1]/td/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//*[@id="right"]/table[2]/tbody/tr[@height="15"]')
    data = []
    for content in content_list:
        name = content.xpath("./td/a/text()")[0].strip()
        new_url = "http://fsggzy.fushun.gov.cn" + content.xpath("./td/a/@href")[0].strip()
        ggstart_time = content.xpath(".//font[@class='ellipsis']/text()")[0].strip()
        temp = [name, ggstart_time, new_url]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df



def f2(driver):
    locator = (By.CLASS_NAME, "huifont")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    total_page = driver.find_element_by_xpath('//td[@class="huifont"]').text.split('/')[1]

    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table/tbody/tr/td[2]/table")
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
    table = soup.find("table")
    table = table.find("table")
    table = table.find("table")
    div = table.find("table")


    return div





data = [
    # 城市建设
    ["gcjs_zhaobiao_gg",
     "http://fsggzy.fushun.gov.cn/fsggzy/jyxx/071001/071001001/",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://fsggzy.fushun.gov.cn/fsggzy/jyxx/071001/071001002/",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://fsggzy.fushun.gov.cn/fsggzy/jyxx/071001/071001003/",["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_sj_gg",
     "http://fsggzy.fushun.gov.cn/fsggzy/jyxx/071002/071002001/071002001001/",["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"市级"}), f2],
    ["zfcg_zhaobiao_xj_gg",
     "http://fsggzy.fushun.gov.cn/fsggzy/jyxx/071002/071002001/071002001002/",["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"县级"}), f2],
    ["zfcg_zhaobiao_dyly_gg",
     "http://fsggzy.fushun.gov.cn/fsggzy/jyxx/071002/071002002/071002002001/",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://fsggzy.fushun.gov.cn/fsggzy/jyxx/071002/071002003/071002003001/",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://fsggzy.fushun.gov.cn/fsggzy/jyxx/071002/071002004/071002004001/",["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_yanshou_gg",
     "http://fsggzy.fushun.gov.cn/fsggzy/jyxx/071002/071002005/",["name", "ggstart_time", "href", "info"], f1, f2],


    ["yiliao_zhaobiao_gg",
     "http://fsggzy.fushun.gov.cn/fsggzy/jyxx/071005/071005001/",["name", "ggstart_time", "href", "info"], f1, f2],
    ["yiliao_zhongbiao_gg",
     "http://fsggzy.fushun.gov.cn/fsggzy/jyxx/071005/071005002/",["name", "ggstart_time", "href", "info"], f1, f2],

]

def work(conp,**args):
    est_meta(conp, data=data, diqu="辽宁省抚顺市",**args)
    est_html(conp, f=f3,**args)
#
# 辽宁-抚顺 网站打不开
# date ： 2019年4月4日16:53:02
#
if __name__ == "__main__":
    conp=["postgres", "since2015", "192.168.3.171", "liaoning", "fushun"]
    import sys
    arg=sys.argv
    if len(arg) >3:
        work(conp,num=int(arg[1]),total=int(arg[2]),html_total=int(arg[3]))
    elif len(arg) == 2:
        work(conp, html_total=int(arg[1]))
    else:
        work(conp)