
# coding=utf-8
import math

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
from selenium.webdriver.support.select import Select
import sys
import time

import json
from zhulong.util.etl import gg_meta,gg_html,est_meta,est_html,est_tbs


_name_="liupanshui"

def f1(driver,num):

    locator=(By.XPATH,'//ul[@class="erul"]/li[1]//a')
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    cnum=int(driver.find_element_by_xpath('//li[@class="selected"]/a').text.strip())
    if cnum != num:
        val=driver.find_element_by_xpath('//ul[@class="erul"]/li[1]//a').get_attribute('href')[-20:]

        driver.execute_script("submitFrom('index_%s.jhtml')"%num)

        locator=(By.XPATH,"//ul[@class='erul']/li[1]//a[not(contains(@href,'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    page=driver.page_source
    soup=BeautifulSoup(page,"html.parser")
    ul=soup.find('ul',class_="erul")
    lis=ul.find_all("li")
    data=[]
    for i in range(len(lis)):
        li=lis[i]
        name=li.find('a').get_text().strip()
        ggstart_time=li.find('p',class_='lip3').get_text()

        driver.find_element_by_xpath('//ul[@class="erul"]/li[%s]//a'%(i+1)).click()
        hands=driver.window_handles
        driver.switch_to.window(hands[1])
        WebDriverWait(driver, 10).until(lambda driver:'http://ggzy.gzlps.gov.cn' in driver.current_url)
        href=driver.current_url
        driver.close()
        driver.switch_to.window(hands[0])
        time.sleep(0.1)

        tmp=[name,href,ggstart_time]

        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df


def f2(driver):
    locator=(By.XPATH,"//ul[@class='erul']/li[1]//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    atext=driver.find_element_by_xpath('//a[@id="last"]').get_attribute('onclick')
    total=re.findall("submitFrom\('index_(\d+).jhtml'",atext)[0]
    total=math.ceil(int(total)/10)

    driver.quit()

    return total
def f3(driver,url):

    driver.get(url)


    locator=(By.XPATH,'//div[@class="article"][string-length()>100]')
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

    div=soup.find('div',class_="article")
    return div

data=[
["gcjs_zhaobiao_gg","http://ggzy.gzlps.gov.cn/jyxxgcgg/index_1.jhtml",["name","href","ggstart_time","info"],f1,f2],
["gcjs_zhongbiao_gg","http://ggzy.gzlps.gov.cn/jyxxgcgs/index_1.jhtml",["name","href","ggstart_time","info"],f1,f2],
["gcjs_liubiao_gg","http://ggzy.gzlps.gov.cn/jyxxgclc/index_1.jhtml",["name","href","ggstart_time","info"],f1,f2],
["gcjs_zgysjg_gg","http://ggzy.gzlps.gov.cn/jyxxgczs/index_1.jhtml",["name","href","ggstart_time","info"],f1,f2],
["gcjs_gqita_da_bian_gg","http://ggzy.gzlps.gov.cn/jyxxgcxm/index_1.jhtml",["name","href","ggstart_time","info"],f1,f2],


["zfcg_zhaobiao_gg","http://ggzy.gzlps.gov.cn/jyxxzccg/index_1.jhtml",["name","href","ggstart_time","info"],f1,f2],
["zfcg_biangeng_gg","http://ggzy.gzlps.gov.cn/jyxxzcgz/index_1.jhtml",["name","href","ggstart_time","info"],f1,f2],
["zfcg_zhongbiao_gg","http://ggzy.gzlps.gov.cn/jyxxzczb/index_1.jhtml",["name","href","ggstart_time","info"],f1,f2],
["zfcg_liubiao_gg","http://ggzy.gzlps.gov.cn/jyxxzcfb/index_1.jhtml",["name","href","ggstart_time","info"],f1,f2],
["zfcg_zgys_gg","http://ggzy.gzlps.gov.cn/jyxxzczs/index_1.jhtml",["name","href","ggstart_time","info"],f1,f2]

]

def work(conp,**args):
   est_meta(conp,data=data,diqu="贵州省六盘水市",**args)

   est_html(conp,f=f3,**args)

if __name__ == '__main__':

    work(conp=["postgres","since2015","192.168.3.171","guizhou","liupanshui"],pageloadstrategy='none',num=1,headless=False)

