import time
from os.path import join, dirname

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

from zhulong.util.etl import est_tbs, est_meta, est_html, gg_existed, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]
from zhulong.util.conf import get_conp
#
# url="http://www.hbzbcg.cn/hbweb/jyxx/002001/002001005/002001005001/MoreInfo.aspx?CategoryNum=002001005001"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)



_name_='huaibei'


def f1(driver,num):
    locator = (By.XPATH, '//table[@id="MoreInfoList1_DataGrid1"]//tr[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath('//div[@id="MoreInfoList1_Pager"]//tr//font[@color="red"]/b').text

    if int(cnum) != num:
        val = driver.find_element_by_xpath('//table[@id="MoreInfoList1_DataGrid1"]//tr[1]//a').get_attribute('href')[-35:-5]
        driver.execute_script("javascript:__doPostBack('MoreInfoList1$Pager','{}')".format(num))
        locator = (By.XPATH, '//table[@id="MoreInfoList1_DataGrid1"]//tr[1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))


    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', id='MoreInfoList1_DataGrid1')
    trs = div.find_all('tr', valign='top')

    for tr in trs:
        tds = tr.find_all('td')
        href = tds[1].a['href']
        name = tds[1].a['title']
        if '</font>' in name:
            if name.startswith('<font'):
                name = re.findall(r'</font>(.+)', name)[0]
            else:
                name = re.findall(r'(.+)<font', name)[0]
        ggstart_time = tds[2].get_text().strip()

        if 'http' in href:
            href = href
        else:
            href = 'http://58.242.87.202' + href

        tmp = [name, ggstart_time, href]
        data.append(tmp)

    df=pd.DataFrame(data=data)
    df["info"] = None
    return df




def f2(driver):
    locator = (By.XPATH, '//table[@id="MoreInfoList1_DataGrid1"]//tr[1]//a')

    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath('//div[@id="MoreInfoList1_Pager"]//a[last()]').get_attribute('title')
    total=re.findall('\d+',total)[0]
    total = int(total)

    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,'//td[@class="infodetd"] | //div[contains(@id,"menutab") and (not(@style) or @style="")]')

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

    div = soup.find('td', attrs={'id': "TDContent"})
    if div == None:
        div = soup.find('div', attrs={'id': re.compile('menutab_6_\d'), 'style': ''})
        if div == None:
            raise ValueError

    return div



data=[
    ["gcjs_zhaobiao_diqu1_gg","http://58.242.87.202/hbweb/jyxx/002001/002001001/002001001001/MoreInfo.aspx?CategoryNum=002001001001",["name","ggstart_time","href","info"],add_info(f1,{"diqu":"市本级"}),f2],
    ["gcjs_zhaobiao_diqu2_gg","http://58.242.87.202/hbweb/jyxx/002001/002001001/002001001002/MoreInfo.aspx?CategoryNum=002001001002",["name","ggstart_time","href","info"],add_info(f1,{"diqu":"濉溪县"}),f2],

    ["gcjs_gqita_da_bian_diqu1_gg","http://58.242.87.202/hbweb/jyxx/002001/002001003/002001003001/MoreInfo.aspx?CategoryNum=002001003001",["name","ggstart_time","href","info"],add_info(f1,{"diqu":"市本级"}),f2],
    ["gcjs_gqita_da_bian_diqu2_gg","http://58.242.87.202/hbweb/jyxx/002001/002001003/002001003002/MoreInfo.aspx?CategoryNum=002001003002",["name","ggstart_time","href","info"],add_info(f1,{"diqu":"濉溪县"}),f2],

    ["gcjs_zhongbiaohx_diqu1_gg","http://58.242.87.202/hbweb/jyxx/002001/002001005/002001005001/MoreInfo.aspx?CategoryNum=002001005001",["name","ggstart_time","href","info"],add_info(f1,{"diqu":"市本级"}),f2],
    ["gcjs_zhongbiaohx_diqu2_gg","http://58.242.87.202/hbweb/jyxx/002001/002001005/002001005002/MoreInfo.aspx?CategoryNum=002001005002",["name","ggstart_time","href","info"],add_info(f1,{"diqu":"濉溪县"}),f2],

    ["gcjs_zhongbiao_diqu1_gg","http://58.242.87.202/hbweb/jyxx/002001/002001002/002001002001/MoreInfo.aspx?CategoryNum=002001002001",["name","ggstart_time","href","info"],add_info(f1,{"diqu":"市本级"}),f2],
    ["gcjs_zhongbiao_diqu2_gg","http://58.242.87.202/hbweb/jyxx/002001/002001002/002001002002/MoreInfo.aspx?CategoryNum=002001002002",["name","ggstart_time","href","info"],add_info(f1,{"diqu":"濉溪县"}),f2],

    ["zfcg_zhaobiao_diqu1_gg","http://58.242.87.202/hbweb/jyxx/002002/002002001/002002001001/MoreInfo.aspx?CategoryNum=002002001001",["name","ggstart_time","href","info"],add_info(f1,{"diqu":"市本级"}),f2],
    ["zfcg_zhaobiao_diqu2_gg","http://58.242.87.202/hbweb/jyxx/002002/002002001/002002001002/MoreInfo.aspx?CategoryNum=002002001002",["name","ggstart_time","href","info"],add_info(f1,{"diqu":"濉溪县"}),f2],

    ["zfcg_zhongbiao_diqu1_gg","http://58.242.87.202/hbweb/jyxx/002002/002002002/002002002001/MoreInfo.aspx?CategoryNum=002002002001",["name","ggstart_time","href","info"],add_info(f1,{"diqu":"市本级"}),f2],
    ["zfcg_zhongbiao_diqu2_gg","http://58.242.87.202/hbweb/jyxx/002002/002002002/002002002002/MoreInfo.aspx?CategoryNum=002002002002",["name","ggstart_time","href","info"],add_info(f1,{"diqu":"濉溪县"}),f2],

    ["zfcg_gqita_da_bian_diqu1_gg","http://58.242.87.202/hbweb/jyxx/002002/002002003/002002003001/MoreInfo.aspx?CategoryNum=002002003001",["name","ggstart_time","href","info"],add_info(f1,{"diqu":"市本级"}),f2],
    ["zfcg_gqita_da_bian_diqu2_gg","http://58.242.87.202/hbweb/jyxx/002002/002002003/002002003002/MoreInfo.aspx?CategoryNum=002002003002",["name","ggstart_time","href","info"],add_info(f1,{"diqu":"濉溪县"}),f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="安徽省淮北市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':

    work(conp=["postgres","since2015","192.168.3.171","anhui","huaibei"])