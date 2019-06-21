import time

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json

from zhulong3.util.etl import est_tbs, est_meta, est_html, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url = "http://www.fzztb.com/CmsPortalWeb/main/project.xhtml"
# driver = webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_ = 'guangdong_shenzhen'


def f1(driver, num):
    locator = (By.XPATH, '//tr[@class="firt"][2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath('//a[@class="a1"]').text
    cnum = re.findall('第(\d+)页', cnum)[0]

    if cnum != str(num):
        val = driver.find_element_by_xpath('//tr[@class="firt"][2]//a').get_attribute('href')[-30:]

        driver.execute_script("reloadscript(%s);" % num)
        locator = (By.XPATH, '//tr[@class="firt"][2]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find_all('tr', class_="firt")[1:]

    for tr in trs:
        tds = tr.find_all('td')
        index_num = tds[0].get_text()
        href = tds[1].a['href']
        name = tds[1].a['title']
        if len(tds)==5:
            gg_type = tds[3].get_text()
            ggstart_time = tds[4].get_text()
            info = {'index_num': index_num, "gg_type": gg_type}
        elif len(tds)==4:
            gg_type = tds[2].get_text()
            ggstart_time = tds[3].get_text()
            info = {'index_num': index_num,"gg_type":gg_type}
        else:
            ggstart_time=tds[2].get_text()
            info = {'index_num': index_num}



        info=json.dumps(info,ensure_ascii=False)
        tmp = [name, ggstart_time,href,info]

        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df

def f4(driver,num):
    locator = (By.XPATH, '//tr[@class="firt"][2]/td[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath('//a[@class="a1"]').text
    cnum = re.findall('第(\d+)页', cnum)
    if cnum:
        cnum=cnum[0]
    else:
        cnum=1

    if str(cnum) != str(num):
        val = driver.find_element_by_xpath('//tr[@class="firt"][2]/td[1]').text

        driver.execute_script("reloadscript(%s);" % num)
        locator = (By.XPATH, '//tr[@class="firt"][2]/td[1][text() != %s]'%val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find_all('tr', class_="firt")[1:]

    for tr in trs:
        tds = tr.find_all('td')
        index_num = tds[0].get_text()
        href = 'no href'
        name = tds[1]['title']
        if len(tds) == 5:
            huiyi_type = tds[2].get_text()
            huiyi_ad = tds[3].get_text()
            ggstart_time = tds[4].get_text()
            info = {'index_num': index_num, "huiyi_type": huiyi_type,'huiyi_add':huiyi_ad,'hreftype':'不可抓网页'}
        else :
            gg_type = tds[2].get_text()
            ggstart_time = tds[3].get_text()
            info = {'index_num': index_num, "gg_type": gg_type,'hreftype':'不可抓网页'}

        info = json.dumps(info, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]

        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df

def f2(driver):
    url=driver.current_url
    if ('jbxx.html' in url) or ('hyxx.html' in url):
        locator = (By.XPATH, '//tr[@class="firt"][2]/td[1]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    else:
        locator = (By.XPATH, '//tr[@class="firt"][2]//a')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//a[@class="a1"]').text
    total = re.findall("共(\d+?)页", total)[0]
    total = int(total)
    driver.quit()

    return total

def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               '//div[@class="detail_contect"]')

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    time.sleep(0.1)
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

    div = soup.find('div', class_="detail_contect")

    return div



data = [

    ["gcjs_zhaobiao_gg", "http://zjj.sz.gov.cn/jsjy/jyxx/zbgg/",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_biangeng_gg", "http://zjj.sz.gov.cn/jsjy/jyxx/bggs/",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_kongzhijia_gg", "http://zjj.sz.gov.cn/jsjy/jyxx/zbkzjgs/",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zgysjg_gg", "http://zjj.sz.gov.cn/jsjy/jyxx/zsyjgs/",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg", "http://zjj.sz.gov.cn/jsjy/jyxx/zbgs/",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://zjj.sz.gov.cn/jsjy/jyxx/dbjggs/",["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_kaibiao_gg", "http://zjj.sz.gov.cn/jsjy/jyxx/kbqkgs/",["name", "ggstart_time", "href", "info"], add_info(f1,{'ggtype':'开标记录'}), f2],
    ["gcjs_gqita_pingbiaowyh_gg", "http://zjj.sz.gov.cn/jsjy/jyxx/pbwyhcymdgs/",["name", "ggstart_time", "href", "info"], add_info(f1,{'ggtype':'评标委员会公示'}), f2],
    ["gcjs_gqita_pingbiaobg_gg", "http://zjj.sz.gov.cn/jsjy/jyxx/pbbggs/",["name", "ggstart_time", "href", "info"], add_info(f1,{'ggtype':'评标报告'}), f2],

    ##另一个网站,但是结构相同
    ["gcjs_gqita_zhijiefabao_gg", "https://www.szjsjy.com.cn:8001/jyw/pub/jsgc/jyxx/gd/zxzbsbsqzjfbgs.html",["name", "ggstart_time", "href", "info"], add_info(f1,{'ggtype':'重新招标失败申请直接发包'}), f2],
    ["gcjs_gqita_xieyi_gg", "https://www.szjsjy.com.cn:8001/jyw/pub/jsgc/jyxx/gd/yxyfsxpwyfwqyxxgs.html",["name", "ggstart_time", "href", "info"], add_info(f1,{'ggtype':'协议选聘'}), f2],
    ["gcjs_gqita_jiebiao_gg", "https://www.szjsjy.com.cn:8001/jyw/pub/jsgc/jyxx/gd/jbxx.html",["name", "ggstart_time", "href", "info"], add_info(f4,{'ggtype':'截标信息'}), f2],
    ["gcjs_gqita_huiyi_gg", "https://www.szjsjy.com.cn:8001/jyw/pub/jsgc/jyxx/gd/hyxx.html",["name", "ggstart_time", "href", "info"], add_info(f4,{'ggtype':'会议信息'}), f2],


]

def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省深圳市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch2", "guangdong_shenzhen"])

