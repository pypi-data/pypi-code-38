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

_name_ = "hebeisheng"


def f1(driver, num):
    locator = (By.XPATH, '//table[@class="tbstyle1"]/tbody/tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum = driver.find_element_by_xpath('//li[@class="active"]/a').text

    if num != int(cnum):
        val = driver.find_element_by_xpath('//table[@class="tbstyle1"]/tbody/tr[1]//a').get_attribute(
            'href')[-30:-3]

        driver.execute_script("javascript:page(%s);"%num)

        locator = (
        By.XPATH, '//table[@class="tbstyle1"]/tbody/tr[1]//a[not(contains(@href, "%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data=[]
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    cons = soup.find('table', class_='tbstyle1').find('tbody').find_all('tr')
    for con in cons:
        tds = con.find_all('td')
        href = con.find('a')['href']


        if 'ppp' in url:
            name = con.find('a').get_text()
            xm_code = tds[1].get_text().strip()
            hangye = tds[3].get_text().strip()
            jine = tds[4].get_text().strip()
            ggstart_time = tds[5].get_text()
            info = json.dumps({'hangye': hangye, 'jine': jine,  'xm_code': xm_code},
                              ensure_ascii=False)
            "javascript:showTjxx('2017-130181-83-01-000285');"
            xmdm = re.findall("\('(.+?)'", href)[0]
            href='http://tzxm.hbzwfw.gov.cn/sbglweb/xmShowList?xmdm=%s'%xmdm
        else:
            name = tds[1]['title']
            xm_code = tds[0]['title']
            bumen = tds[3]['title']
            shixiang = tds[2]['title']
            jieguo = tds[4].get_text().strip()
            ggstart_time = tds[5].get_text().strip()
            info = json.dumps({'bumen': bumen, 'shixiang': shixiang,'jieguo':jieguo, 'xm_code': xm_code},
                              ensure_ascii=False)
            xmdm=re.findall("\('(.+?)',",href)[0]
            sxid=re.findall(",'(.+?)'\)",href)[0]

            href = 'http://tzxm.hbzwfw.gov.cn/sbglweb/xminfo?xmdm=%s&sxid=%s&xzqh=130000'%(xmdm,sxid)

        tmp = [name,  ggstart_time, href, info]
        # print(tmp)
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):
    locator = (By.XPATH, '//table[@class="tbstyle1"]/tbody/tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath('//div[@class="pagewrap"]/div/div[1]/strong').text.strip()
    count=driver.find_element_by_xpath('//div[@class="pagewrap"]//select/option[@selected]').get_attribute('value')
    total=math.ceil(int(total)/int(count))
    driver.quit()
    return int(total)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//body[string-length()>100]')
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
    div = soup.find('body')
    if '已经过了有效期失效不能访问' in page:
        raise ValueError('ip失效')
    return div


data = [
    ["xm_shenpi_ppp_gg",
     "http://tzxm.hbzwfw.gov.cn/sbglweb/pppXxjcfwList?xzqh=130000",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'PPP项目'}), f2],

    ["xm_shenpi_gg",
     "http://tzxm.hbzwfw.gov.cn/sbglweb/gsxxList?xzqh=130000",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data,interval_page=1000,num=20, diqu="河北省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlshenpi", "hebeisheng"])
    # driver = webdriver.Chrome()
    # for d in data:
    #     driver.get(d[1])
    #     print(d[1])
    #     f1(driver,2)
