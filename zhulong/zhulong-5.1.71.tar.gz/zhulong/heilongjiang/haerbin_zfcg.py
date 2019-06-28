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

from zhulong.util.etl import est_tbs,est_meta,est_html

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url="http://www.hljcg.gov.cn/xwzs!queryXwxxqx.action?lbbh=52301"
# driver=webdriver.Chrome()
# driver.maximize_window()
# driver.get(url)
# # #


_name_='haerbin_zfcg'

def f1(driver, num):

    locator = (By.XPATH, '//div[@class="yahoo"]/div[1]/span/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath('//div[@class="yahoo2"]/div/span/b[2]').text.strip()
    cnum = re.findall('(\d+)/', cnum)[0]
    if cnum != str(num):
        val = driver.find_element_by_xpath('//div[@class="yahoo"]/div[1]/span/a').get_attribute('onclick')
        val=re.findall('javascript:location.href=(.+);return false',val)[0].strip("'")
        driver.execute_script("javascript:jump('{}');return false;".format(num))

        locator = (By.XPATH, '//div[@class="yahoo"]/div[1]/span/a[not(contains(@onclick,"%s"))]' % val)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located(locator))

    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='yahoo')
    divs = div.find_all('div', class_="xxei")

    for li in divs:
        href = li.find('span', class_="lbej").a['onclick']
        name = li.find('span', class_="lbej").a.get_text().strip()
        ggstart_time = li.find('span', class_="sjej").get_text()
        zbdl = li.find('span', class_="nrej").get_text()
        href = re.findall('javascript:location.href=(.+);return false', href)[0].strip("'")

        if 'http' in href:
            href = href
        else:
            href = 'http://www.hljcg.gov.cn' + href
        info={"zbdl":zbdl}
        info=json.dumps(info,ensure_ascii=False)
        tmp = [name, ggstart_time, href,info]
        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="yahoo"]/div[1]/span/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.find_element_by_xpath('//div[@class="yahoo2"]/div/span/b[2]').text
    page = re.findall('/(\d+)', page)[0]

    total = int(page)
    driver.quit()
    return total


def chang_type(f,num):
    def inner(*args):
        driver=args[0]
        time.sleep(0.1)
        url=driver.current_url
        if 'index.jsp' in url:
            locator=(By.XPATH,'(//div[contains(@class,"cen_new")]//div[@class="xx1"])[%d]/a'%num)
            WebDriverWait(driver,10).until(EC.presence_of_element_located(locator)).click()
            locator=(By.XPATH,'//div[@class="yahoo"]/div[1]//a')
            WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

        return f(*args)
    return inner



def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="xxej"]')

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
    div = soup.find('div', class_="xxej")

    return div


data = [


    ["zfcg_zhaobiao_gg","http://www.hljcg.gov.cn/welcome.jsp?dq=2301",["name","ggstart_time","href","info"],chang_type(f1,1),chang_type(f2,1)],

    ["zfcg_zhongbiao_gg", "http://www.hljcg.gov.cn/welcome.jsp?dq=2301",
     [ "name", "ggstart_time", "href", "info"], chang_type(f1,3), chang_type(f2,3)],
]

def work(conp,**args):
    est_meta(conp,data=data,diqu="黑龙江省哈尔滨市",**args)
    est_html(conp,f=f3,**args)

if __name__=='__main__':


    work(conp=["postgres", "since2015", "192.168.3.171", "heilongjiang", "haerbin"])
    pass