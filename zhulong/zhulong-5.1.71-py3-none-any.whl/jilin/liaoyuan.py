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
# url="http://www.ccggzy.gov.cn/qxxxgk/003002/003002004/CountyPurhcaseNotice.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)
#

_name_='liaoyuan'


def f1(driver,num):

    locator = (By.XPATH, '//ul[@class="ewb-info-list"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url

    cnum = int(re.findall('/(\d+).html', url)[0])

    if cnum != num:

        url = url.rsplit('/', maxsplit=1)[0]  + "/%s.html"%str(num)

        val = driver.find_element_by_xpath('//ul[@class="ewb-info-list"]/li[1]/a').get_attribute('href')[-25:-5]
        driver.get(url)
        locator = (By.XPATH, '//ul[@class="ewb-info-list"]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('ul', class_='ewb-info-list')
    trs = div.find_all('li', attrs={'class': 'ewb-list-node clearfix'})

    for tr in trs:

        href = tr.a['href']

        ggstart_time = tr.span.get_text().strip()
        tags = '|'.join([w.extract().get_text() for w in tr.a.find_all('font')])
        info = {"tags": tags}
        info=json.dumps(info,ensure_ascii=False)
        name = tr.a.get_text().strip()
        if 'http' in href:
            href = href
        else:
            href = 'http://www.lygg.gov.cn' + href

        tmp = [name, ggstart_time, href,info]

        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//ul[@class="ewb-info-list"]/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath('//span[@id="index"]').text
    total = re.findall('1/(\d+)', page)[0]

    total = int(total)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="news-article"][string-length()>10]')

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
    div = soup.find('div', class_='news-article')

    return div




data=[

    ["gcjs_zhaobiao_gg","http://www.lygg.gov.cn/jyxx/003001/003001001/1.html",["name","ggstart_time","href","info"],f1,f2],
    ["gcjs_biangeng_gg","http://www.lygg.gov.cn/jyxx/003001/003001002/1.html",["name","ggstart_time","href","info"],f1,f2],
    ["gcjs_zhongbiaohx_gg","http://www.lygg.gov.cn/jyxx/003001/003001003/1.html",["name","ggstart_time","href","info"],f1,f2],

    ["zfcg_zhaobiao_gg","http://www.lygg.gov.cn/jyxx/003002/003002001/1.html",["name","ggstart_time","href","info"],f1,f2],
    ["zfcg_biangeng_gg","http://www.lygg.gov.cn/jyxx/003002/003002002/1.html",["name","ggstart_time","href","info"],f1,f2],
    ["zfcg_zhongbiaohx_gg","http://www.lygg.gov.cn/jyxx/003002/003002003/1.html",["name","ggstart_time","href","info"],f1,f2],

]


#网站变更 http://www.lygg.gov.cn
##变更时间 2019-5-16



def work(conp,**args):
    est_meta(conp,data=data,pageLoadStrategy='none',pageloadtimeout=60,diqu="吉林省辽源市",**args)
    est_html(conp,f=f3,**args)

if __name__=='__main__':


    work(conp=["postgres","since2015","192.168.3.171","jilin","liaoyuan"],headless=False,num=1,total=2)