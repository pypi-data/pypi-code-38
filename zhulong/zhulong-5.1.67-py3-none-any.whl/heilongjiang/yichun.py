import time
import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json

from zhulong.util.etl import est_tbs,est_meta,est_html

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url="http://www.bzztb.gov.cn/BZWZ/jyxx/003001/003001001/003001001001/003001001001001/"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)
#

_name_='yichun'

def f1(driver,num):
    locator = (By.XPATH, '//div[@class="listcon"]/div[1]/ul[2]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath('//div[@class="page"]/b[2]').text
    cnum = re.findall('(\d+)/', cnum)[0]

    if cnum != str(num):
        url = driver.current_url
        url = url.rsplit('=', maxsplit=1)[0] + '=' + str(num)
        val = driver.find_element_by_xpath('//div[@class="listcon"]/div[1]/ul[2]/li[1]/a').get_attribute('href')[-15:-5]

        driver.get(url)
        locator = (By.XPATH, '//div[@class="listcon"]/div[1]/ul[2]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='trends')
    divs = div.find_all('li')

    for li in divs:
        href = li.a['href']
        name = li.a['title']
        ggstart_time = li.span.get_text()
        if 'http' in href:
            href = href
        else:
            href = 'http://ggzy.yc.gov.cn' + href
        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="listcon"]/div[1]/ul[2]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath('//div[@class="page"]/b[2]').text

    page = re.findall('/(\d+)', page)[0]
    total = int(page)
    driver.quit()

    return total




def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="con02"][string-length()>10]')
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
    div=soup.find('div',class_='con02')

    return div


data=[
    ["gcjs_zhaobiao_gg","http://ggzy.yc.gov.cn/docweb/docList.action?channelId=2117&parentChannelId=-1&pageNo=1",["name","ggstart_time","href","info"],f1,f2],
    ["gcjs_kongzhijia_gg","http://ggzy.yc.gov.cn/docweb/docList.action?channelId=2119&parentChannelId=-1&pageNo=1",["name","ggstart_time","href","info"],f1,f2],
    ["gcjs_zhongbiaohx_gg","http://ggzy.yc.gov.cn/docweb/docList.action?channelId=2120&parentChannelId=-1&pageNo=1",["name","ggstart_time","href","info"],f1,f2],
    ["gcjs_gqita_da_bian_gg","http://ggzy.yc.gov.cn/docweb/docList.action?channelId=2118&parentChannelId=-1&pageNo=1",["name","ggstart_time","href","info"],f1,f2],

    ["zfcg_zhaobiao_gg","http://ggzy.yc.gov.cn/docweb/docList.action?channelId=2121&parentChannelId=-1&pageNo=1",["name","ggstart_time","href","info"],f1,f2],
    #包含：中标，流标
    ["zfcg_zhongbiao_gg","http://ggzy.yc.gov.cn/docweb/docList.action?channelId=2123&parentChannelId=-1&pageNo=1",["name","ggstart_time","href","info"],f1,f2],
    ["zfcg_gqita_da_bian_gg","http://ggzy.yc.gov.cn/docweb/docList.action?channelId=2122&parentChannelId=-1&pageNo=1",["name","ggstart_time","href","info"],f1,f2],

]

def work(conp,**args):
    est_meta(conp,data=data,diqu="黑龙江省伊春市",**args)
    est_html(conp,f=f3,**args)

if __name__=='__main__':

    work(conp=["postgres","since2015","192.168.3.171","heilongjiang","yichun"],num=5,cdc_total=9)