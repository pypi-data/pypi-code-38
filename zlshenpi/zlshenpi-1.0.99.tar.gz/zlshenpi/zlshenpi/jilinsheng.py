import math

import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zlshenpi.util.etl import add_info, est_meta, est_html, est_tbs, add_info, est_meta_large
import sys
import time
import json

_name_ = "jilinsheng"



def f1(driver, num):
    locator = (By.XPATH, '//div[@class="tagContent selectTag"]//tbody/tr[1]/td[1]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    url=driver.current_url
    cnum=re.findall('pageNo=(\d+)&',url)[0]

    if num != int(cnum):
        val = driver.find_element_by_xpath(
            '//div[@class="tagContent selectTag"]//tbody/tr[1]/td[1]').text

        url=re.sub('(?<=pageNo=)\d+',str(num),url)

        driver.get(url)

        locator = (
            By.XPATH,
            '//div[@class="tagContent selectTag"]//tbody/tr[1]/td[1][not(contains(string(), "%s"))]' %
            val)
        WebDriverWait(
            driver, 20).until(
            EC.presence_of_element_located(locator))
    data=[]
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    cons = soup.find(
        'div',class_='tagContent selectTag').find('tbody').find_all('tr')

    for con in cons:
        tds = con.find_all('td')
        xm_code = tds[0].get_text().strip()
        name = tds[1].get_text().strip()
        dw=tds[2].get_text().strip()
        jieguo=tds[3].get_text().strip()
        jieguo=re.sub('[\n\t ]','',jieguo)
        ggstart_time='not'
        href = tds[1].find('a')
        if href:
            href = href['onclick']
            cbsnum=re.findall("qkRecord\('(.+?)',",href)[0]
            recordnum=re.findall(",'(.+?)'\)",href)[0]
            href='http://tzxm.jl.gov.cn:8888/reqviewpdf.jspx?file=registrationform%2Fpreview.jspx%3Fcbsnum%3D{}%26recordnum%3D{}'.format(cbsnum,recordnum)
            info = json.dumps({'dw': dw,
                               'jieguo': jieguo,
                               'xm_code': xm_code,
                               },
                              ensure_ascii=False)

        else:
            href='not'
            info = json.dumps({'dw': dw,
                               'jieguo': jieguo,
                               'xm_code': xm_code,
                               "hreftype": "不可抓网页",},
                              ensure_ascii=False)


        tmp = [name,  ggstart_time, href, info]
        # print(tmp)
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="tagContent selectTag"]//tbody/tr[1]/td[1]')
    WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath(
        '//div[@class="fanye"]//a[last()]').get_attribute('href')
    total=re.findall('pageNo=(\d+)',total)[0]
    driver.quit()
    return int(total)

def f4(driver, num):
    locator = (By.XPATH, '//table[@class="index-table"]//tr[2]/td[1]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    cnum=driver.find_element_by_xpath('//a[@class="cur"]').text

    if num != int(cnum):
        val = driver.find_element_by_xpath(
            '//table[@class="index-table"]//tr[2]/td[1]').get_attribute('title')[-20:]

        driver.execute_script('$("#pageNo").val(%d);$("#publicInformationForm").submit();' % num)

        locator = (
            By.XPATH,
            '//table[@class="index-table"]//tr[2]/td[1][not(contains(@title, "%s"))]' %val)

        WebDriverWait(
            driver, 20).until(
            EC.presence_of_element_located(locator))
    data=[]
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    cons = soup.find(
        'table',class_='index-table').find('tbody').find_all('tr')[1:]

    for con in cons:
        tds = con.find_all('td')
        name = tds[0].get_text().strip()
        xm_code=re.findall('[\d-]+',name)[-1]

        shixiang=tds[1]['title'].strip()
        dw=tds[2].get_text().strip()
        jieguo=tds[3].get_text().strip()
        ggstart_time='not'
        href = tds[0].find('a')

        if href:
            href = href['onclick']

            info = json.dumps({'dw': dw,
                               'jieguo': jieguo,
                               'shixiang':shixiang,
                               'xm_code': xm_code,
                               },
                              ensure_ascii=False)

        else:
            href='not'
            info = json.dumps({'dw': dw,
                               'jieguo': jieguo,
                               'xm_code': xm_code,
                               'shixiang': shixiang,
                               "hreftype": "不可抓网页",},
                              ensure_ascii=False)


        tmp = [name,  ggstart_time, href, info]
        # print(tmp)
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f5(driver):
    locator = (By.XPATH, '//table[@class="index-table"]//tr[2]/td[1]')
    WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath(
        '//div[@class="pageNum"]/span[1]/strong').text

    driver.quit()
    return int(total)


def f3(driver, url):
    if 'queryDetailed' in url:

        driver.get('http://tzxm.jl.gov.cn/portalopenPublicInformation.do?method=queryExamineAll')
        locator = (By.XPATH, '//table[@class="index-table"]//tr[2]/td[1]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        driver.execute_script(url)
        locator = (By.XPATH, '//div[@class="layui-layer-content"][string-length()>50]')
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))

    else:
        driver.get(url)

        locator = (By.XPATH, '//div[@id="viewerContainer"][string-length()>50]')
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
        if i > 5:
            break
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_="layui-layer-content")
    if div == None:
        div=soup.find('div',id='viewerContainer')

    time.sleep(10)
    return div




data = [
    ["xm_shenpi_old_gg",
     "http://tzxm.jl.gov.cn:8888/tzsp/projectHandlePublicity.jspx?pageNo=1&&projectname=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["xm_shenpi_gg",
     "http://tzxm.jl.gov.cn/portalopenPublicInformation.do?method=queryExamineAll",
     ["name", "ggstart_time", "href", "info"], f4, f5],

]


def work(conp, **args):
    est_meta_large(conp, data=data,interval_page=1000,num=20, diqu="吉林省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlshenpi", "jilinsheng"],num=1,headless=False,total=2)
    # driver = webdriver.Chrome()
    # for d in data:
    #     driver.get(d[1])
    #     print(d[1])
    #     f1(driver,2)
