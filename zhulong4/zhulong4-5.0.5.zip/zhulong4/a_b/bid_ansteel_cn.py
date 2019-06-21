import math
import random
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

_name_ = 'bid_ansteel_cn'


def f1(driver, num):
    # time.sleep(random.randint(50,60))

    locator = (By.XPATH, '//div[@class="cheenz"]/ul/li')
    WebDriverWait(driver, 40).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath('//div[@class="cheenz"]/ul/li/a').get_attribute("href")[-20:]
    cnum_temp = driver.find_element_by_xpath('//div[@class="fenye"]/span[1]').text
    cnum = re.findall('(\d+)\/',cnum_temp)[0]
    if int(cnum) != int(num):
        url = re.sub('page=\d+','page='+str(num),driver.current_url)
        # print(url)
        driver.get(url)
        locator = (By.XPATH, '//div[@class="cheenz"]/ul/li/a[not(contains(@href,"%s"))]' % val)
    WebDriverWait(driver, 40).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="cheenz"]/ul/li')
    for content in content_list:
        name = re.sub('\s+','',content.xpath('./a/text()')[0].strip())
        url = "http://bid.ansteel.cn" + content.xpath('./a/@href')[0].strip()
        ggstart_time =  content.xpath("./span/text()")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print('temp', temp)
    df = pd.DataFrame(data=data)
    df["info"] = None

    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="fenye"]/span[1]')
    WebDriverWait(driver, 50).until(EC.presence_of_element_located(locator))
    total_temp = driver.find_element_by_xpath('//div[@class="fenye"]/span[1]').text
    total_page = re.findall('\/(\d+)',total_temp)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    time.sleep(0.1)
    locator = (By.XPATH, '//div[@class="pmen"]')
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

    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_='pmen')
    return div


data = [
    ["qy_zhaobiao_benbu_gg",
     "http://bid.ansteel.cn/forepage/skin4/ywlist.aspx?pagesize=15&cmptype=%E6%8B%9B%E6%A0%87&ywtype=2&zbgs=%E9%9E%8D%E9%92%A2&page=1",
     ["name", "ggstart_time", "href","info"], add_info(f1,{'Tag':'鞍山本部'}), f2],
    ["qy_zgys_benbu_gg",
     "http://bid.ansteel.cn/ForePage/Skin4/YWList.aspx?cmptype=%E8%B5%84%E6%A0%BC%E9%A2%84%E5%AE%A1&ywtype=2&zbgs=%E9%9E%8D%E9%92%A2&page=1",
     ["name", "ggstart_time", "href","info"], add_info(f1,{'Tag':'鞍山本部'}),f2],

    ["qy_biangeng_benbu_gg",
     "http://bid.ansteel.cn/ForePage/Skin4/YWList.aspx?cmptype=%E5%8F%98%E6%9B%B4%E5%85%AC%E5%91%8A&ywtype=2&zbgs=%E9%9E%8D%E9%92%A2&page=1",
     ["name", "ggstart_time", "href","info"], add_info(f1,{'Tag':'鞍山本部'}), f2],


    ["qy_zhaobiao_chengdu_gg",
     "http://bid.ansteel.cn/ForePage/Skin4/YWList.aspx?cmptype=%E6%8B%9B%E6%A0%87&ywtype=2&zbgs=%E6%88%90%E9%83%BD&page=1",
     ["name", "ggstart_time", "href","info"], add_info(f1,{'Tag':'成都'}), f2],
    ["qy_zhongbiao_chengdu_gg",
     "http://bid.ansteel.cn/ForePage/Skin4/YWList.aspx?cmptype=%E4%B8%AD%E6%A0%87%E5%85%AC%E7%A4%BA&ywtype=2&zbgs=%E6%88%90%E9%83%BD&page=1",
     ["name", "ggstart_time", "href","info"], add_info(f1,{'Tag':'成都'}),f2],


    ["qy_zhaobiao_guoji_gg",
     "http://bid.ansteel.cn/ForePage/Skin4/YWList.aspx?cmptype=%E6%8B%9B%E6%A0%87&ywtype=2&zbgs=%E5%9B%BD%E9%99%85&page=1",
     ["name", "ggstart_time", "href","info"], add_info(f1,{'Tag':'国际'}), f2],
    ["qy_zgys_guoji_gg",
     "http://bid.ansteel.cn/ForePage/Skin4/YWList.aspx?cmptype=%E8%B5%84%E6%A0%BC%E9%A2%84%E5%AE%A1&ywtype=2&zbgs=%E9%9E%8D%E9%92%A2&page=1",
     ["name", "ggstart_time", "href","info"], add_info(f1,{'Tag':'国际'}),f2],





]


def work(conp, **args):
    est_meta(conp, data=data, diqu="鞍钢招标有限公司", **args)
    est_html(conp, f=f3, **args)

def main():

    conp = ["postgres", "since2015", "192.168.3.171", "anbang_qiye", "bid_ansteel_cn"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get('http://bid.ansteel.cn/forepage/skin4/ywlist.aspx?pagesize=15&cmptype=%E6%8B%9B%E6%A0%87&ywtype=2&zbgs=%E9%9E%8D%E9%92%A2&page=1')
    # for i in range(1,41): print(f1(driver, i))




    # driver = webdriver.Chrome()
    # driver.get("http://bid.ansteel.cn/forepage/skin4/ywlist.aspx?pagesize=15&cmptype=%E6%8B%9B%E6%A0%87&ywtype=2&zbgs=%E9%9E%8D%E9%92%A2&page=1")
    # f1(driver, 2)
    # f1(driver, 3)
    # f1(driver, 8)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://www.bidchance.com/info-zhongbiao-23488777.html'))
    # driver.close()
if __name__ == "__main__":
    main()