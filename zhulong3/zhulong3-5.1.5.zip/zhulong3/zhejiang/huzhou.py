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

_name_ = 'zhejiang_huzhou'


def f1(driver, num):
    locator = (By.XPATH, '//table[@align="center"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath('//td[@class="yahei redfont"]').text
    locator = (By.XPATH, '//table[@align="center"]/tbody')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//table[@align="center"]/tbody/tr[2]/td/a').get_attribute("href")[-60:]
    if int(cnum) != int(num):
        url = re.sub('Paging=\d+', 'Paging=' + str(num), driver.current_url)
        driver.get(url)
        locator = (By.XPATH, "//table[@align='center']/tbody/tr[2]/td/a[not(contains(@href,'%s'))]" % val)
        for _ in range(5):
            try:
                WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located(locator))
                break
            except:
                driver.refresh()
    data = []
    page = driver.page_source
    body = etree.HTML(page)

    content_list = body.xpath('//table[@align="center"]/tbody/tr[@height="24"]')
    for content in content_list:
        # //table[@align="center"]/tbody/tr[1]/child::td
        if len(content.xpath("./child::td")) > 1:
            name = content.xpath("./td/a/@title")[0].strip()
            url = "http://ggzy.huzhou.gov.cn/" + content.xpath("./td/a/@href")[0].strip()
            ggstart_time = content.xpath("./td[last()]/font/text()")[0].strip()
            try:
                area = content.xpath('./td/a/font/text()')[0].strip()
            except:
                area = "None"
            info = json.dumps({"area": area}, ensure_ascii=False)

            temp = [name, ggstart_time, url, info]
            data.append(temp)
            # print('temp', temp)
        else:
            continue
    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//td[@class="huifont"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_temp = driver.find_element_by_xpath('//td[@class="huifont"]').text
    total_page = re.findall("\/(\d+)", total_temp)[0]

    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//td[@valign="top" and @class="" and @height="859"]|//table[@width="980" and @height]')
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

    div = soup.find('td', height='859')

    return div


data = [

    ["gcjs_zhaobiao_xefb_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jcjs/021004/021004001/?Paging=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':"限额发包"}), f2],
    ["gcjs_biangeng_xefb_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jcjs/021004/021004003/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':"限额发包"}), f2],
    ["gcjs_zhongbiao_xefb_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jcjs/021004/021004002/?Paging=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':"限额发包"}), f2],

    ["gcjs_kaibiao_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jcjs/021001/021001005/?Paging=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_kaibiao_jiaotong_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jcjs/021002/021002004/?Paging=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':"交通"}), f2],
    ["gcjs_kaibiao_shuili_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jcjs/021003/021003004/?Paging=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':"水利"}), f2],




    ["gcjs_zhaobiao_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jcjs/021001/021001001/?Paging=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhaobiao_jiaotong_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jcjs/021002/021002001/?Paging=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':"交通"}), f2],
    ["gcjs_zhaobiao_shuili_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jcjs/021003/021003001/?Paging=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':"水利"}), f2],

    ["gcjs_zhongbiaohx_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jcjs/021001/021001002/?Paging=2",  # unormal  21  page2
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_1_jiaotong_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jcjs/021002/021002002/?Paging=2",  # id
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':"交通"}), f2],
    ["gcjs_zhongbiaohx_shuili_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jcjs/021003/021003002/?Paging=2",  # id
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':"水利"}), f2],

    ["gcjs_biangeng_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jcjs/021001/021001003/?Paging=2",  # unormal  21  page2
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_biangeng_jiaotong_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jcjs/021002/021002003/?Paging=2",  # id
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':"交通"}), f2],
    ["gcjs_biangeng_shuili_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jcjs/021003/021003003/?Paging=2",  # id
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':"水利"}), f2],

    ["gcjs_zhongbiao_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jcjs/021001/021001004/?Paging=2",  # unormal  21  page2
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_2_jiaotong_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jcjs/021002/021002005/?Paging=2",  # id
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':"交通"}), f2],
    ["gcjs_zhongbiao_shuili_gg",
     "http://ggzy.huzhou.gov.cn/HZfront/jcjs/021003/021003005/?Paging=2",  # id
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':"水利"}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="浙江省湖州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "zhejiang_huzhou"]
    work(conp,num=3,headless=False)
    # driver = webdriver.Chrome()
    # driver.get("http://ggzy.huzhou.gov.cn/HZfront/MoreinfoHZ/MoreInfoSerachHZ.aspx?Paging=5&categorynum=021003002&TypeValue=")
    # f1(driver, 2)
    # driver.get("http://ggzy.huzhou.gov.cn/HZfront/jcjs/021003/021003002/?Paging=2")
    # f1(driver, 3)
    # driver.get("http://ggzy.huzhou.gov.cn/HZfront/jcjs/021003/021003002/?Paging=2")
    # f1(driver, 10)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver,
    #          'http://ggzy.huzhou.gov.cn/HZfront/InfoDetail/?InfoID=d355d561-2fcc-40f1-a133-cc8e3a332f66&CategoryNum=021003002'))
    # driver.close()
