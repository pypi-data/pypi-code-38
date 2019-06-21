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

_name_='tieling'
def f1(driver, num):
    if "Index" in driver.current_url:
        cnum = driver.current_url.split('?')[0].split('/')[-1]
    else:cnum=1
    locator = (By.XPATH, "//div[@class='page_r_list']/ul/li/a")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//div[@class='page_r_list']/ul/li/a").get_attribute("href")[-40:]
    if int(cnum) != int(num):
        url = re.sub(r'\d+\?',str(num) + '?',driver.current_url)
        driver.get(url)
        locator = (By.XPATH, '//div[@class="page_r_list"]/ul/li/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@class='page_r_list']/ul/li")
    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip().replace('/','-')
        url = "http://tlggzyjy.com" + content.xpath("./a/@href")[0].strip()
        temp = [name, ggstart_time, url]

        data.append(temp)
        # print(temp)
    if len(data) == 1:data.append(['此条数据负责占位子,写入数据库后可删除。','',''])
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df

def f2(driver):
    if "Index" in driver.current_url:
        locator = (By.XPATH,"//div[@class='page_pagding']/div/span")
        WebDriverWait(driver,20).until(EC.presence_of_element_located(locator))
        total_page = driver.find_element_by_xpath("//div[@class='page_pagding']/div/span[last()]").text
    # return total_page
    else:total_page = 1
    driver.quit()
    return int(total_page)

def f3(driver, url):
    driver.get(url)
    locator = (By.CLASS_NAME, "page_r_info")
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
    div = soup.find("div",class_="page_r_info")
    return div


data = [
    ["zfcg_zhaobiao_tielingshi_gg",
     "http://tlggzyjy.com/Project/Index/1?ProjectState=1&CountyId=1&TradeTypeId=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{"area":"铁岭市"}), f2],
    ["zfcg_zhaobiao_tielingxian_gg",
     "http://tlggzyjy.com/Project/Index/1?ProjectState=1&CountyId=2&TradeTypeId=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"铁岭县"}), f2],
    ["zfcg_zhaobiao_kaiyuanshi_gg",
     "http://tlggzyjy.com/Project/Index/1?ProjectState=1&CountyId=3&TradeTypeId=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"开原市"}), f2],
    ["zfcg_zhaobiao_changtuxian_gg",
     "http://tlggzyjy.com/Project/Index/1?ProjectState=1&CountyId=4&TradeTypeId=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"昌图县"}), f2],
    ["zfcg_zhaobiao_xifengxian_gg",
     "http://tlggzyjy.com/Project?ProjectState=1&CountyId=5&TradeTypeId=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"西丰县"}), f2],
    ["zfcg_zhaobiao_diaobingshanshi_gg",
     "http://tlggzyjy.com/Project/Index/1?ProjectState=1&CountyId=6&TradeTypeId=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"调兵山市"}), f2],
    ["zfcg_zhaobiao_yinzhou_gg",
     "http://tlggzyjy.com/Project/Index/1?ProjectState=1&CountyId=7&TradeTypeId=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"银州"}), f2],
    ["zfcg_zhaobiao_qinghequ_gg",
     "http://tlggzyjy.com/Project/Index/1?ProjectState=1&CountyId=8&TradeTypeId=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"清河区"}), f2],
    ["zfcg_zhaobiao_kaifaqu_gg",
     "http://tlggzyjy.com/Project?ProjectState=1&CountyId=9&TradeTypeId=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"开发区"}), f2],



    ["zfcg_zhongbiao_tielingshi_gg",
     "http://tlggzyjy.com/Project/Index/1?ProjectState=3&CountyId=1&TradeTypeId=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"铁岭市"}), f2],
    ["zfcg_zhongbiao_tielingxian_gg",
     "http://tlggzyjy.com/Project/Index/1?ProjectState=3&CountyId=2&TradeTypeId=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"铁岭县"}), f2],
    ["zfcg_zhongbiao_changtuxian_gg",
     "http://tlggzyjy.com/Project/Index/1?ProjectState=3&CountyId=4&TradeTypeId=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"昌图县"}), f2],
    ["zfcg_zhongbiao_diaobingshanshi_gg",
     "http://tlggzyjy.com/Project/Index/1?ProjectState=3&CountyId=6&TradeTypeId=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"调兵山市"}), f2],
    ["zfcg_zhongbiao_yinzhou_gg",
     "http://tlggzyjy.com/Project/Index/1?ProjectState=3&CountyId=7&TradeTypeId=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"银州"}), f2],
    ["zfcg_zhongbiao_kaifaqu_gg",
     "http://tlggzyjy.com/Project?ProjectState=3&CountyId=9&TradeTypeId=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"开发区"}), f2],

    #gcjs _ zhaobiao
    ["gcjs_zhaobiao_tielingshi_gg",
     "http://tlggzyjy.com/Project/Index/1?ProjectState=1&CountyId=1&TradeTypeId=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"铁岭市"}), f2],
    ["gcjs_zhaobiao_tielingxian_gg",
     "http://tlggzyjy.com/Project/Index/1?ProjectState=1&CountyId=2&TradeTypeId=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"铁岭县"}), f2],
    ["gcjs_zhaobiao_kaiyuanshi_gg",
     "http://tlggzyjy.com/Project?ProjectState=1&CountyId=3&TradeTypeId=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"开原市"}), f2],
    ["gcjs_zhaobiao_changtuxian_gg",
     "http://tlggzyjy.com/Project/Index/1?ProjectState=1&CountyId=4&TradeTypeId=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"昌图县"}), f2],
    ["gcjs_zhaobiao_xifengxian_gg",
     "http://tlggzyjy.com/Project?ProjectState=1&CountyId=5&TradeTypeId=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"西丰县"}), f2],
    ["gcjs_zhaobiao_diaobingshanshi_gg",
     "http://tlggzyjy.com/Project/Index/1?ProjectState=1&CountyId=6&TradeTypeId=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"调兵山市"}), f2],
    ["gcjs_zhaobiao_yinzhou_gg",
     "http://tlggzyjy.com/Project?ProjectState=1&CountyId=7&TradeTypeId=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"银州"}), f2],

    # gcjs _ zhongbiao
    ["gcjs_zhongbiao_tielingshi_gg",
     "http://tlggzyjy.com/Project?ProjectState=3&CountyId=1&TradeTypeId=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"铁岭市"}), f2],
    ["gcjs_zhongbiao_tielingxian_gg",
     "http://tlggzyjy.com/Project?ProjectState=3&CountyId=2&TradeTypeId=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"铁岭县"}), f2],

    ["gcjs_zhongbiao_changtuxian_gg",
     "http://tlggzyjy.com/Project?ProjectState=3&CountyId=4&TradeTypeId=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"昌图县"}), f2],



]


def work(conp,**args):
    est_meta(conp, data=data, diqu="辽宁省铁岭市",**args)
    est_html(conp, f=f3,**args)


if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "liaoning", "tieling"])
