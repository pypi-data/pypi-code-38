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
from zhulong.util.etl import est_html, est_meta
import time

_name_='fuxin'
def f1(driver, num):
    locator = (By.XPATH,'//*[@id="MoreInfoList1_Pager"]/table/tbody/tr/td[1]/font[3]/b')
    WebDriverWait(driver,20).until(EC.presence_of_element_located(locator))
    cnum = int(driver.find_element_by_xpath('//*[@id="MoreInfoList1_Pager"]/table/tbody/tr/td[1]/font[3]/b').text)
    locator = (By.XPATH, '//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a').get_attribute("href")[-60:]
    if int(cnum) != int(num):
        driver.execute_script("javascript:__doPostBack('MoreInfoList1$Pager','%s')"%num)

        locator = (By.XPATH, '//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a')
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        locator = (
            By.XPATH, '//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    locator = (By.CLASS_NAME, 'border1')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//table[@id='MoreInfoList1_DataGrid1']//tr")
    for content in content_list:
        name = content.xpath("./td/a/text()")[0].strip()
        ggstart_time = content.xpath("./td[3]/text()")[0].strip()
        url = "http://www.fxggzy.com"+content.xpath("./td/a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH,'//*[@id="MoreInfoList1_Pager"]/table/tbody/tr/td[1]/font[2]/b')
    WebDriverWait(driver,20).until(EC.presence_of_element_located(locator))
    total_page = int(driver.find_element_by_xpath('//*[@id="MoreInfoList1_Pager"]/table/tbody/tr/td[1]/font[2]/b').text)
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@class='tab topd']")
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
    div = soup.find('table',class_="tab topd")
    return div

data = [
    ["zfcg_zhaobiao_gg",
     "http://www.fxggzy.com/fx_front/jyxx/001002/001002001/MoreInfo.aspx?CategoryNum=001002001",
     ["name", "ggstart_time", "href", "info"],f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://www.fxggzy.com/fx_front/jyxx/001002/001002003/MoreInfo.aspx?CategoryNum=001002003",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://www.fxggzy.com/fx_front/jyxx/001002/001002002/MoreInfo.aspx?CategoryNum=001002002",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_gg",
     "http://www.fxggzy.com/fx_front/jyxx/001001/001001001/MoreInfo.aspx?CategoryNum=001001001",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://www.fxggzy.com/fx_front/jyxx/001001/001001002/MoreInfo.aspx?CategoryNum=001001002",
     ["name", "ggstart_time", "href", "info"], f1, f2],



]


def work(conp,**args):
    est_meta(conp, data=data, diqu="辽宁省阜新市",**args)
    est_html(conp, f=f3,**args)


if __name__ == "__main__":
    conp=["postgres", "since2015", "192.168.3.171", "liaoning", "fuxin"]
    import sys
    arg=sys.argv
    if len(arg) >3:
        work(conp,num=int(arg[1]),total=int(arg[2]),html_total=int(arg[3]))
    elif len(arg) == 2:
        work(conp, html_total=int(arg[1]))
    else:
        work(conp)