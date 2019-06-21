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

_name_ = 'bid_powerchina_cn'


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="ul_div"]/ul/li[1]/a|//ul[@id="bulletinList"]/li[1]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    try:
        val = driver.find_element_by_xpath('//div[@class="ul_div"]/ul/li[1]/a | //ul[@class="newslist"]/li[1]/a').get_attribute("href")[-50:]
    except:
        val = driver.find_element_by_xpath('//ul[@id="bulletinList"]/li[1]/input').get_attribute("value")[-50:]
    cnum_temp = driver.find_element_by_xpath('//table[@class="pageBur"]/tbody/tr/td/span|//div[@class="pages"]/label').text
    cnum = re.findall(r'(\d+)\/', cnum_temp)[0]
    if int(cnum) != int(num):
        if 'page' not in driver.current_url:
            driver.execute_script('jump(%s);' % num)
            locator = (By.XPATH, '''//div[@class="ul_div"]/ul/li[1]/a[not(contains(@href,"%s"))]''' % val)
        else:
            url = re.sub('page=\d+','page='+str(num),driver.current_url)
            driver.get(url)
            locator = (By.XPATH, '''//ul[@id="bulletinList"]/li[1]/a[not(contains(@href,"%s"))]''' % val)


    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@class="ul_div"]/ul/li|//ul[@id="bulletinList"]/li')
    for content in content_list:
        name = content.xpath("./a/@title|./a/text()")[0].strip()
        if 'page' not in driver.current_url:
            url = "http://bid.powerchina.cn" + content.xpath("./a/@href")[0].strip()
        else:
            try:
                url = 'http:' + content.xpath("./input/@value")[0].strip()
            except:
                url = 'http:' + content.xpath("./a/@href")[0].strip()

        ggstart_time = content.xpath("./a/div/div/text()|./span/text()")[0].strip().strip('[').strip(']')
        temp = [name, ggstart_time, url]
        data.append(temp)

    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):

    driver.maximize_window()
    locator = (By.XPATH, '//table[@class="pageBur"]/tbody/tr/td/span|//div[@class="pages"]/label')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_temp = driver.find_element_by_xpath('//table[@class="pageBur"]/tbody/tr/td/span|//div[@class="pages"]/label').text
    total_page = re.findall(r'\/(\d+)', total_temp)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@style="height: auto; border: 2px solid #9AC5F2; width: 1034px;"]|//div[@class="mainBorder"]')
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
    div = soup.find('div', style='height: auto; border: 2px solid #9AC5F2; width: 1034px;')
    if not div:
        div = soup.find('div', class_='mainBorder')
    return div


data = [
    ["qy_zhaobiao_gg",
     "http://bid.powerchina.cn/announcement/getGengDuo?typeed=4&type=0&menu=login",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_biangeng_gg",
     "http://bid.powerchina.cn/announcement/getGengDuo?typeed=5&type=11&menu=login",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_zhongbiaohx_gg",
     "http://bid.powerchina.cn/announcement/getGengDuo?typeed=70&type=0&menu=login",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_zhongbiao_gg",
     "http://bid.powerchina.cn/announcement/getGengDuo?typeed=6&type=0&menu=login",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["qy_zhaobiao_sb_gg",
     "http://ec3.powerchina.cn/zgdjcms//category/bulletinList.html?categoryId=2&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'设备'}), f2],
    ["qy_dayi_sb_gg",
     "http://ec3.powerchina.cn/zgdjcms//category/bulletinList.html?dates=300&categoryId=6&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'设备'}), f2],
    ["qy_zhongbiao_sb_gg",
     "http://ec3.powerchina.cn/zgdjcms//category/bulletinList.html?dates=300&categoryId=4&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'设备'}), f2],
    ["qy_liubiao_sb_gg",
     "http://ec3.powerchina.cn/zgdjcms//category/bulletinList.html?dates=300&categoryId=5&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'设备'}), f2],
    ["qy_biangeng_sb_gg",
     "http://ec3.powerchina.cn/zgdjcms//category/bulletinList.html?dates=300&categoryId=3&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'Tag':'设备'}), f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="中国电力建设集团有限公司", **args)
    est_html(conp, f=f3, **args)

def main():

    conp = ["postgres", "since2015", "192.168.3.171", "anbang_qiye", "bid_powerchina_cn"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://bid.powerchina.cn/announcement/getGengDuo?typeed=4&type=0&menu=login")
    # f1(driver, 2)
    # f1(driver, 3)
    # f1(driver, 10)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # driver.get("http://bid.powerchina.cn/announcement/getGengDuo?typeed=6&type=0&menu=login")
    # f1(driver, 2)
    # f1(driver, 3)
    # f1(driver, 10)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # driver.get("http://bid.powerchina.cn/announcement/getGengDuo?typeed=5&type=11&menu=login")
    # f1(driver, 2)
    # f1(driver, 3)
    # f1(driver, 10)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://bid.powerchina.cn/announcement/getAnnouncementDetails.html?id=1812118840'))
    # driver.close()
if __name__ == "__main__":
    main()