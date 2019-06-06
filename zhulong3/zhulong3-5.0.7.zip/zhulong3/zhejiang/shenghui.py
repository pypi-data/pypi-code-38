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

_name_ = 'zhejiang_shenghui'


def f1(driver, num):
    locator = (By.XPATH, '//table[contains(@id,"DataGrid1")]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//table[contains(@id,"DataGrid1")]/tbody/tr/td/a').get_attribute("href")[-30:]
    try:
        cnum_temp = driver.find_element_by_xpath('//font[@color="red"][2]').text
        cnum = re.findall("\/(\d+)", cnum_temp)[0]
    except:
        cnum = driver.find_element_by_xpath('//font[@color="red"]').text
    locator = (By.XPATH, '//table[contains(@id,"DataGrid1")]/tbody/tr')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    if int(cnum) != int(num):
        if 'bcwj' in driver.current_url.lower():
            driver.execute_script("javascript:__doPostBack('BcwjInfoList1$Pager','%s')"%num)
        else:
            driver.execute_script("javascript:__doPostBack('%sList1$Pager','%s')"%(re.findall(r'ce\/(.+?)More',driver.current_url)[0],num))

        locator = (By.XPATH, "//table[contains(@id,'DataGrid1')]/tbody/tr/td/a[not(contains(@href,'%s'))]" % val)

    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table[contains(@id,"DataGrid1")]/tbody/tr')
    for content in content_list:
        try:
            name = content.xpath("./td/a/@title")[0].strip()
            if "zsProName".lower() in driver.current_url.lower():
                url = "http://www.zmctc.com/zjgcjy/Notice/"  +content.xpath("./td/a/@href")[0].strip()
            else:
                url = content.xpath("./td/a/@href")[0].strip()
            ggstart_time = content.xpath("./td[last()]//text()")[0].strip().strip('(').strip(')')
            project_code= content.xpath('./td[2]/font/text()|./td[2]/a/font/text()')[0].strip().strip('[').strip(']')
            info = json.dumps({'project_code':project_code},ensure_ascii=False)
            temp = [name,ggstart_time, url, info]
            data.append(temp)
            # print(temp)
        except:
            continue
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    try:
        locator = (By.XPATH, '//font[@color="red"][2]')
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        total_temp = driver.find_element_by_xpath('//font[@color="red"][2]').text
        total_page = re.findall("\/(\d+)", total_temp)[0]
    except:
        #//font[@color="blue"][2]
        locator = (By.XPATH, '//font[@color="blue"][2]')
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        total_page = driver.find_element_by_xpath('//font[@color="blue"][2]').text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//table[@id="tblInfo"]|//td[@class="TableRight"]')
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
    if "TableRight" in page:
        div = soup.find('td',class_='TableRight')
    else:
        div = soup.find('table', id='tblInfo')
    return div


data = [
    ["gcjs_zhaobiao_wenjian_gg",   # 网站自身重复
     "http://www.zmctc.com/zjgcjy/Notice/ZBWJInfoMore.aspx",
     ["name", "ggstart_time","href",  "info"], add_info(f1,{"Tag":"招标文件公示"}), f2],
    ["gcjs_zhaobiao_gg",
     "http://www.zmctc.com/zjgcjy/Notice/AfficheInfoMore.aspx",
     ["name", "ggstart_time","href",  "info"], f1, f2],
    ["gcjs_zhaobiao_buchong_gg",
     "http://www.zmctc.com/zjgcjy/Notice/BcwjMore.aspx",
     ["name", "ggstart_time","href",  "info"], add_info(f1,{"Tag":"补充文件"}), f2],

    ["gcjs_zhongbiao_gg",
     "http://www.zmctc.com/zjgcjy/Notice/tblOSInfoMore.aspx",  # unormal  21  page2
     ["name", "ggstart_time","href",  "info"], f1, f2],

    ["gcjs_zgysjg_gg",
     "http://www.zmctc.com/zjgcjy/Notice/zsProNameInfoMore.aspx",  # id
     ["name", "ggstart_time","href",  "info"], f1, f2],
    ["gcjs_gqita_pb_gg",
     "http://www.zmctc.com/zjgcjy/Notice/tblZJGSMore.aspx",
     ["name", "ggstart_time","href",  "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="浙江省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "zhejiang"]
    work(conp,num=1,headless=False)
    # driver = webdriver.Chrome()
    # driver.get("http://www.zmctc.com/zjgcjy/Notice/ZBWJInfoMore.aspx")
    # f1(driver, 2)
    # driver.get("http://www.zmctc.com/zjgcjy/Notice/zsProNameInfoMore.aspx")
    # f1(driver, 3)
    # driver.get("http://www.zmctc.com/zjgcjy/Notice/tblOSInfoMore.aspx")
    # f1(driver, 10)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver,
    #          'http://new.zmctc.com/zjgcjy/infodetail/?infoid=1c67f87d-5587-4e98-9ad5-8219f55e0b9e&categoryNum=004006002'))
    # driver.close()
