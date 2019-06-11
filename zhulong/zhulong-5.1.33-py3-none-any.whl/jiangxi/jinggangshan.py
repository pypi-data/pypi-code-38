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

from zhulong.util.etl import est_tbs, est_meta, est_html, est_gg, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]


# url="https://ggzy.changsha.gov.cn/spweb/CS/TradeCenter/tradeList.do?Deal_Type=Deal_Type2"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_='jinggangshan'

def f1(driver,num):

    locator = (By.XPATH, "//ul[@class='govpublic']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url=driver.current_url
    cnum = re.findall('_(\d+?).jspx', url)[0]

    if int(cnum) != num:

        val = driver.find_element_by_xpath("//ul[@class='govpublic']/li[1]/a").get_attribute('href').rsplit('/',maxsplit=1)[1]

        url=re.sub('_\d+?.jspx','_%s.jspx'%num,url)
        driver.get(url)
        locator = (By.XPATH, "//ul[@class='govpublic']/li[1]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data=[]

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    lis = soup.find('ul', class_='govpublic').find_all('li',recursive=False)

    for li in lis:
        href = li.a['href']
        ggstart_time = li.span.get_text().strip()
        name = li.a['title'].strip()

        if 'http' in href:
            href=href
        else:
            href='http:'+href
        tmp = [name, ggstart_time, href]
        data.append(tmp)

    df=pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):

    locator = (By.XPATH, "//ul[@class='govpublic']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath("//ul[@class='pager']/li[last()-1]/a").text

    total=int(total)

    driver.quit()

    return total

def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="row"][contains(@style,"padding") and string-length()>10]')

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
    div = soup.find('div',class_="row",style=re.compile('padding'))

    return div



data=[
    ["gcjs_zhaobiao_gg","http://www.jgs.gov.cn/node/5340_1.jspx",['name','ggstart_time','href','info'],f1,f2],
    ["qsy_zhaobiao_gg","http://www.jgs.gov.cn/node/5348_1.jspx",['name','ggstart_time','href','info'],add_info(f1,{"gclx":"限额以下工程"}),f2],
    ["zfcg_zhaobiao_gg","http://www.jgs.gov.cn/node/5339_1.jspx",['name','ggstart_time','href','info'],f1,f2],
    ["jqita_zhongbiaohx_gg","http://www.jgs.gov.cn/node/5344_1.jspx",['name','ggstart_time','href','info'],f1,f2],

]

def work(conp,**args):
    est_meta(conp,data=data,diqu="江西省井冈山市",**args)
    est_html(conp,f=f3,**args)



if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","jiangxi","jinggangshan"]

    work(conp=conp,headless=False,num=1)