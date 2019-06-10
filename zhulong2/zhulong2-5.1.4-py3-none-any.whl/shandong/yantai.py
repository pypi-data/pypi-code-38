import random
import time

import pandas as pd
import re
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from zhulong2.util.fake_useragent import UserAgent

from zhulong2.util.etl import est_meta, est_html, add_info, est_gg

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]

#
# url="http://cgb.yantai.gov.cn/col/col12525/index.html?uid=8972&pageNum=1"
# driver=webdriver.Chrome()
# # driver.minimize_window()
# driver.maximize_window()
# driver.get(url)

_name_='shandong_yantai'


def f1(driver,num):
    proxies_data = webdriver.DesiredCapabilities.CHROME
    proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
    if proxies_chromeOptions:
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    else:
        proxies = {}

    num=pow(2,num-1)

    ua=UserAgent()
    locator = (By.XPATH, '//div[@class="default_pgContainer"]//li[1]/a')
    WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))
    url = driver.current_url

    columnid=re.findall('col/col(\d+?)/',url)[0]
    unitid=re.findall('uid=(\d+?)&',url)[0]

    cookies = driver.get_cookies()
    COOKIES = {}
    for cookie in cookies:
        COOKIES[cookie['name']] = cookie['value']


    headers={
        "Referer": url,
        "User-Agent": ua.chrome,
    }

    form_data={

    "col": 1,
    "appid": 1,
    "webid": 89,
    "path": "/",
    "columnid": columnid,
    "sourceContentType": 1,
    "unitid": unitid,
    "webname": "烟台市政府采购网",
    "permissiontype": 0

    }

    startrecord=(num-1)*150+1
    endrecord=num*150

    req_url='http://cgb.yantai.gov.cn/module/web/jpage/dataproxy.jsp?startrecord={}&endrecord={}&perpage=50'.format(startrecord,endrecord)


    time.sleep(random.random()+1)
    req=requests.post(req_url,data=form_data,headers=headers,cookies=COOKIES,proxies=proxies,timeout=120)
    if req.status_code != 200:
        raise ValueError('Error response status_code %s'%req.status_code)
    data=[]
    content_text=req.text
    contents=re.findall('<record>.*?</record>',content_text)
    for content in contents:

        href=re.findall("href=\'(.+?)\'",content)[0]
        if 'http' in href:
            href=href
        else:
            href="http://cgb.yantai.gov.cn"+href

        name=re.findall("title=\'(.+?)\'",content)[0]
        ggstart_time=re.findall("<span class=\'bt_time\'>(.+?)</span>",content)[0]
        tmp=[name,ggstart_time,href]

        data.append(tmp)

    df=pd.DataFrame(data=data)
    df["info"] = None

    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="default_pgContainer"]//li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = int(driver.find_element_by_xpath('//span[@class="default_pgTotalRecord"]').text.strip())

    total=total//150 if total % 150 == 0 else total // 150 + 1

    list_=np.logspace(0, 12, 13, base=2).tolist()

    num_list=[]
    for num in range(1,total+1):
        if num in list_:
            num_list.append(num)
    total=int(len(num_list))

    driver.quit()
    return total

def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@id="zoom"][string-length()>10]')

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
    div = soup.find('div', id="zoom")

    return div


data=[

    ["zfcg_zhaobiao_diqu1_gg","http://cgb.yantai.gov.cn/col/col12525/index.html?uid=8972&pageNum=1",["name","ggstart_time","href",'info'],add_info(f1,{"diqu":"市本级"}),f2],
    ["zfcg_yucai_diqu1_gg","http://cgb.yantai.gov.cn/col/col12530/index.html?uid=35897&pageNum=1",["name","ggstart_time","href",'info'],add_info(f1,{"diqu":"市本级"}),f2],
    ["zfcg_zhongbiao_diqu1_gg","http://cgb.yantai.gov.cn/col/col12526/index.html?uid=8995&pageNum=1",["name","ggstart_time","href",'info'],add_info(f1,{"diqu":"市本级"}),f2],
    ["zfcg_biangeng_diqu1_gg","http://cgb.yantai.gov.cn/col/col12527/index.html?uid=9018&pageNum=1",["name","ggstart_time","href",'info'],add_info(f1,{"diqu":"市本级"}),f2],
    ["zfcg_yanshou_diqu1_gg","http://cgb.yantai.gov.cn/col/col12529/index.html?uid=35853&pageNum=1",["name","ggstart_time","href",'info'],add_info(f1,{"diqu":"市本级"}),f2],

    ["zfcg_yucai_diqu2_gg","http://cgb.yantai.gov.cn/col/col14667/index.html?uid=36261&pageNum=1",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_zhongbiao_diqu2_gg","http://cgb.yantai.gov.cn/col/col14663/index.html?uid=36256&pageNum=1",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_biangeng_diqu2_gg","http://cgb.yantai.gov.cn/col/col14664/index.html?uid=36257&pageNum=1",["name","ggstart_time","href",'info'],f1,f2],
    ["zfcg_yanshou_diqu2_gg","http://cgb.yantai.gov.cn/col/col14666/index.html?uid=36260&pageNum=1",["name","ggstart_time","href",'info'],f1,f2],

    ####一次请求整个区县招标数量太大,无法请求,需拆分成县区
    ["zfcg_zhaobiao_diqu3_gg","http://cgb.yantai.gov.cn/col/col12531/index.html?uid=9401&pageNum=1",["name","ggstart_time","href",'info'],add_info(f1,{"diqu":"芝罘区"}),f2],
    ["zfcg_zhaobiao_diqu4_gg","http://cgb.yantai.gov.cn/col/col12537/index.html?uid=9401&pageNum=1",["name","ggstart_time","href",'info'],add_info(f1,{"diqu":"莱山区"}),f2],
    ["zfcg_zhaobiao_diqu5_gg","http://cgb.yantai.gov.cn/col/col12543/index.html?uid=9401&pageNum=1",["name","ggstart_time","href",'info'],add_info(f1,{"diqu":"福山区"}),f2],
    ["zfcg_zhaobiao_diqu6_gg","http://cgb.yantai.gov.cn/col/col12549/index.html?uid=9401&pageNum=1",["name","ggstart_time","href",'info'],add_info(f1,{"diqu":"牟平区"}),f2],
    ["zfcg_zhaobiao_diqu7_gg","http://cgb.yantai.gov.cn/col/col12555/index.html?uid=9401&pageNum=1",["name","ggstart_time","href",'info'],add_info(f1,{"diqu":"开发区"}),f2],
    ["zfcg_zhaobiao_diqu8_gg","http://cgb.yantai.gov.cn/col/col12561/index.html?uid=9401&pageNum=1",["name","ggstart_time","href",'info'],add_info(f1,{"diqu":"高新区"}),f2],
    ["zfcg_zhaobiao_diqu9_gg","http://cgb.yantai.gov.cn/col/col12567/index.html?uid=9401&pageNum=1",["name","ggstart_time","href",'info'],add_info(f1,{"diqu":"蓬莱区"}),f2],
    ["zfcg_zhaobiao_diqu10_gg","http://cgb.yantai.gov.cn/col/col12573/index.html?uid=9401&pageNum=1",["name","ggstart_time","href",'info'],add_info(f1,{"diqu":"龙口市"}),f2],
    ["zfcg_zhaobiao_diqu11_gg","http://cgb.yantai.gov.cn/col/col12579/index.html?uid=9401&pageNum=1",["name","ggstart_time","href",'info'],add_info(f1,{"diqu":"莱州区"}),f2],
    ["zfcg_zhaobiao_diqu12_gg","http://cgb.yantai.gov.cn/col/col12585/index.html?uid=9401&pageNum=1",["name","ggstart_time","href",'info'],add_info(f1,{"diqu":"招远市"}),f2],
    ["zfcg_zhaobiao_diqu13_gg","http://cgb.yantai.gov.cn/col/col12591/index.html?uid=9401&pageNum=1",["name","ggstart_time","href",'info'],add_info(f1,{"diqu":"栖霞区"}),f2],
    ["zfcg_zhaobiao_diqu14_gg","http://cgb.yantai.gov.cn/col/col12598/index.html?uid=9401&pageNum=1",["name","ggstart_time","href",'info'],add_info(f1,{"diqu":"莱阳市"}),f2],
    ["zfcg_zhaobiao_diqu15_gg","http://cgb.yantai.gov.cn/col/col12604/index.html?uid=9401&pageNum=1",["name","ggstart_time","href",'info'],add_info(f1,{"diqu":"海阳市"}),f2],
    ["zfcg_zhaobiao_diqu16_gg","http://cgb.yantai.gov.cn/col/col12610/index.html?uid=9401&pageNum=1",["name","ggstart_time","href",'info'],add_info(f1,{"diqu":"长岛县"}),f2],
    ["zfcg_zhaobiao_diqu17_gg","http://cgb.yantai.gov.cn/col/col12621/index.html?uid=9401&pageNum=1",["name","ggstart_time","href",'info'],add_info(f1,{"diqu":"保税港区"}),f2],
    ["zfcg_zhaobiao_diqu18_gg","http://cgb.yantai.gov.cn/col/col12627/index.html?uid=9401&pageNum=1",["name","ggstart_time","href",'info'],add_info(f1,{"diqu":"昆嵛山"}),f2],
    ["zfcg_zhaobiao_diqu19_gg","http://cgb.yantai.gov.cn/col/col12633/index.html?uid=9401&pageNum=1",["name","ggstart_time","href",'info'],add_info(f1,{"diqu":"东部新区"}),f2],



]

def work(conp,**args):
    est_meta(conp,data=data,diqu="山东省烟台市",**args)
    est_html(conp,f=f3,**args)




if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","lch","shandong_yantai"]

    work(conp=conp,cdc_total=2,headless=False,num=1)