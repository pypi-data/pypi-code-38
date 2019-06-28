import json
import math
import random

import pandas as pd
import re

import requests
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


from zhulong.util.etl import gg_meta,gg_html,est_meta,est_html
from zhulong.util.fake_useragent import UserAgent

_name_="lanzhou"



def f1(driver,num):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        if proxies_chromeOptions:
            proxy = proxies_chromeOptions[0].split('=')[1]
            proxies = {'http': '%s' % proxy}
        else:
            proxies = {}
    except:
        proxies = {}

    ua=UserAgent()
    url=driver.current_url
    categorynum=re.findall('/(\d+?)/moreinfojyxx',url)[0]

    form_data = {

        "categorynum": categorynum,
        "citycode": "all",
        "pageIndex": num,
        "pageSize": 15,

    }

    headers = {

        "Referer": url,
        "User-Agent": ua.chrome}

    req_url='http://lzggzyjy.lanzhou.gov.cn/EpointWebBuilder/xxlistSearchAction.action?cmd=initPageList'

    time.sleep(0.5 + random.random())
    req = requests.post(req_url, data=form_data, headers=headers,proxies=proxies ,timeout=40)

    if req.status_code != 200:
        raise ValueError('response status_code is %s'%req.status_code)
    content=req.content.decode('unicode_escape')

    content=re.findall('"Table" :\[(.+?)\]}',content)[0]

    contents=re.findall("(\{.+?\})[,']",content)
    data=[]
    for c in contents:
        c=json.loads(c)
        href=c['infoid']
        name=c['title2']
        ggstart_time=c['infodate']
        diqu=c['cityname']
        data_cate=c['categorynum']
        if diqu == '市本级':
            url_d='jygk'
        else:
            url_d='xqfzx'

        href = '/'.join(['http://lzggzyjy.lanzhou.gov.cn',url_d, data_cate[:6],
                         data_cate, ggstart_time.replace('-', ''),href + '.html'])
        info = json.dumps({'diqu':diqu},ensure_ascii=False)
        tmp=[name,ggstart_time,href,info]

        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df

def f2(driver):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        if proxies_chromeOptions:
            proxy = proxies_chromeOptions[0].split('=')[1]
            proxies = {'http': '%s' % proxy}
        else:
            proxies = {}
    except:
        proxies = {}

    ua = UserAgent()

    url = driver.current_url
    categorynum = re.findall('/(\d+?)/moreinfojyxx', url)[0]


    form_data = {

        "categorynum": categorynum,
        "citycode": "all",
        "pageIndex": 1,
        "pageSize": 15,
    }

    headers = {
        "Referer": url,
        "User-Agent": ua.chrome}

    req_url = 'http://lzggzyjy.lanzhou.gov.cn/EpointWebBuilder/xxlistSearchAction.action?cmd=initPageCount'

    req = requests.post(req_url, data=form_data, headers=headers,proxies=proxies, timeout=40)
    if req.status_code != 200:
        raise ValueError('response status_code is %s' % req.status_code)

    total=json.loads(req.text)
    total=math.ceil(int(total.get('custom'))/15)

    driver.quit()
    return total



def f3(driver,url):


    driver.get(url)

    locator=(By.XPATH,'//div[@class="ewb-flow"]/div[@data-role="body"]/div[@class=""][string-length()>100] | '
                      '//div[@class="ewb-flow"]/div[@data-role="body"]/div[not(contains(@class,"hidden"))][string-length()>50] | '
                      '//div[@class="ewb-main"][string-length()>50]')

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

    div=soup.find('div',class_='ewb-flow').find('div',attrs={"data-role":"body"}).find('div',class_="",recursive=False)
    if div == None:
        div=soup.find('div',class_='ewb-flow').find('div',attrs={"data-role":"body"})
        divs=div.find_all('div',class_=re.compile('hidden'),recursive=False)
        for i in divs:
            i.extract()

        if div ==None:
            div=soup.find('div',class_='ewb-main')

    return div


data=[

        ["gcjs_zhaobiao_gg","http://lzggzyjy.lanzhou.gov.cn/jygk/002001/002001001/moreinfojyxx.html",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_biangeng_gg","http://lzggzyjy.lanzhou.gov.cn/jygk/002001/002001002/moreinfojyxx.html",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zhongbiaohx_gg","http://lzggzyjy.lanzhou.gov.cn/jygk/002001/002001003/moreinfojyxx.html",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zhongbiao_gg","http://lzggzyjy.lanzhou.gov.cn/jygk/002001/002001004/moreinfojyxx.html",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zgys_gg","http://lzggzyjy.lanzhou.gov.cn/jygk/002001/002001005/moreinfojyxx.html",["name","ggstart_time","href","info"],f1,f2],


        ["zfcg_zhaobiao_gg","http://lzggzyjy.lanzhou.gov.cn/jygk/002002/002002001/moreinfojyxx.html",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_biangeng_gg","http://lzggzyjy.lanzhou.gov.cn/jygk/002002/002002002/moreinfojyxx.html",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_zhongbiao_gg","http://lzggzyjy.lanzhou.gov.cn/jygk/002002/002002003/moreinfojyxx.html",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_zhaobiao_zb1_gg","http://lzggzyjy.lanzhou.gov.cn/jygk/002002/002002004/moreinfojyxx.html",["name","ggstart_time","href","info"],f1,f2],

    ]

def work(conp,**args):
    est_meta(conp,data=data,diqu="甘肃省兰州市",**args)
    est_html(conp,f=f3,**args)


if __name__=="__main__":
    # work(conp=["postgres","since2015",'192.168.3.171',"gansu","lanzhou"],num=1,headless=True,total=3,html_total=10)
    driver=webdriver.Chrome()
    url='http://lzggzyjy.lanzhou.gov.cn/xqfzx/014002/014002001/20190131/cd4bc553-d73b-40d3-91ea-e6e2550dd879.html'
    f3(driver,url)
    pass
