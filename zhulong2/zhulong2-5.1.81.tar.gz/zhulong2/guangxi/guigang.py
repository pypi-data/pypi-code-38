import random

import pandas as pd
import re

import requests
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from zhulong2.util.etl import est_html, est_meta, add_info

_name_ = "guangxi_guigang"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='list-container']/ul/li[1]/a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//li[@class='paginationjs-page J-paginationjs-page active']/a")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(st)
    except:
        cnum = 1

    if num != cnum:
        val = driver.find_element_by_xpath("//div[@class='list-container']/ul/li[1]/a").get_attribute('href')[-30:]
        driver.find_element_by_xpath("//input[@class='J-paginationjs-go-pagenumber']").clear()
        driver.find_element_by_xpath("//input[@class='J-paginationjs-go-pagenumber']").send_keys(num, Keys.ENTER)
        locator = (By.XPATH, "//div[@class='list-container']/ul/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("div", class_='list-container')
    lis = div.find_all('li', class_='list-item')
    data = []
    for tr in lis:
        info = {}
        a = tr.find('a')

        if tr.find('span', class_='district'):
            span1 = tr.find('span', class_='district').extract().text.strip()
            if re.findall(r'\[(.*)\]', span1):
                span2 = re.findall(r'\[(.*)\]', span1)[0]
                if '·' in span2:
                    diqu1 = span2.split('·')[0]
                    lx = span2.split('·')[1]
                    info['diqu1'] = diqu1
                    info['lx'] = lx
                else:
                    info['diqu1'] = span2
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        td = tr.find('span', class_="date").text.strip()
        link = 'http://zfcg.czj.gxgg.gov.cn' + a['href'].strip()
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:
            info = None
        tmp = [title, td, link, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='list-container']/ul/li[1]/a")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//li[@class='paginationjs-page paginationjs-last J-paginationjs-page']/a")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = int(st)
    except:
        num = 1
    driver.quit()
    return num


def f3(driver, url):
    driver.get(url)
    if '<iframe id="iframe' in driver.page_source:
        driver.switch_to_frame('iframe')
    locator = (By.XPATH,
               "//body[@class='view'][string-length()>10] | //div[@class='artcl_m'][string-length()>10] | //div[@class='right_con'][string-length()>10]")
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
    div = soup.find('body', class_='view')
    if div == None:
        div = soup.find('div', class_='artcl_m')
        if div == None:
            div = soup.find('div', class_='right_con')
    return div


data = [
    ["zfcg_zhaobiao_shiji_gg",
     "http://zfcg.czj.gxgg.gov.cn/ZcyAnnouncement/ZcyAnnouncement2/index.html?districtCode=450899",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],
    # # # # #
    ["zfcg_yucai_shiji_gg",
     "http://zfcg.czj.gxgg.gov.cn/ZcyAnnouncement/ZcyAnnouncement1/index.html?districtCode=450899",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],
    # # #
    ["zfcg_zhongbiao_shiji_gg",
     "http://zfcg.czj.gxgg.gov.cn/ZcyAnnouncement/ZcyAnnouncement4/ZcyAnnouncement3004/index.html?districtCode=450899",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],
    #
    ["zfcg_biangeng_shiji_gg",
     "http://zfcg.czj.gxgg.gov.cn/ZcyAnnouncement/ZcyAnnouncement3/index.html?districtCode=450899",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],
    # # ###
    ["zfcg_zhaobiao_dyly_shiji_gg",
     "http://zfcg.czj.gxgg.gov.cn/ZcyAnnouncement/singeOrignNoticeParent/index.html?districtCode=450899",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级', 'zbfs': '单一来源'}), f2],
    # # # # #
    ["zfcg_zhaobiao_xianqu_gg",
     "http://zfcg.czj.gxgg.gov.cn/ZcyAnnouncement/ZcyAnnouncement2/index.html?districtCode=450802%2C450803%2C450804%2C450821%2C450881",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县区'}), f2],
    # #
    ["zfcg_yucai_xianqu_gg",
     "http://zfcg.czj.gxgg.gov.cn/ZcyAnnouncement/ZcyAnnouncement1/index.html?districtCode=450802%2C450803%2C450804%2C450821%2C450881",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县区'}), f2],
    # # # #
    ["zfcg_zhongbiao_xianqu_gg",
     "http://zfcg.czj.gxgg.gov.cn/ZcyAnnouncement/ZcyAnnouncement4/ZcyAnnouncement3004/index.html?districtCode=450802%2C450803%2C450804%2C450821%2C450881",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县区'}), f2],
    # # # #
    ["zfcg_biangeng_xianqu_gg",
     "http://zfcg.czj.gxgg.gov.cn/ZcyAnnouncement/ZcyAnnouncement3/index.html?districtCode=450802%2C450803%2C450804%2C450821%2C450881",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县区'}), f2],

    ["zfcg_zhaobiao_dyly_xianqu_gg",
     "http://zfcg.czj.gxgg.gov.cn/ZcyAnnouncement/singeOrignNoticeParent/index.html?districtCode=450802%2C450803%2C450804%2C450821%2C450881",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '县区', 'zbfs': '单一来源'}), f2],
    # # # #

    ["zfcg_liubiao_gg",
     "http://zfcg.czj.gxgg.gov.cn/ZcyAnnouncement/ZcyAnnouncement4/ZcyAnnouncement3007/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zgysjg_yq_gg",
     "http://zfcg.czj.gxgg.gov.cn/ZcyAnnouncement/ZcyAnnouncement4/ZcyAnnouncement3009/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '邀请招标'}), f2],

    ["zfcg_zhongzhi_gg",
     "http://zfcg.czj.gxgg.gov.cn/ZcyAnnouncement/ZcyAnnouncement4/ZcyAnnouncement3015/index.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_jieguobiangeng_gg",
     "http://zfcg.czj.gxgg.gov.cn/ZcyAnnouncement/ZcyAnnouncement4/ZcyAnnouncement3017/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '采购结果变更公告'}), f2],

    ["zfcg_zgysjg_gk_gg",
     "http://zfcg.czj.gxgg.gov.cn/ZcyAnnouncement/ZcyAnnouncement4/ZcyAnnouncement3009/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '公开招标'}), f2],

    ["zfcg_gqita_caigoujieguo_gg",
     "http://zfcg.czj.gxgg.gov.cn/ZcyAnnouncement/ZcyAnnouncement4/ZcyAnnouncement4007/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '其他采购结果公告'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广西省贵港市", **args)
    est_html(conp, f=f3, **args)


# 网址变更
# 需要在Windows上跑
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "guigang"], pageloadtimeout=120)
    #
    # driver=webdriver.Chrome()
    # url = "http://zfcg.czj.gxgg.gov.cn/ZcyAnnouncement/singeOrignNoticeParent/index.html?districtCode=450802%2C450803%2C450804%2C450821%2C450881"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    # driver=webdriver.Chrome()
    # url = "http://zfcg.czj.gxgg.gov.cn/ZcyAnnouncement/singeOrignNoticeParent/index.html?districtCode=450802%2C450803%2C450804%2C450821%2C450881"
    # driver.get(url)
    # for i in range(2, 5):
    #     df=f1(driver, i)
    #     print(df.values)
    #     for d in df[2].values:
    #         f =f3(driver, d)
    #         print(f)
