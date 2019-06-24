import time
from collections import OrderedDict
from os.path import join, dirname
from pprint import pprint

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

from zhulong.util.etl import est_tbs, est_meta, est_html, gg_existed, add_info,est_gg
from zhulong.util.conf import get_conp
# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]


# url="http://www.szggzyjy.cn/szfront/jyxx/002001/002001001/002001001001/"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)


_name_='chizhou'



def f1(driver,num):

    locator = (By.XPATH, '//li[@class="wb-data-list"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum=re.findall('Paging=(\d+)',url)[0]
    if int(cnum) != num:
        val=driver.find_element_by_xpath('//li[@class="wb-data-list"][1]//a').get_attribute('href')[-50:-30]
        url=re.sub('Paging=\d+','Paging=%d'%num,url)
        driver.get(url)
        locator=(By.XPATH,'//li[@class="wb-data-list"][1]//a[not(contains(@href,"%s"))]'%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    lis = soup.find_all('li', class_="wb-data-list")

    for tr in lis:
        try:
            href = tr.div.a['href']
            name = tr.div.a['title']
            ggstart_time = tr.span.get_text().strip(']').strip('[')
        except:
            continue
        if 'http' in href:
            href = href
        else:
            href = "http://ggj.chizhou.gov.cn"+href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"] = None
    return df



def f2(driver):
    locator = (By.XPATH, '//li[@class="wb-data-list"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath('//td[@class="huifont"]').text
    total = re.findall('/(\d+)', total)[0]
    total = int(total)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               '/html/body')

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    html=driver.page_source
    if '系统发生了错误' in html:

        return '404'

    locator = (By.XPATH, '//div[contains(@id,"menutab") and (not(@style) or @style="")][string-length()>10] | //div[@class="ewb-tell-bd"]/table | //*[@id="form1"]/div[4]/div/div[2]/div/table/tbody/tr/td/table')

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
    try:
        div = soup.find('div', class_="ewb-tell-bd").find_all('tr')[2]
    except:
        div = soup.find('div', attrs={'id': re.compile('menutab_6_\d'), 'style': ''})
        if div==None:
            raise ValueError

    return div




def get_data():
    data = []

    # zfcg
    ggtype2 = OrderedDict([("zhaobiao", "001"), ("gqita_da_bian", "004"), ("zhongbiao", "003"), ("liubiao", "007"),('zhaobiao_danyilaiyuan','005')])
    # gcjs
    ggtype1 = OrderedDict([("zhaobiao", "001"), ("zhongbiaohx", "002"), ("zhongbiao", "003"), ("gqita_da_bian", "005"),('yucai','007')])

    ##gcjs_zfcg
    adtype1 = OrderedDict([('市级', '001,1'), ("石台县", "001,2"), ("东至县", "002,3"), ("青阳县", "003,4"),('贵池区','004,5')])

    #gcjs

    for w1 in ggtype1.keys():
        for w2 in adtype1.keys():
            if w2 == '市级':
                href='http://ggj.chizhou.gov.cn/chiztpfront/jyxx/002001/002001{jy}/002001{jy}{dq}/?Paging=1'.format(
                dq=adtype1[w2].split(',')[0], jy=ggtype1[w1])
                tmp = ["gcjs_{0}_diqu{1}_gg".format(w1, adtype1[w2].split(',')[1]), href, ["name", "ggstart_time", "href", 'info'],
                       add_info(f1, {"diqu": w2}), f2]

            else:
                href = "http://ggj.chizhou.gov.cn/chiztpfront/jyxx/002001/002001{jy}/002001{jy}002/002001{jy}002{dq}/?Paging=1".format(
                    dq=adtype1[w2].split(',')[0], jy=ggtype1[w1])
                tmp = ["gcjs_{0}_diqu{1}_gg".format(w1, adtype1[w2].split(',')[1]), href,["name", "ggstart_time", "href", 'info'],
                       add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)

    #zfcg
    for w1 in ggtype2.keys():
        for w2 in adtype1.keys():
            if w2 == '市级':
                href='http://ggj.chizhou.gov.cn/chiztpfront/jyxx/002002/002002{jy}/002002{jy}{dq}/?Paging=1'.format(
                dq=adtype1[w2].split(',')[0], jy=ggtype2[w1])
                tmp = ["zfcg_{0}_diqu{1}_gg".format(w1, adtype1[w2].split(',')[1]), href, ["name", "ggstart_time", "href", 'info'],
                       add_info(f1, {"diqu": w2}), f2]

            else:
                href = "http://ggj.chizhou.gov.cn/chiztpfront/jyxx/002002/002002{jy}/002002{jy}002/002002{jy}002{dq}/?Paging=1".format(
                    dq=adtype1[w2].split(',')[0], jy=ggtype2[w1])
                tmp = ["zfcg_{0}_diqu{1}_gg".format(w1, adtype1[w2].split(',')[1]), href,["name", "ggstart_time", "href", 'info'],
                       add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)


    # remove_arr = [""]
    data1 = data.copy()
    # for w in data:
    #     if w[0] in remove_arr: data1.remove(w)


    return data1


data = get_data()
# pprint(data)



def work(conp,**args):
    est_meta(conp,data=data,diqu="安徽省池州市",**args)
    est_html(conp,f=f3,**args)




if __name__=='__main__':

    work(conp=["postgres", "since2015", "192.168.4.175", "anhui", "chizhou"])
    pass
