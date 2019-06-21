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

from zhulong4.util.etl import est_tbs, est_meta, est_html, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url = "http://www.fqztb.com/Home/tenderList?index=3&type=%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE"
# driver = webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)


_name_ = 'uat_ec_chng_com_cn'


def f1(driver, num):
    locator = (By.XPATH, '//ul[@class="main_r_con"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath('//span[@id="viewPageCurrent"]').text
    cnum = re.findall('当前第(\d+?)页', cnum)[0]


    if int(cnum) != num:
        val = driver.find_element_by_xpath('//ul[@class="main_r_con"]/li[1]/a').get_attribute('href')
        val = re.findall("javascript:announcementClick\('(\d+?)','101',''\)", val)[0]

        driver.execute_script("""
        (function jumpPage(pageNo) {
    	var start = 0;
    	if (pageNo > 1) {
    		start = (pageNo - 1) * pageSize;
    	}
    	$("#pageCurrent").val(pageNo);
    	$('#page-pageStart').val(start);
    	$("#pageForm").trigger("submit");
        })(%d)""" % num)

        # 第二个等待
        locator = (By.XPATH, '//ul[@class="main_r_con"]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('ul', class_='main_r_con')
    trs = div.find_all('li')
    for tr in trs:

        href = tr.a['href']
        name = tr.a['title']
        ggstart_time = tr.p.get_text()

        href = re.findall("javascript:announcementClick\('(\d+?)','101',''\)", href)[0]

        if 'http' in href:
            href = href
        else:
            href = 'http://uat.ec.chng.com.cn/ecmall/announcement/announcementDetail.do?announcementId=' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)

    df = pd.DataFrame(data=data)
    df["info"] = None

    return df


def f2(driver):

    locator = (By.XPATH, '//ul[@class="main_r_con"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//span[@id="viewPageTotal"]').text
    total = re.findall('共(\d+?)页', total)[0]

    total = int(total)

    driver.quit()

    return total


def chang_type(f,num):
    def inner(*args):
        driver=args[0]
        locator = (By.XPATH, '//ul[@class="main_r_con"]/li[1]/a')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        ctext=driver.find_element_by_xpath('(//a[@class="hover"])[last()]').text.strip()
        if ctext in ['招标公告','公开询价公告']:
            val = driver.find_element_by_xpath('//ul[@class="main_r_con"]/li[1]/a').get_attribute('href')
            val = re.findall("javascript:announcementClick\('(\d+?)','101',''\)", val)[0]

            driver.find_element_by_xpath('//div[@class="main_box_left"]//dd[%s]/a'%num).click()
            # 第二个等待
            locator = (By.XPATH, '//ul[@class="main_r_con"]/li[1]/a[not(contains(@href,"%s"))]' % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*args)
    return inner


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               '//div[@class="detail_box qst_box"][string-length()>10]')

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
        if i > 10: break

    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')

    div = soup.find('div', class_="detail_box qst_box")



    return div


data = [

    ["qy_zhaobiao_gg", "http://uat.ec.chng.com.cn/ecmall/more.do?type=103",["name", "ggstart_time", "href", "info"], f1, f2],
    ["qy_zgys_gg", "http://uat.ec.chng.com.cn/ecmall/more.do?type=103",["name", "ggstart_time", "href", "info"], chang_type(f1,2), chang_type(f2,2)],
    ["qy_zhongbiaohx_gg", "http://uat.ec.chng.com.cn/ecmall/more.do?type=103",["name", "ggstart_time", "href", "info"], chang_type(f1,3), chang_type(f2,3)],
    ["qy_zhongbiao_gg", "http://uat.ec.chng.com.cn/ecmall/more.do?type=103",["name", "ggstart_time", "href", "info"], chang_type(f1,4), chang_type(f2,4)],

    ["qy_zhaobiao_xunjia_gg", "http://uat.ec.chng.com.cn/ecmall/morelogin.do?type=107",["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':'公开询价'}), f2],
    ["qy_zhongbiao_xunjia_gg", "http://uat.ec.chng.com.cn/ecmall/morelogin.do?type=107",["name", "ggstart_time", "href", "info"], add_info(chang_type(f1,2),{'zbfs':"公开询价"}), chang_type(f2,2)],
    ["qy_zhongbiao_danyilaiyuan_gg", "http://uat.ec.chng.com.cn/ecmall/morelogin.do?type=107",["name", "ggstart_time", "href", "info"], add_info(chang_type(f1,3),{'zbfs':"单一来源"}), chang_type(f2,3)],
    ["qy_zhaobiao_tanpan_gg", "http://uat.ec.chng.com.cn/ecmall/morelogin.do?type=107",["name", "ggstart_time", "href", "info"], add_info(chang_type(f1,4),{'zbfs':"竞争性谈判"}), chang_type(f2,4)],
    ["qy_zhongbiao_tanpan_gg", "http://uat.ec.chng.com.cn/ecmall/morelogin.do?type=107",["name", "ggstart_time", "href", "info"], add_info(chang_type(f1,5),{'zbfs':"竞争性谈判"}), chang_type(f2,5)],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="中国华能", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch3", "uat_ec_chng_com_cn"])
    pass