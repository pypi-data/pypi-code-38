import pandas as pd  
import re 
import requests 
from selenium import webdriver 
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 

import json

import time
from zhulong.util.fake_useragent import UserAgent
from zhulong.util.etl import est_html,est_meta ,add_info
_name_="zhanjiang"


def re_data(url,num,proxies):
    url_dict={
    "http://www.zjprtc.com/JSGC/ZBGGList.html?moduletype=5&subtype=1":
    ["http://www.zjprtc.com/jsgc_Message/queryPaginationBysearchText.do?areaType=9",'zhaoBiaoGongGaoGUID'
    ,'http://www.zjprtc.com/JSGC/JSGC_ZhaoBiao_GongGao_View.html?moduletype=5&guid=xxxx-guid&subtype=1'],

    "http://www.zjprtc.com/JSGC/JSGC_PBJGGSList.html?moduletype=5&subtype=24":
    ["http://www.zjprtc.com/jsgc_Message/queryPaginationJieGuoGongGaoysearchText.do?areaType=9",'jieGuoGongGaoGUID',
    'http://www.zjprtc.com/JSGC/JSGC_PingBiaoJieGuo_View.html?moduletype=5&guid=xxxx-guid&subtype=24'
    ],

    "http://www.zjprtc.com/JSGC/JSGC_GZGGList.html?moduletype=5&subtype=2":
    ["http://www.zjprtc.com/jsgc_Message/queryPaginationBuYiJiLuBysearchText.do?areaType=9",'buYiJiLuGUID',
    'http://www.zjprtc.com/JSGC/JSGC_GZGGView.html?moduletype=5&guid=xxxx-guid&subtype=2'
    ],

    "http://www.zjprtc.com/Jyweb/ZFCG_JYXTList.html?moduletype=5&subtype=12":
    ["http://www.zjprtc.com/zfcg_Message/queryPaginationBysearchText.do?areaType=9",'zhaoBiaoGongGaoGUID',
    'http://www.zjprtc.com/Jyweb/ZFCG_ZhaoBiao_GongGao_View.html?moduletype=5&guid=xxxx-guid&subtype=12'
    ],

    "http://www.zjprtc.com/Jyweb/ZFCG_GengZhengGongGao_List.html?moduletype=5&subtype=13":
    ["http://www.zjprtc.com/zfcg_Message/queryPaginationBuYiJiLuBysearchText.do?areaType=9",'buYiJiLuGUID',
    'http://www.zjprtc.com/Jyweb/ZFCG_GengZheng_GongGao_View.html?moduletype=5&guid=xxxx-guid&subtype=13'
    ],

    "http://www.zjprtc.com/Jyweb/ZFCG_PingBiaoJieGuo_List.html?moduletype=5&subtype=14":
    ["http://www.zjprtc.com/zfcg_Message/queryPaginationJieGuoGongGaoysearchText.do?areaType=9",'jieGuoGongGaoGUID',
    'http://www.zjprtc.com/Jyweb/ZFCG_PingBiaoJieGuo_View.html?moduletype=5&guid=xxxx-guid&subtype=14'
    ]

    }


    user_agents = UserAgent()
    user_agent = user_agents.chrome
    
    start_url = url_dict[url][0]
    payloadData = {
    "page":num,
    "rows":15

    }
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'User-Agent': user_agent,
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }
    if proxies:
         res = requests.get(url=start_url, headers=headers, params=payloadData,proxies=proxies)
    else:
         res = requests.get(url=start_url, headers=headers, params=payloadData)
   

    rows=res.json()['rows']

    data=[]
    for row in rows:
    #print(row)
        name=row['xiangMuName']
        ggstart_time=row['strFaBuQiShiShiJian']

        guid=row[url_dict[url][1]]
        href=url_dict[url][2].replace('xxxx-guid',guid)
        info=None
        tmp=[name,ggstart_time,href,info]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    return df


def f1(driver,num):

    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s'% proxy}
    except:
        proxies = ''
    url=driver.current_url 

    df=re_data(url,num,proxies)
    return df 

def f2(driver):
    locator=(By.ID,"datagrid")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))


    locator=(By.XPATH,"//div[@class='mmggxlh']//span[contains(string(),'当')]")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    total=int(re.findall("共([0-9]{1,})页" ,driver.find_element_by_xpath("//div[@class='mmggxlh']//span[@class='dian'][3]").text)[0])
    driver.quit()
    return total

def f3(driver,url):

    driver.get(url)

    locator=(By.XPATH,"//div[@id='divContent'][string-length()>30]")



    WebDriverWait(driver,20).until(EC.presence_of_all_elements_located(locator))

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

    div=soup.find('div',id="divContent")
    #div=div.find_all('div',class_='ewb-article')[0]
    
    return div


data=[
        ["gcjs_zhaobiao_gg","http://www.zjprtc.com/JSGC/ZBGGList.html?moduletype=5&subtype=1",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zhongbiao_gg","http://www.zjprtc.com/JSGC/JSGC_PBJGGSList.html?moduletype=5&subtype=24",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_biangeng_gg","http://www.zjprtc.com/JSGC/JSGC_GZGGList.html?moduletype=5&subtype=2",["name","ggstart_time","href","info"],f1,f2],


        ["zfcg_zhaobiao_gg","http://www.zjprtc.com/Jyweb/ZFCG_JYXTList.html?moduletype=5&subtype=12",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_biangeng_gg","http://www.zjprtc.com/Jyweb/ZFCG_GengZhengGongGao_List.html?moduletype=5&subtype=13",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_zhongbiao_gg","http://www.zjprtc.com/Jyweb/ZFCG_PingBiaoJieGuo_List.html?moduletype=5&subtype=14",["name","ggstart_time","href","info"],f1,f2]



    ]



def work(conp,**args):
    est_meta(conp,data=data,diqu="广东省湛江市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","127.0.0.1","guangdong","zhanjiang"],num=20)

# url="http://www.zjprtc.com/JSGC/JSGC_PingBiaoJieGuo_View.html?moduletype=5&guid=99d57294-df52-4ca0-a487-cf8e85aac85f&subtype=24"
# driver=webdriver.Chrome()

# driver.get(url)