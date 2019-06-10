import time

import pandas as pd
import re
from datetime import datetime,timedelta
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

_name_ = 'fujian_fuzhou'


def f1(driver, num):
    locator = (By.XPATH, '(//table[@id="articleList"]//tr)[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = int(driver.find_element_by_xpath('//li[@class="page-number active"]/a').text)

    while num != cnum:
        cnum = int(driver.find_element_by_xpath('//li[@class="page-number active"]/a').text)
        val = driver.find_element_by_xpath('(//table[@id="articleList"]//tr)[2]//a').get_attribute('href')[-30:]
        if num > cnum:
            if num-cnum > total_page//2:
                ele=driver.find_element_by_xpath('//li[@class="page-last"]/a')
                driver.execute_script('arguments[0].click()', ele)
            else:
                ele=driver.find_element_by_xpath('//li[@class="page-next"]/a')
                driver.execute_script('arguments[0].click()', ele)
        elif cnum > num:
            if cnum - num > total_page//2:
                ele=driver.find_element_by_xpath('//li[@class="page-first"]/a')
                driver.execute_script('arguments[0].click()', ele)
            else:
                ele=driver.find_element_by_xpath('//li[@class="page-pre"]/a')
                driver.execute_script('arguments[0].click()', ele)
        else:
            break
        locator = (By.XPATH, '(//table[@id="articleList"]//tr)[2]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []
    html = driver.page_source

    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find('table', id="articleList").find_all('tr')[1:]

    for tr in trs:
        tds = tr.find_all('td')
        index_num = tds[1].get_text()
        href = tds[2].a['href']
        name = tds[2].a.get_text()
        ggstart_time = tds[3].get_text().strip()

        today_ = datetime.strftime(datetime.now(), '%Y-%m-%d')
        yesterday_ = datetime.strftime(datetime.now() - timedelta(days=1), '%Y-%m-%d')
        date_dict = {'今天': today_, '昨天': yesterday_}
        ggstart_time = date_dict.get(ggstart_time, ggstart_time)

        if 'http' in href:
            href = href
        else:
            href = 'http://www.fzztb.com' + href

        info={'index_num':index_num}
        info=json.dumps(info,ensure_ascii=False)
        tmp = [name, ggstart_time, href,info]

        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    global total_page
    locator = (By.XPATH, '(//table[@id="articleList"]//tr)[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath('//li[@class="page-last"]/a').text
    total = int(total)
    total_page=total
    driver.quit()

    return total


def chang_type(f,num):
    def inner(*args):
        driver=args[0]
        locator = (By.XPATH, '(//table[@id="articleList"]//tr)[2]//a')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        ctext=driver.find_element_by_xpath('//ul[@id="project-list"]/li[@class="active"]/a').text.strip()
        if '抽取代理' in ctext:
            val = driver.find_element_by_xpath('(//table[@id="articleList"]//tr)[2]//a').get_attribute('href')[-30:]

            ele=driver.find_element_by_xpath('//ul[@id="project-list"]/li[%s]/a' % num)
            driver.execute_script('arguments[0].click()', ele)
            locator = (By.XPATH, '(//table[@id="articleList"]//tr)[2]//a[not(contains(@href,"{}"))]'.format(val))
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        return f(*args)
    return inner


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               '//div[@id="detail"]/iframe')

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    driver.switch_to.frame('contentIframe')

    locator=(By.XPATH,"//body[string-length()>10]")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

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

    div = soup.find('body')
    driver.switch_to.parent_frame()
    return div


data = [

["gcjs_yucai_gg", "http://www.fzztb.com/CmsPortalWeb/main/project.xhtml",["name", "ggstart_time", "href", "info"], chang_type(f1,2), chang_type(f2,2)],
["gcjs_zhaobiao_gg", "http://www.fzztb.com/CmsPortalWeb/main/project.xhtml",["name", "ggstart_time", "href", "info"], chang_type(f1,4), chang_type(f2,4)],
["gcjs_gqita_da_bian_gg", "http://www.fzztb.com/CmsPortalWeb/main/project.xhtml",["name", "ggstart_time", "href", "info"], chang_type(f1,5), chang_type(f2,5)],
["gcjs_zhongbiaohx_gg", "http://www.fzztb.com/CmsPortalWeb/main/project.xhtml",["name", "ggstart_time", "href", "info"], chang_type(f1,7), chang_type(f2,7)],
["gcjs_zhongbiao_gg", "http://www.fzztb.com/CmsPortalWeb/main/project.xhtml",["name", "ggstart_time", "href", "info"], chang_type(f1,8), chang_type(f2,8)],
["gcjs_liubiao_gg", "http://www.fzztb.com/CmsPortalWeb/main/project.xhtml",["name", "ggstart_time", "href", "info"], chang_type(f1,9), chang_type(f2,9)],
["gcjs_gqita_kaibiao_gg", "http://www.fzztb.com/CmsPortalWeb/main/project.xhtml",["name", "ggstart_time", "href", "info"], add_info(chang_type(f1,6),{"gclx":"开标记录"}), chang_type(f2,6)],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="福建省福州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch2", "fujian_fuzhou"],headless=True,num=1,pageloadtimeout=80)
