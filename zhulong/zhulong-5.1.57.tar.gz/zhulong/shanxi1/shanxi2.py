import json
import math
import time
import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zhulong.util.etl import est_meta, est_html, add_info

_name_ = 'shanxi2'


def f1(driver, num):

    locator = (By.XPATH, '//body[string-length()>500][contains(string(),"操作成功")]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = int(re.findall("&page=(\d+)&", url)[0])

    mark_url=re.findall('getMore(.+?)Info',url)[0]
    if num != cnum:
        page_len=len(driver.page_source)
        url = re.sub("&page=\d+&", "&page=%s&"%num, url)
        driver.get(url)
        locator = (By.XPATH, '//body[string-length()>500][contains(string(),"操作成功")]')
        WebDriverWait(driver, 10).until(lambda driver:len(driver.page_source)!=page_len and EC.presence_of_element_located(locator))

    data=[]
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    body = soup.find("body").text
    content1=json.loads(body)
    contents=content1.get('obj')
    for c in contents:

        name=c.get('PROJECTNAME')
        ggstart_time=c.get('RECEIVETIME')
        procode=c.get('PROJECTCODE')
        url_s=c.get('URL')

        ID=c.get('ID')

        href='http://prec.sxzwfw.gov.cn/moreInfoController.do?get{}Detail&url='.format(mark_url)
        href=''.join([href,url_s,'&id=',ID])

        info=json.dumps({'procode':procode},ensure_ascii=False)

        tmp = [name,ggstart_time,href,info]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator=(By.XPATH,'//body[string-length()>500][contains(string(),"attribute")]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    html=driver.page_source
    total=re.findall('"attribute":"(\d+)"',html)[0]
    total=math.ceil(int(total)/100)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="body_main"][string-length()>100]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

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
    div = soup.find('div', class_='w1000')

    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://prec.sxzwfw.gov.cn/moreInfoController.do?getMoreNoticeInfo&page=1&rows=100&dateFlag=&tableName=gcjs&projectRegion=&sjly=&projectName=&beginReceivetime=&endReceivetime=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_gg",
     "http://prec.sxzwfw.gov.cn/moreInfoController.do?getMoreNoticeInfo&page=1&rows=100&dateFlag=&tableName=zfcg&projectRegion=&sjly=&projectName=&beginReceivetime=&endReceivetime=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["yiliao_zhaobiao_gg",
     "http://prec.sxzwfw.gov.cn/moreInfoController.do?getMoreNoticeInfo&page=1&rows=100&dateFlag=&tableName=yp&projectRegion=&sjly=&projectName=&beginReceivetime=&endReceivetime=",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["gcjs_zhongbiaohx_gg",
     "http://prec.sxzwfw.gov.cn/moreInfoController.do?getMoreResultNoticeInfo&page=1&rows=100&dateFlag=&tableName=gcjs&projectRegion=&sjly=&projectName=&beginReceivetime=&endReceivetime=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiaohx_gg",
     "http://prec.sxzwfw.gov.cn/moreInfoController.do?getMoreResultNoticeInfo&page=1&rows=100&dateFlag=&tableName=zfcg&projectRegion=&sjly=&projectName=&beginReceivetime=&endReceivetime=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["yiliao_zhongbiaohx_gg",
     "http://prec.sxzwfw.gov.cn/moreInfoController.do?getMoreResultNoticeInfo&page=1&rows=100&dateFlag=&tableName=yp&projectRegion=&sjly=&projectName=&beginReceivetime=&endReceivetime=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp=conp, data=data, diqu="山西省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "shanxi1", "shenghui"],headless=False,num=1,total=2)


