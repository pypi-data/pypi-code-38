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

_name_='xinyu'

def f1(driver,num):

    locator = (By.XPATH, '//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page=driver.find_element_by_xpath('//*[@id="MoreInfoList1_Pager"]/div[1]/font[3]/b').text

    if int(page) != num:
        val = driver.find_element_by_xpath('//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a').get_attribute('href')[-30:-5]
        driver.execute_script("javascript:__doPostBack('MoreInfoList1$Pager','{}')".format(num))
        try:
            locator = (By.XPATH, '//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a[not(contains(@href,"%s"))]'%val)
            WebDriverWait(driver, 15).until(EC.presence_of_element_located(locator))
        except:
            locator = (By.XPATH, '//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a[not(contains(@href,"%s"))]' %val)
            WebDriverWait(driver, 15).until(EC.presence_of_element_located(locator))


    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', id='MoreInfoList1_DataGrid1')
    trs = table.find_all('tr')
    data=[]
    for tr in trs:
        tds = tr.find_all('td')
        href = tds[1].a['href']
        href = 'http://www.xyggzy.cn' + href
        title = tds[1].a['title']
        date_time = tds[2].get_text().strip()
        tmp = [title,date_time,href]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"] = None
    return df




def f2(driver):

    locator = (By.XPATH, '//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath('//*[@id="MoreInfoList1_Pager"]/div[1]/font[2]/b').text
    total=int(total)
    driver.quit()

    return total

def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="border"][string-length()>10]')

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
    div = soup.find('td',id='TDContent').parent.parent
    return div


data=[
    ["gcjs_gqita_zhao_bian_gg","http://www.xyggzy.cn/ggzy/jsgc/010001/MoreInfo.aspx?CategoryNum=010001",['name','ggstart_time','href','info'],f1,f2],
    ["gcjs_zhongbiaohx_gg","http://www.xyggzy.cn/ggzy/jsgc/010002/MoreInfo.aspx?CategoryNum=010002",['name','ggstart_time','href','info'],f1,f2],

    ["zfcg_zhaobiao_gg", "http://www.xyggzy.cn/ggzy/zfcg/009001/MoreInfo.aspx?CategoryNum=009001",["name", "ggstart_time", "href",'info'],f1,f2],
    ["zfcg_zhongbiaohx_gg", "http://www.xyggzy.cn/ggzy/zfcg/009002/MoreInfo.aspx?CategoryNum=009002",["name", "ggstart_time", "href",'info'],f1,f2],

    ["jqita_zhaobiao_gg", "http://www.xyggzy.cn/ggzy/xzjy/016001/MoreInfo.aspx?CategoryNum=016001",["name", "ggstart_time", "href",'info'],add_info(f1,{"gclx":"乡镇交易"}) ,f2],
    ["jqita_zhongbiaohx_gg", "http://www.xyggzy.cn/ggzy/xzjy/016002/MoreInfo.aspx?CategoryNum=016002",["name", "ggstart_time", "href",'info'],add_info(f1,{"gclx":"乡镇交易"}),f2],

]

def work(conp,**args):
    est_meta(conp,data=data,diqu="江西省新余市",**args)
    est_html(conp,f=f3,**args)
    # est_gg(conp,diqu="江西省新余市")


if __name__=='__main__':


    conp=["postgres","since2015","192.168.3.171","jiangxi","xinyu"]

    work(conp=conp,headless=False,num=1)