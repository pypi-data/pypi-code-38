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

_name_='nanchang'

def f1(driver,num):
    locator = (By.XPATH, '//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page=driver.find_element_by_xpath('//*[@id="MoreInfoList1_Pager"]/table/tbody/tr/td[1]/font[3]/b').text

    if int(page) != num:
        val = driver.find_element_by_xpath('//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a').get_attribute(
            "href")[- 30:-5]
        driver.execute_script("javascript:__doPostBack('MoreInfoList1$Pager','{}')".format(num))

        locator = (By.XPATH, '//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a[not(contains(@href,"%s"))]'%val)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located(locator))

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', id='MoreInfoList1_DataGrid1')
    trs = table.find_all('tr')
    data=[]
    for tr in trs:
        tds = tr.find_all('td')
        href = tds[1].a['href']
        href = 'http://ncztb.nc.gov.cn' + href
        title = tds[1].a['title']
        diqu=tds[1].a.find('font',color="red")
        if diqu:
            info={"diqu":diqu.get_text()}
            info=json.dumps(info,ensure_ascii=False)
        else:
            info=None
        date_time = tds[2].get_text().strip()
        tmp = [title, date_time,href,info]
        data.append(tmp)
    df=pd.DataFrame(data=data)

    return df




def f2(driver):

    locator = (By.XPATH, '//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath('//*[@id="MoreInfoList1_Pager"]/table/tbody/tr/td[1]/font[2]/b').text
    total=int(total)
    driver.quit()

    return total

def f3(driver, url):
    driver.get(url)
    try:
        locator = (By.XPATH, '//table[@id="tblInfo"][string-length()>5]')
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    except:
        locator = (By.XPATH, '/html/body')
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
    div = soup.find('td', id="TDContent")

    if div == None:
        div = soup.find('embed', id="plugin")
    elif not div.get_text().strip():
        div = soup.find('table', id="tblInfo")
    if div == None:
        raise ValueError

    return div





data=[
    ["gcjs_fangjianshizheng_zhaobiao_gg","http://ncztb.nc.gov.cn/nczbw/jyxx/002001/002001002/MoreInfo.aspx?CategoryNum=002001002",['name','ggstart_time','href','info'],add_info(f1,{"gclx":"房建市政"}),f2],
    ["gcjs_fangjianshizheng_gqita_da_bian_gg","http://ncztb.nc.gov.cn/nczbw/jyxx/002001/002001004/MoreInfo.aspx?CategoryNum=002001004",['name','ggstart_time','href','info'],add_info(f1,{"gclx":"房建市政"}),f2],
    ["gcjs_fangjianshizheng_zhongbiaohx_gg","http://ncztb.nc.gov.cn/nczbw/jyxx/002001/002001005/MoreInfo.aspx?CategoryNum=002001005",['name','ggstart_time','href','info'],add_info(f1,{"gclx":"房建市政"}),f2],

    ["gcjs_jiaotong_zhaobiao_gg","http://ncztb.nc.gov.cn/nczbw/jyxx/002002/002002002/MoreInfo.aspx?CategoryNum=002002002",["name", "ggstart_time", "href",'info'],add_info(f1,{"gclx":"交通工程"}),f2],
    ["gcjs_jiaotong_gqita_da_bian_gg","http://ncztb.nc.gov.cn/nczbw/jyxx/002002/002002003/MoreInfo.aspx?CategoryNum=002002003",["name", "ggstart_time", "href",'info'],add_info(f1,{"gclx":"交通工程"}),f2],

    ["gcjs_jiaotong_zhongbiao_gg","http://ncztb.nc.gov.cn/nczbw/jyxx/002002/002002005/MoreInfo.aspx?CategoryNum=002002005",["name", "ggstart_time", "href",'info'],add_info(f1,{"gclx":"交通工程"}),f2],

    ["gcjs_shuili_zhaobiao_gg", "http://ncztb.nc.gov.cn/nczbw/jyxx/002003/002003001/MoreInfo.aspx?CategoryNum=002003001",["name", "ggstart_time", "href",'info'],add_info(f1,{"gclx":"水利工程"}),f2],
    ["gcjs_shuili_gqita_da_bian_gg", "http://ncztb.nc.gov.cn/nczbw/jyxx/002003/002003002/MoreInfo.aspx?CategoryNum=002003002",["name", "ggstart_time", "href",'info'],add_info(f1,{"gclx":"水利工程"}),f2],
    ["gcjs_shuili_zhongbiaohx_gg", "http://ncztb.nc.gov.cn/nczbw/jyxx/002003/002003004/MoreInfo.aspx?CategoryNum=002003004",["name", "ggstart_time", "href",'info'],add_info(f1,{"gclx":"水利工程"}),f2],

    ["gcjs_tielu_zhaobiao_gg", "http://ncztb.nc.gov.cn/nczbw/jyxx/002009/002009001/MoreInfo.aspx?CategoryNum=002009001",["name", "ggstart_time", "href",'info'],add_info(f1,{"gclx":"铁路工程"}),f2],
    ["gcjs_tielu_gqita_da_bian_gg", "http://ncztb.nc.gov.cn/nczbw/jyxx/002009/002009003/MoreInfo.aspx?CategoryNum=002009003",["name", "ggstart_time", "href",'info'],add_info(f1,{"gclx":"铁路工程"}),f2],
    ["gcjs_tielu_zhongbiao_gg", "http://ncztb.nc.gov.cn/nczbw/jyxx/002009/002009004/MoreInfo.aspx?CategoryNum=002009004",["name", "ggstart_time", "href",'info'],add_info(f1,{"gclx":"铁路工程"}),f2],

    ["gcjs_zhongdian_zhaobiao_gg", "http://ncztb.nc.gov.cn/nczbw/jyxx/002010/002010001/MoreInfo.aspx?CategoryNum=002010001",["name", "ggstart_time", "href",'info'],add_info(f1,{"gclx":"重点工程"}),f2],
    ["gcjs_zhongdian_gqita_da_bian_gg", "http://ncztb.nc.gov.cn/nczbw/jyxx/002010/002010002/MoreInfo.aspx?CategoryNum=002010002",["name", "ggstart_time", "href",'info'],add_info(f1,{"gclx":"重点工程"}),f2],
    ["gcjs_zhongdian_zhongbiaohx_gg", "http://ncztb.nc.gov.cn/nczbw/jyxx/002010/002010004/MoreInfo.aspx?CategoryNum=002010004",["name", "ggstart_time", "href",'info'],add_info(f1,{"gclx":"重点工程"}),f2],

    ["zfcg_zhaobiao_gg", "http://ncztb.nc.gov.cn/nczbw/jyxx/002004/002004001/MoreInfo.aspx?CategoryNum=002004001",["name", "ggstart_time", "href",'info'],f1,f2],
    ["zfcg_biangeng_gg", "http://ncztb.nc.gov.cn/nczbw/jyxx/002004/002004002/MoreInfo.aspx?CategoryNum=002004002",["name", "ggstart_time", "href",'info'],f1,f2],
    ["zfcg_gqita_da_bian_gg", "http://ncztb.nc.gov.cn/nczbw/jyxx/002004/002004003/MoreInfo.aspx?CategoryNum=002004003", ["name", "ggstart_time", "href",'info'],f1,f2],
    ["zfcg_zhongbiao_gg", "http://ncztb.nc.gov.cn/nczbw/jyxx/002004/002004004/MoreInfo.aspx?CategoryNum=002004004",["name", "ggstart_time", "href",'info'],f1,f2],

    ["jqita_zhaobiao_gg", "http://ncztb.nc.gov.cn/nczbw/jyxx/002011/002011001/MoreInfo.aspx?CategoryNum=002011001",["name", "ggstart_time", "href",'info'],f1,f2],
    ["jqita_zhongbiao_gg", "http://ncztb.nc.gov.cn/nczbw/jyxx/002011/002011002/MoreInfo.aspx?CategoryNum=002011002",["name", "ggstart_time", "href",'info'],f1,f2],
    ["gcjs_jiaotong_zgysjg_gg","http://ncztb.nc.gov.cn/nczbw/jyxx/002002/002002004/MoreInfo.aspx?CategoryNum=002002004",
     ["name", "ggstart_time", "href",'info'],add_info(f1,{"gclx":"交通工程"}),f2],
    ["gcjs_tielu_zgys_gg", "http://ncztb.nc.gov.cn/nczbw/jyxx/002009/002009002/MoreInfo.aspx?CategoryNum=002009002",
     ["name", "ggstart_time", "href",'info'],add_info(f1,{"gclx":"铁路工程"}),f2],

    ["zfcg_zhaobiao_danyilaiyuan_gg", "http://ncztb.nc.gov.cn/nczbw/jyxx/002004/002004005/MoreInfo.aspx?CategoryNum=002004005",["name", "ggstart_time", "href",'info'],add_info(f1,{"zbfs":"单一来源"}),f2],
    ["gcjs_jiaotong_zgys_gg", "http://ncztb.nc.gov.cn/nczbw/jyxx/002002/002002001/MoreInfo.aspx?CategoryNum=002002001",["name", "ggstart_time", "href",'info'],add_info(f1,{"gclx":"交通工程"}),f2],

]

def work(conp,**args):
    est_meta(conp,data=data,diqu="江西省南昌市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","jiangxi","nanchang"]

    work(conp=conp,headless=False,num=1)