import pandas as pd  
import re

from lxml import etree
from selenium import webdriver 
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write,db_command,db_query
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
import sys 
import time
import json
from zhulong.util.etl import est_tbs,est_meta,est_html,gg_existed,add_info

_name_='beijing'


def f1(driver,num):

    locator = (By.XPATH, '//ul[@class="article-list2"]/li[1]/a')
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute("href")[-25:]

    locator = (By.XPATH, '//ul[@class="pages-list"]/li/a')
    txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    cnum = int(re.findall('(\d+)\/',txt)[0])


    if str(cnum) != str(num):
        n_url = re.sub('index[_\d]*','index_'+str(num),driver.current_url)
        driver.get(n_url)

        locator = (By.XPATH, '//ul[@class="article-list2"]/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    body = etree.HTML(html)
    contents = body.xpath('//ul[@class="article-list2"]/li')
    for content in contents:
        name = content.xpath('./a/@title')[0].strip()
        href = 'https://ggzyfw.beijing.gov.cn' + content.xpath('./a/@href')[0].strip()
        ggstart_time = content.xpath('./div/text()')[0].strip()
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df=pd.DataFrame(data=data,columns=["name", "ggstart_time", "href"])
    df['info'] = None
    return df 


def f2(driver):
    locator = (By.XPATH, '//ul[@class="pages-list"]/li/a')
    txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    total_page = int(re.findall('\/(\d+)',txt)[0])

    driver.quit()
    return total_page


def f3(driver,url):

    driver.get(url)

    locator=(By.XPATH,'//div[@class="content-list"]')
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

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
    div = soup.find('div', class_='content-list')

    return div


data=[
    ["gcjs_gqita_gg","https://ggzyfw.beijing.gov.cn/jylcgcjs/index.html",["name","ggstart_time","href","info"],f1,f2],
    ["zfcg_gqita_gg","https://ggzyfw.beijing.gov.cn/jylczfcg/index.html",["name","ggstart_time","href","info"],f1,f2],

]

def work(conp,**args):
    est_meta(conp,data=data,diqu="北京市",**args)
    est_html(conp,f=f3,**args)

if __name__=='__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "beijing", "beijing"],total=2,headless=False,num=1)
    # for t in data:
    #     driver =webdriver.Chrome()
    #     driver.get(t[1])
    #     tpage = f2(driver)
    #     print(tpage)
    #
    #     for i in range(1,5):
    #         driver = webdriver.Chrome()
    #         driver.get(t[1])
    #         df = f1(driver,i).values.tolist()
    #
    #         for d in df:
    #             print(d)
    #             f3(driver, d[2])
    #             driver.quit()

