import json

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
from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html, add_info,est_gg

# driver=webdriver.Chrome()
# url="http://www.bygzjy.cn/f/trade/annogoods/list?selectedProjectType=3"
# driver.get(url)

_name_='baiyin'



def f1(driver, num):
    locator = (By.XPATH, "//div[@class='byTradingDetailMain']//dl[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//ul[@class='pagination pagination-outline']/li[@class='paginate_button active']/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = int(driver.find_element_by_xpath("//li[@class='paginate_button active']/a").text)
    if cnum != num:
        page_count = len(driver.page_source)
        val = driver.find_element_by_xpath('//div[@class="byTradingDetailMain"]//dl[1]//a').get_attribute('href')
        val = re.findall(r'/f/(.+)$', val)[0]
        driver.execute_script("page(%d,20,'');" % num)

        locator = (
            By.XPATH, "//div[@class='byTradingDetailMain']//dl[1]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        WebDriverWait(driver, 10).until(lambda driver: len(driver.page_source) != page_count)
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find("div", class_="byTradingDetailMain")
    dls = div.find_all("dl")
    data = []
    for dl in dls:
        name = dl.find('a').get_text().strip().replace('\t', '').replace('\n', '').replace(' ', '')
        href = dl.find('a')['href']
        ggstart_time = dl.find('span', class_='byTradingDetailTime').get_text()
        if 'http' in href:
            href = href
        else:
            href = 'http://ggzyjy.baiyin.gov.cn' + href
        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='byTradingDetailMain']//dl[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//ul[@class='pagination pagination-outline']/li[@class='paginate_button active']/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        total = int(driver.find_element_by_xpath('//li[@class="paginate_button "][last()]/a').text)
    except:
        total = 1
    driver.quit()

    return total


def f3_wait(driver):

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



def f3(driver,url):
    driver.get(url)
    locator=(By.XPATH,'//div[@class="jxTradingMainLayer clear"][string-length()>100] | //div[@id="content"][string-length()>50]')
    WebDriverWait(driver,10).until(EC.presence_of_all_elements_located(locator))

    f3_wait(driver)

    ##f3 情况1
    page=driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div=soup.find('div',class_='jxTradingMainLayer clear')
    if not div:
        div=soup.find('div',id="content")

    return div

data=[
    #新交易

        ["gcjs_zhaobiao_shizheng_gg","http://ggzyjy.baiyin.gov.cn/f/newtrade/annogoods/list?selectedProjectType=1&index=1",["name","ggstart_time","href","info"],add_info(f1,{'gclx':"房建市政"}),f2],
        ["gcjs_zhaobiao_jiaotong_gg","http://ggzyjy.baiyin.gov.cn/f/newtrade/annogoods/list?selectedProjectType=2&index=1",["name","ggstart_time","href","info"],add_info(f1,{'gclx':"交通水利"}),f2],
        ["zfcg_zhaobiao_gg","http://ggzyjy.baiyin.gov.cn/f/newtrade/annogoods/list?selectedProjectType=3&index=1",["name","ggstart_time","href","info"],f1,f2],

        ["yiliao_zhaobiao_gg","http://ggzyjy.baiyin.gov.cn/f/newtrade/annogoods/list?selectedProjectType=5",["name","ggstart_time","href","info"],f1,f2],
        ["gcjs_zhaobiao_xiane_gg","http://ggzyjy.baiyin.gov.cn/f/newtrade/annogoods/list?selectedProjectType=8",["name","ggstart_time","href","info"],add_info(f1,{'zbfs':"限额以下"}),f2],
        ["zfcg_zhaobiao_xiane_gg","http://ggzyjy.baiyin.gov.cn/f/newtrade/annogoods/list?selectedProjectType=9",["name","ggstart_time","href","info"],add_info(f1,{'zbfs':"限额以下"}),f2],

        ["gcjs_zhongbiaohx_shizheng_gg","http://ggzyjy.baiyin.gov.cn/f/newtrade/annogoods/list?selectedProjectType=1&index=3",["name","ggstart_time","href","info"],add_info(f1,{'gclx':"房建市政"}),f2],

        ["gcjs_zhongbiaohx_jiaotong_gg","http://ggzyjy.baiyin.gov.cn/f/newtrade/annogoods/list?selectedProjectType=2&index=3",["name","ggstart_time","href","info"],add_info(f1,{'gclx':"交通水利"}),f2],

        ["zfcg_zhongbiaohx_gg","http://ggzyjy.baiyin.gov.cn/f/newtrade/annogoods/list?selectedProjectType=3&index=3",["name","ggstart_time","href","info"],f1,f2],
        ["zfcg_zgysjg_gg","http://ggzyjy.baiyin.gov.cn/f/newtrade/annogoods/list?selectedProjectType=3&index=2",["name","ggstart_time","href","info"],f1,f2],

        ["yiliao_zhongbiaohx_gg","http://ggzyjy.baiyin.gov.cn/f/newtrade/annogoods/list?selectedProjectType=5&index=3",["name","ggstart_time","href","info"],f1,f2],
        ["gcjs_zhongbiaohx_xiane_gg","http://ggzyjy.baiyin.gov.cn/f/newtrade/annogoods/list?selectedProjectType=8&index=3",["name","ggstart_time","href","info"],add_info(f1,{'zbfs':"限额以下"}),f2],
        ["zfcg_zhongbiaohx_xiane_gg","http://ggzyjy.baiyin.gov.cn/f/newtrade/annogoods/list?selectedProjectType=9&index=3",["name","ggstart_time","href","info"],add_info(f1,{'zbfs':"限额以下"}),f2],


    #交易
        ["gcjs_zhaobiao_shizheng_gg","http://ggzyjy.baiyin.gov.cn/f/trade/annogoods/list?selectedProjectType=1",["name","ggstart_time","href","info"],add_info(f1,{'gclx':"房建市政"}),f2],

        ["gcjs_zhaobiao_jiaotong_gg","http://ggzyjy.baiyin.gov.cn/f/trade/annogoods/list?selectedProjectType=2",["name","ggstart_time","href","info"],add_info(f1,{'gclx':"交通水利"}),f2],

        ["zfcg_zhaobiao_gg","http://ggzyjy.baiyin.gov.cn/f/trade/annogoods/list?selectedProjectType=3",["name","ggstart_time","href","info"],f1,f2],

        ["yiliao_zhaobiao_gg","http://ggzyjy.baiyin.gov.cn/f/trade/annogoods/list?selectedProjectType=5",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zhongbiaohx_shizheng_gg","http://ggzyjy.baiyin.gov.cn/f/trade/annogoods/list?selectedProjectType=1&index=3",["name","ggstart_time","href","info"],add_info(f1,{'gclx':"房建市政"}),f2],
        ["gcjs_zgysjg_shizheng_gg","http://ggzyjy.baiyin.gov.cn/f/trade/annogoods/list?selectedProjectType=1&index=2",["name","ggstart_time","href","info"],add_info(f1,{'gclx':"房建市政"}),f2],

        ["gcjs_zhongbiaohx_jiaotong_gg","http://ggzyjy.baiyin.gov.cn/f/trade/annogoods/list?selectedProjectType=2&index=3",["name","ggstart_time","href","info"],add_info(f1,{'gclx':"交通水利"}),f2],
        ["gcjs_zgysjg_jiaotong_gg","http://ggzyjy.baiyin.gov.cn/f/trade/annogoods/list?selectedProjectType=2&index=2",["name","ggstart_time","href","info"],add_info(f1,{'gclx':"交通水利"}),f2],

        ["zfcg_zhongbiaohx_gg","http://ggzyjy.baiyin.gov.cn/f/trade/annogoods/list?selectedProjectType=3&index=3",["name","ggstart_time","href","info"],f1,f2],
        ["zfcg_zgysjg_gg","http://ggzyjy.baiyin.gov.cn/f/trade/annogoods/list?selectedProjectType=3&index=2",["name","ggstart_time","href","info"],f1,f2],

        ["yiliao_zhongbiaohx_gg","http://ggzyjy.baiyin.gov.cn/f/trade/annogoods/list?selectedProjectType=5&index=3",["name","ggstart_time","href","info"],f1,f2],


    ]


## f3 为全流程

def work(conp,**args):
    est_meta(conp,data=data,diqu="甘肃省白银市",**args)
    est_html(conp,f=f3,**args)
    # est_gg(conp=conp,diqu="甘肃省白银市")



if __name__=="__main__":
    work(conp=["postgres","since2015",'192.168.3.171',"gansu","baiyin"],headless=False,num=1,total=2)
