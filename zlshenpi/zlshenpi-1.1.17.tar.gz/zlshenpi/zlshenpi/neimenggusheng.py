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

_name_ = "neimenggusheng"

def f1(driver, num):
    locator = (By.XPATH, '//div[@class="tagContent selectTag"]//tbody/tr[1]//a')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    url=driver.current_url
    cnum=re.findall('pageNo=(\d+)',url)[0]

    if num != int(cnum):
        val = driver.find_element_by_xpath(
            '//div[@class="tagContent selectTag"]//tbody/tr[1]//a').get_attribute('href')[-30:]

        url=re.sub('(?<=pageNo=)\d+',str(num),url)

        driver.get(url)

        locator = (
            By.XPATH,
            '//div[@class="tagContent selectTag"]//tbody/tr[1]//a[not(contains(@href, "%s"))]' %
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
        href = tds[0].a['href']
        xm_code = tds[0].get_text().strip()
        name = tds[1].get_text().strip()
        shixiang=tds[2].get_text().strip()
        jieguo=tds[3].get_text().strip()
        ggstart_time='not'
        info = json.dumps({'shixiang': shixiang,
                               'jieguo': jieguo,
                               'xm_code': xm_code},
                              ensure_ascii=False)

        if 'http' in href:
            href = href
        else:
            href = 'http://nmg.tzxm.gov.cn' + href

        tmp = [name,  ggstart_time, href, info]
        # print(tmp)
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="tagContent selectTag"]//tbody/tr[1]//a')
    WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath(
        '//div[@class="fanye"]//a[last()]').get_attribute('href')
    total=re.findall('pageNo=(\d+)',total)[0]
    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="block_content"][string-length()>50]')
    WebDriverWait(
        driver, 20).until(
        EC.presence_of_all_elements_located(locator))
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
    div = soup.find('div', class_="block_content")

    return div


data = [

    ["xm_shenpi_gg",
     "http://nmg.tzxm.gov.cn/tzsp/projectHandlePublicity.jspx?projectname=&pageNo=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data, interval_page=1000,num=20,diqu="内蒙古省",pageLoadStrategy='none',pageloadtimeout=80, **args)
    est_html(conp, f=f3,pageloadtimeout=80, **args)


if __name__ == '__main__':
    work(
        conp=[
            "postgres",
            "since2015",
            "192.168.3.171",
            "zlshenpi",
            "neimenggusheng"],
        num=1,headless=False,pageLoadStrategy='none')

    # driver = webdriver.Chrome()
    # for d in data:
    #     driver.get(d[1])
    #     print(d[1])
    #     f1(driver,2)
