
# coding=utf-8
import pandas as pd
import re

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
from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html, est_tbs, add_info

_name_="shenghui2"


def f1(driver,num):

    locator=(By.XPATH,'//div[@class="list_all_style_1"]/div[1]/p')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum = int(re.findall('queryContent_(\d+)',url)[0])
    if cnum != num:
        val=driver.find_element_by_xpath('//div[@class="list_all_style_1"]/div[1]').get_attribute('onclick')
        url=re.sub("queryContent_\d+","queryContent_%s"%num,url)
        driver.get(url)
        locator=(By.XPATH,"//div[@class='list_all_style_1']/div[1][not(contains(@href,'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    page=driver.page_source
    soup=BeautifulSoup(page,"html.parser")
    ul=soup.find('div',class_="list_all_style_1")
    lis=ul.find_all("div")
    data=[]
    for div in lis:
        href=div['onclick']
        name=div.find('span',class_='zdddd').get_text().strip()
        ggstart_time=div.find_all('span')[-1].get_text().strip()
        href=re.findall('http:.+jhtml',href)[0]

        tmp=[name,href,ggstart_time]

        data.append(tmp)
    df=pd.DataFrame(data=data)
    df['info']=None
    return df

def f2(driver):
    locator=(By.XPATH,'//div[@class="list_all_style_1"]/div[1]/p')
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))


    atext=driver.find_element_by_xpath("//ul[@class='pages-list']/li[1]/a").text
    rr=re.compile("/(\d+)页")
    total=int(rr.findall(atext)[0])

    driver.quit()

    return total
def f3(driver,url):

    driver.get(url)


    locator=(By.XPATH,'//div[@class="news_content"][string-length()>100]')

    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

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

    div=soup.find('div',class_='news_content')
    return div

data=[
["gcjs_zhaobiao_gg","http://ggzy.guizhou.gov.cn/queryContent_1-jyxx.jspx?channelId=81",["name","href","ggstart_time","info"],f1,f2],
["gcjs_kongzhijia_gg","http://ggzy.guizhou.gov.cn/queryContent_1-jyxx.jspx?channelId=123",["name","href","ggstart_time","info"],f1,f2],
["gcjs_zhongbiaohx_gg","http://ggzy.guizhou.gov.cn/queryContent_1-jyxx.jspx?channelId=83",["name","href","ggstart_time","info"],f1,f2],
["gcjs_liubiao_gg","http://ggzy.guizhou.gov.cn/queryContent_1-jyxx.jspx?channelId=124",["name","href","ggstart_time","info"],f1,f2],
["gcjs_zgysjg_gg","http://ggzy.guizhou.gov.cn/queryContent_1-jyxx.jspx?channelId=85",["name","href","ggstart_time","info"],f1,f2],
["gcjs_gqita_da_bian_gg","http://ggzy.guizhou.gov.cn/queryContent_1-jyxx.jspx?channelId=84",["name","href","ggstart_time","info"],f1,f2],
["gcjs_gqita_zhengming_gg","http://ggzy.guizhou.gov.cn/queryContent_1-jyxx.jspx?channelId=186",["name","href","ggstart_time","info"],add_info(f1,{"gclx":"交易证明书"}),f2],


["zfcg_gqita_zhengming_gg","http://ggzy.guizhou.gov.cn/queryContent_1-jyxx.jspx?channelId=187",["name","href","ggstart_time","info"],add_info(f1,{"gclx":"交易证明书"}),f2],
["zfcg_zhaobiao_gg","http://ggzy.guizhou.gov.cn/queryContent_1-jyxx.jspx?channelId=86",["name","href","ggstart_time","info"],f1,f2],
["zfcg_zgysjg_gg","http://ggzy.guizhou.gov.cn/queryContent_1-jyxx.jspx?channelId=176",["name","href","ggstart_time","info"],f1,f2],
["zfcg_zhongbiao_gg","http://ggzy.guizhou.gov.cn/queryContent_1-jyxx.jspx?channelId=87",["name","href","ggstart_time","info"],f1,f2],
["zfcg_liubiao_gg","http://ggzy.guizhou.gov.cn/queryContent_1-jyxx.jspx?channelId=88",["name","href","ggstart_time","info"],f1,f2],
["zfcg_gqita_da_bian_gg","http://ggzy.guizhou.gov.cn/queryContent_1-jyxx.jspx?channelId=90",["name","href","ggstart_time","info"],f1,f2],



]

def work(conp,**args):
    est_meta(conp,data=data,diqu="贵州省省会",**args)

    est_html(conp,f=f3,**args)
if __name__ == '__main__':

    work(conp=["postgres","since2015","192.168.3.171","guizhou","shenghui"],pageloadstrategy='none')