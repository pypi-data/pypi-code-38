import re
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
import pandas as pd
from zhulong.util.etl import est_meta, est_html, add_info

_name_ = "xinganmeng"


def f1(driver, num):
    locator = (By.XPATH,"//li[@class='list-body-item']")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//li[@class='list-body-item'][1]/a").get_attribute("href")[-50:]

    locator = (By.XPATH, "//td[@class='yahei redfont']")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    cnum = driver.find_element_by_xpath("//td[@class='yahei redfont']").text
    flag = 0
    # return
    while int(cnum) != int(num):
        try:
            driver.execute_script("window.location.href='./?Paging=%s'"%num)
            locator = (By.XPATH, "//li[@class='list-body-item'][1]/a[not(contains(@href,'%s'))]" % val)
            WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
            break
        except:
            if flag >=5:break
            flag+=1
            driver.refresh()
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//td[@class='yahei redfont']")))
            cnum = driver.find_element_by_xpath("//td[@class='yahei redfont']").text

    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//li[@class='list-body-item']")
    for content in content_list:
        name = content.xpath("./a/span[1]/text()")[0].strip()
        ggstart_time = content.xpath("./a/span[2]/text()")[0].strip()
        url = "http://ggzy.xam.gov.cn" + content.xpath("./a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    # print("这是第[{}]页".format(num))
    return df


def f2(driver):
    locator = (By.XPATH, "//td[@class='huifont']")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    total_page = re.findall('\/(\d+)',driver.find_element_by_xpath("//td[@class='huifont']").text)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='detail-content']")
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
    div = soup.find('div', class_='detail-content')
    # print(div)
    return div


data = [
    ["gcjs_zhaobiao_fjsz_gg",
     "http://ggzy.xam.gov.cn/xamggzy/jyxx/004001/004001001/004001001001/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"房建市政工程"}), f2],
    ["gcjs_biangeng_fjsz_gg",
     "http://ggzy.xam.gov.cn/xamggzy/jyxx/004001/004001001/004001001002/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"房建市政工程"}), f2],
    ["gcjs_zhongbiaohx_fjsz_gg",
     "http://ggzy.xam.gov.cn/xamggzy/jyxx/004001/004001001/004001001004/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"房建市政工程"}), f2],
    ["gcjs_liubiao_fjsz_gg",
     "http://ggzy.xam.gov.cn/xamggzy/jyxx/004001/004001001/004001001006/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"房建市政工程"}), f2],


    ["gcjs_dayi_fjsz_gg",
     "http://ggzy.xam.gov.cn/xamggzy/jyxx/004001/004001001/004001001003/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"房建市政工程"}), f2],

    ["gcjs_biangeng_2_fjsz_gg",
     "http://ggzy.xam.gov.cn/xamggzy/jyxx/004001/004001001/004001001005/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"房建市政工程"}), f2],

    ["gcjs_jiaotong_zhaobiao_gg",
     "http://ggzy.xam.gov.cn/xamggzy/jyxx/004001/004001002/004001002001/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_jiaotong_biangeng_gg",
     "http://ggzy.xam.gov.cn/xamggzy/jyxx/004001/004001002/004001002002/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_jiaotong_zhongbiaohx_gg",
     "http://ggzy.xam.gov.cn/xamggzy/jyxx/004001/004001002/004001002004/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_jiaotong_liubiao_gg",
     "http://ggzy.xam.gov.cn/xamggzy/jyxx/004001/004001002/004001002006/",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["gcjs_shuili_zhaobiao_gg",
     "http://ggzy.xam.gov.cn/xamggzy/jyxx/004001/004001003/004001003001/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuili_biangeng_gg",
     "http://ggzy.xam.gov.cn/xamggzy/jyxx/004001/004001003/004001003002/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuili_zhongbiaohx_gg",
     "http://ggzy.xam.gov.cn/xamggzy/jyxx/004001/004001003/004001003004/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuili_liubiao_gg",
     "http://ggzy.xam.gov.cn/xamggzy/jyxx/004001/004001003/004001003006/",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["gcjs_qita_zhaobiao_gg",
     "http://ggzy.xam.gov.cn/xamggzy/jyxx/004001/004001004/004001004001/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'其他工程'}), f2],
    ["gcjs_qita_biangeng_gg",
     "http://ggzy.xam.gov.cn/xamggzy/jyxx/004001/004001004/004001004002/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'其他工程'}), f2],
    ["gcjs_qita_zhongbiaohx_gg",
     "http://ggzy.xam.gov.cn/xamggzy/jyxx/004001/004001004/004001004004/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'其他工程'}), f2],
    ["gcjs_qita_liubiao_gg",
     "http://ggzy.xam.gov.cn/xamggzy/jyxx/004001/004001004/004001004006/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'tag':'其他工程'}), f2],



    ["zfcg_zhaobiao_gg",
     "http://ggzy.xam.gov.cn/xamggzy/jyxx/004002/004002001/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://ggzy.xam.gov.cn/xamggzy/jyxx/004002/004002003/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://ggzy.xam.gov.cn/xamggzy/jyxx/004002/004002002/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_liubiao_gg",
     "http://ggzy.xam.gov.cn/xamggzy/jyxx/004002/004002006/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **kwargs):
    est_meta(conp, data=data, diqu="内蒙古自治区兴安盟", **kwargs)
    est_html(conp, f=f3, **kwargs)


if __name__ == "__main__":
     work(conp=["postgres", "since2015", "192.168.3.171", "neimenggu", "xinganmeng"],pagelaodtimeout=40,num=5)

    # driver = webdriver.Chrome()

    # driver.get("http://ggzy.xam.gov.cn/xamggzy/jyxx/004002/004002001/")
    # for i in range(60,92):
    #     f1(driver,i)