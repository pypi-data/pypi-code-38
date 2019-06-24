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

# #
# url="http://www.bzztb.gov.cn/BZWZ/jyxx/003001/003001001/003001001001/003001001001001/"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)
#

_name_='qiqihaer'

def f1(driver,num):
    locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]/div/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath('//span[@id="index"]').text.strip()
    cnum = re.findall('(\d+)/', cnum)[0]

    if cnum != str(num):
        url = driver.current_url
        if num ==1:
            url = url.rsplit('/', maxsplit=1)[0] + '/' + 'about.html'
        else:
            url = url.rsplit('/', maxsplit=1)[0] + '/' + str(num) + '.html'

        val = driver.find_element_by_xpath('//ul[@class="wb-data-item"]/li[1]/div/a').get_attribute('href')[-30:-5]
        driver.get(url)
        locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]/div/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('ul', class_='wb-data-item')
    divs = div.find_all('li', class_="wb-data-list")

    for li in divs:
        href = li.div.a['href']
        name = li.div.a.get_text().strip()
        ggstart_time = li.span.get_text()
        if 'http' in href:
            href = href
        else:
            href = 'http://www.qqhrggzy.cn' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)

    df=pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]/div/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath('//span[@id="index"]').text

    page = re.findall('/(\d+)', page)[0]
    total = int(page)
    driver.quit()

    return total




def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="ewb-art"]')

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
    div=soup.find('div',class_="ewb-main ewb-min-height")
    div.find('div',class_='ewb-location').extract()
    div.find('div',class_='ewb-art-hd').extract()

    return div




data=[
    ["gcjs_zhaobiao_gg","http://ggzy.qqhr.gov.cn/jyxx/003001/003001001/about.html",["name","ggstart_time","href","info"],f1,f2],
    ["gcjs_biangeng_gg","http://ggzy.qqhr.gov.cn/jyxx/003001/003001002/about.html",["name","ggstart_time","href","info"],f1,f2],
    #包含中标，中标候选人，放弃中标
    ["gcjs_zhongbiaohx_gg","http://ggzy.qqhr.gov.cn/jyxx/003001/003001004/about.html",["name","ggstart_time","href","info"],f1,f2],

    ["zfcg_zhaobiao_gg","http://ggzy.qqhr.gov.cn/jyxx/003002/003002001/about.html",["name","ggstart_time","href","info"],f1,f2],
    ["zfcg_biangeng_gg","http://ggzy.qqhr.gov.cn/jyxx/003002/003002002/about.html",["name","ggstart_time","href","info"],f1,f2],
    #包含中标，放弃中标，废标
    ["zfcg_zhongbiao_gg","http://ggzy.qqhr.gov.cn/jyxx/003002/003002003/about.html",["name","ggstart_time","href","info"],f1,f2],
    #包含单一性来源，预采公告
    ["zfcg_gqita_yu_dan_gg","http://ggzy.qqhr.gov.cn/jyxx/003002/003002004/about.html",["name","ggstart_time","href","info"],f1,f2],


]

##网站变更 http://ggzy.qqhr.gov.cn
##变更时间 2019-5-16



def work(conp,**args):
    est_meta(conp,data=data,diqu="黑龙江省齐齐哈尔市",**args)
    est_html(conp,f=f3,**args)

if __name__=='__main__':
    conp = ["postgres", "since2015", "192.168.3.171", "heilongjiang", "qiqihaer"]

    work(conp=conp)