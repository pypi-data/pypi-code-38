import json
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
from zhulong.util.etl import est_tables, gg_meta, gg_html, est_meta, est_html

_name_='jiaozhou'

def f1(driver, num):
    locator = (By.XPATH, "(//li[@class='lnWithData']/a)[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page_all = driver.find_element_by_xpath('//span[@class="td_Page"]').text
    cnum = re.findall(r'第(\d+)页', page_all)[0]

    if num != int(cnum):
        val = driver.find_element_by_xpath('(//li[@class="lnWithData"]/a)[1]').get_attribute('href')[-35:]
        driver.execute_script("javascript:pgTo({})".format(num-1))
        time.sleep(0.5)
        locator = (By.XPATH, "(//li[@class='lnWithData']/a)[1][not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    tbody = soup.find("ul", class_="infoList")
    trs = tbody.find_all("li", class_='lnWithData')
    data = []
    for tr in trs:
        info = {}
        a = tr.find("a")
        title = a.text.strip()
        try:
            stat = tr.find('span').text.strip()
            state = re.findall(r'\[(.*)\]', stat)[0]
        except:
            state = "-"
        span_1 = tr.find('span').text.strip()
        span_2 = re.findall(r'(\d+.*)', span_1)[0]
        if re.findall(r'^\[(\w+?)\]', title):
            lx = re.findall(r'^\[(\w+?)\]', title)[0]
            info['lx']=lx
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:info = None
        tmp = [title, span_2, "http://jzggzy.jiaozhou.gov.cn/" + a["href"], info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df




def f2(driver):
    locator = (By.XPATH, '//span[@class="td_Page"]')
    page_all = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    page = re.findall(r'共(\d+)页', page_all)[0]
    driver.quit()
    return int(page)


def f3(driver,url):
    driver.get(url)
    locator=(By.XPATH, "//table[@class='gggsTb'][string-length()>15] | //div[@class='wrapperNei'][string-length()>15]")
    WebDriverWait(driver,10).until(EC.presence_of_all_elements_located(locator))
    before=len(driver.page_source)
    time.sleep(0.1)
    after=len(driver.page_source)
    i=0
    while before!=after:
        before=len(driver.page_source)
        time.sleep(0.1)
        after=len(driver.page_source)
        i+=1
        if i>5:break
    page=driver.page_source
    soup=BeautifulSoup(page,'html.parser')
    div=soup.find('table',class_='gggsTb')
    if div == None:
        div = soup.find('div', class_='wrapperNei')
    return div





data = [
        ["gcjs_zhaobiao_gg","http://jzggzy.jiaozhou.gov.cn/list.jsp?type=GJGG",
         ["name", "ggstart_time", "href","info"],f1,f2],

        ["gcjs_zhongbiao_gg","http://jzggzy.jiaozhou.gov.cn/list.jsp?regCode=&type=GJGS&subType=0",
         ["name", "ggstart_time", "href","info"],f1,f2],


        ["zfcg_zhaobiao_gg","http://jzggzy.jiaozhou.gov.cn/list.jsp?type=ZCGG",
         ["name",  "ggstart_time", "href","info"],f1,f2],

        ["zfcg_zhongbiao_gg","http://jzggzy.jiaozhou.gov.cn/list.jsp?regCode=&type=ZCGS&subType=0",
         ["name", "ggstart_time", "href","info"],f1,f2],
    ]


def work(conp,**args):
    est_meta(conp,data=data,diqu="山东省胶州市",**args)
    est_html(conp,f=f3,**args)



if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","shandong","jiaozhou"],pageloadtimeout=60)

