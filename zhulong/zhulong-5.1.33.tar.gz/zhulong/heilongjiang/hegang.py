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
# #

_name_='hegang'

def f1(driver,num):
    locator = (By.XPATH, '//ul[@class="ewb-info-items"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath('//span[@id="index"]').text
    cnum = re.findall('(\d+)/', cnum)[0]

    if cnum != str(num):
        url = driver.current_url
        url = url.rsplit('/', maxsplit=1)[0] + '/' + str(num) + '.html'

        val = driver.find_element_by_xpath('//ul[@class="ewb-info-items"]/li[1]/a').get_attribute('href')[-30:-5]

        driver.get(url)

        locator = (By.XPATH, '//ul[@class="ewb-info-items"]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('ul', class_='ewb-info-items')
    divs = div.find_all('li')

    for li in divs:
        href = li.a['href']
        name = li.a['title']
        ggstart_time = li.span.get_text().strip()
        if 'http' in href:
            href = href
        else:
            href = 'http://www.hgggzyjyw.org.cn' + href
        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@class="ewb-info-items"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath('//span[@id="index"]').text

    page = re.findall('/(\d+)', page)[0]
    total = int(page)
    driver.quit()

    return total




def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="ewb-artical"]')

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

    div=soup.find('div',class_='ewb-artical')

    return div




data=[
    ["gcjs_zhaobiao_gg","http://www.hgggzyjyw.org.cn/gcjs/014001/1.html",["name","ggstart_time","href","info"],f1,f2],
    ["gcjs_liubiao_gg","http://www.hgggzyjyw.org.cn/gcjs/014002/1.html",["name","ggstart_time","href","info"],f1,f2],

    ["gcjs_biangeng_gg","http://www.hgggzyjyw.org.cn/gcjs/014003/1.html",["name","ggstart_time","href","info"],f1,f2],
    ["gcjs_zhongbiaohx_gg","http://www.hgggzyjyw.org.cn/gcjs/014004/1.html",["name","ggstart_time","href","info"],f1,f2],

    ["zfcg_zhaobiao_gg","http://www.hgggzyjyw.org.cn/zfcg/015001/1.html",["name","ggstart_time","href","info"],f1,f2],
    ["zfcg_gqita_bian_liu_gg","http://www.hgggzyjyw.org.cn/zfcg/015002/1.html",["name","ggstart_time","href","info"],f1,f2],
    ["zfcg_zhongbiao_gg","http://www.hgggzyjyw.org.cn/zfcg/015003/1.html",["name","ggstart_time","href","info"],f1,f2],


]

def work(conp,**args):
    est_meta(conp,data=data,diqu="黑龙江省鹤岗市",**args)
    est_html(conp,f=f3,**args)

if __name__=='__main__':


    work(conp=["postgres","since2015","192.168.3.171","heilongjiang","hegang"])