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
from zhulong4.util.etl import est_html, est_meta, add_info
import time

_name_ = 'etp_fawiec_com'


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="detail clearfloat"]/ul/li')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//div[@class="detail clearfloat"]/ul/li/div/a').get_attribute("href")[-50:]
    cnum = driver.find_element_by_xpath('//a[@class="cur-ye"]/span').text
    if int(cnum) != int(num):
        driver.execute_script('pagination(%s);' % num)
        locator = (By.XPATH, '''//div[@class="detail clearfloat"]/ul/li/div/a[not(contains(@href,"%s"))]''' % val)
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="detail clearfloat"]/ul/li')
    for content in content_list:
        name = content.xpath("./div[1]/a/text()")[0].strip()
        url = "https://etp.faw.cn" + content.xpath("./div[1]/a/@href")[0].strip()
        ggstart_time = content.xpath("./div[2]/span[2]/text()")[0].split('：')[1]
        gg_type = content.xpath("./div[2]/span[1]/text()")[0].strip()
        try:
            deadline = content.xpath("./div[1]/span")[0].xpath('string(.)')
        except:
            deadline = 'None'
        project_type = re.sub(r'\s+','',content.xpath("./div[3]/span[1]/text()")[0].strip())
        # print(name,url,ggstart_time,deadline,project_type)
        info = json.dumps({'gg_type':gg_type,'deadline':deadline,'project_type':project_type})
        temp = [name, ggstart_time, url, info]
        data.append(temp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    driver.maximize_window()
    locator = (By.XPATH, '//div[@class="page-container"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_page = driver.find_element_by_xpath('//div[@class="page-container"]/a[last()-1]/span').text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="detail"]')
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
    div = soup.find('div', class_='detail')
    return div


data = [
    ["qy_zhaobiao_gg",
     "https://etp.faw.cn/gg/ggList?zbLeiXing=&xmLeiXing=&ggStartTimeEnd=",
     ["name", "ggstart_time", "href","info"], f1, f2],
    ["qy_biangeng_gg",
     "https://etp.faw.cn/gg/bgggList?zbLeiXing=&xmLeiXing=&ggStartTimeEnd=",
     ["name", "ggstart_time", "href","info"], f1, f2],
    ["qy_zhongbiaohx_gg",
     "https://etp.faw.cn/gg/zbhxrList?zbLeiXing=&xmLeiXing=&ggStartTimeEnd=",
     ["name", "ggstart_time", "href","info"], f1, f2],

    ["qy_zhongbiao_gg",
     "https://etp.faw.cn/gg/zbjgList?zbLeiXing=&xmLeiXing=&ggStartTimeEnd=",
     ["name", "ggstart_time", "href","info"], f1, f2],
    ["qy_zsjg_gg",
     "https://etp.faw.cn/gg/zgscList?zbLeiXing=&xmLeiXing=&ggStartTimeEnd=",
     ["name", "ggstart_time", "href","info"], f1, f2],

    ["qy_zhaobiao_fzb_gg",
     "https://etp.faw.cn/gg/toXinXiList?gongGaoType=5&xmLeiXing=&ggStartTimeEnd=&hangYeType=5",
     ["name", "ggstart_time", "href","info"], add_info(f1,{'tag':'非招标'}), f2],
    ["qy_biangeng_fzb_gg",
     "https://etp.faw.cn/gg/toXinXiList?gongGaoType=6&xmLeiXing=&ggStartTimeEnd=&hangYeType=5",
     ["name", "ggstart_time", "href","info"], add_info(f1,{'tag':'非招标'}), f2],
    ["qy_zhongbiaohx_fzb_gg",
     "https://etp.faw.cn/gg/toXinXiList?gongGaoType=7&xmLeiXing=&ggStartTimeEnd=&hangYeType=5",
     ["name", "ggstart_time", "href","info"], add_info(f1,{'tag':'非招标'}), f2],

    ["qy_zhongbiao_fzb_gg",
     "https://etp.faw.cn/gg/toXinXiList?gongGaoType=15&xmLeiXing=&ggStartTimeEnd=&hangYeType=5",
     ["name", "ggstart_time", "href","info"], add_info(f1,{'tag':'非招标'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="中国一汽电子招标采购平台", **args)
    est_html(conp, f=f3, **args)

def main():
    conp = ["postgres", "since2015", "192.168.3.171", "anbang_qiye", "etp_fawiec_com"]
    work(conp,num=5)
    # driver = webdriver.Chrome()
    # driver.get("https://etp.faw.cn/gg/toXinXiList?gongGaoType=5&xmLeiXing=&ggStartTimeEnd=&hangYeType=5")
    # print(f1(driver, 2))
    # f1(driver, 3)
    # f1(driver, 10)
    #
    # print(f2(driver))
    #
    # driver = webdriver.Chrome()
    # driver.get("https://b2b.10086.cn/b2b/main/showBiao!preShowBiao.html?noticeType=list2")
    # f1(driver, 2)
    # f1(driver, 3)
    # f1(driver, 10)
    #
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # driver.get("https://b2b.10086.cn/b2b/main/showBiao!preShowBiao.html?noticeType=list3")
    # f1(driver, 2)
    # f1(driver, 3)
    # f1(driver, 10)
    #
    # print(f2(driver))
# driver = webdriver.Chrome()
# print(f3(driver, 'http://bidding.ceiec.com.cn/bggg/5235.jhtml'))
# driver.close()
if __name__ == "__main__":
    main()