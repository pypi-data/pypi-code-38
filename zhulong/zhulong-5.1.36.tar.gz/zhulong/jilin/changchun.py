import math
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

from zhulong.util.etl import est_tbs,est_meta,est_html, gg_existed,add_info,est_gg
from zhulong.util.conf import get_conp
# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

# #
# url="http://www.ccggzy.gov.cn/sjxxgk/002001/002001004/CityZfcgNotice.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)
# #

_name_='changchun'


def f1(driver,num):

    locator = (By.XPATH, '//body/pre[string-length()>50]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum=re.findall('pageIndex=(\d+?)&',url)[0]

    if cnum != str(num):
        val = len(driver.find_element_by_xpath('//body/pre').text)

        url=re.sub('pageIndex=\d+?&','pageIndex=%s&'%num,url)
        driver.get(url)
        locator = (By.XPATH, '//body/pre[string-length() != %s and string-length()>50]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data_ = []
    html = driver.find_element_by_xpath('//body/pre').text
    content = json.loads(html, encoding='utf8')
    contents = json.loads(content['custom'], encoding='utf8')['Table']
    for li in contents:
        jy_type = li.get('jyfl')
        href = li.get('href')
        ggstart_time = li.get('infodate')
        name = li.get('title')
        href = "http://www.ccggzy.gov.cn" + href

        info={"jy_type":jy_type}
        info=json.dumps(info,ensure_ascii=False)
        tmp = [name, ggstart_time, href,info]

        data_.append(tmp)

    df = pd.DataFrame(data=data_)

    return df

def f2(driver):
    url=driver.current_url
    if 'getCityZfcgInfo' in url:
        url=re.sub('getCityZfcgInfo&','getCityZfcgInfoCount&',url)
    else:
        url = re.sub('getCityTradeInfo&', 'getCityTradeInfoCount&', url)
    driver.get(url)
    locator=(By.XPATH,'//body/pre[string-length()>50]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    html=driver.page_source

    total=re.findall('"custom":"(\d+?)"',html)[0]
    count=re.findall('pageSize=(\d+?)&',url)[0]
    total = math.ceil(int(total)/int(count))

    driver.quit()

    return total


def f3(driver, url):

    driver.get(url)

    locator = (By.XPATH, '//div[@class="ewb-text-box"]')

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
    div = soup.find('div',class_='ewb-text-box')
    div.find('div',class_="ewb-source").extract()

    return div




def get_data():
    data2 = []

    #zfcg_quxian
    ggtype1 = OrderedDict([("zhaobiao","001"),("biangeng", "003"), ("zhongbiaohx", "004")])
    #gcjs_quxian_shiji
    ggtype2 = OrderedDict([("zhaobiao","001"),("zhongbiaohx","002"),("biangeng", "003"), ("zhongbiao", "004")])
    #zfcg_shiji
    ggtype3 = OrderedDict([("yucai","002"),("zhaobiao","001"),("biangeng", "003"), ("zhongbiao", "004")])


    ##zfcg_gcjs
    adtype1 = OrderedDict([("南关区","02"),("宽城区","03"),("朝阳区","04"),("二道区","05"),("绿园区","06"),
			("双阳区","12"),("农安县","22"),("九台市","81"),("榆树市","82"),("德惠市","83"),("长春新区","95"),
			("汽车经济技术开发区","96"),("净月旅游开发区","97"),("高新技术开发区","98"),("经济技术开发区","99"),("莲花山区","94")])

    #zfcg_xianqu
    for w1 in ggtype1.keys():
        for w2 in adtype1.keys():
            href = "http://www.ccggzy.gov.cn/ccggzy/getxxgkAction.action?cmd=getCityZfcgInfo&pageIndex=1&pageSize=15&categorynum=003001{jy}&xiaqucode=2201{dq}&jyfl=%E5%85%A8%E9%83%A8".format(dq=adtype1[w2],jy=ggtype1[w1])
            tmp = ["zfcg_%s_diqu%s_gg" % (w1, adtype1[w2]), href, ["name","ggstart_time","href",'info'],
                   add_info(f1, {"diqu": w2}), f2]
            data2.append(tmp)
    #gcjs_xianqu
    for w1 in ggtype2.keys():
        for w2 in adtype1.keys():
            href = "http://www.ccggzy.gov.cn/ccggzy/getxxgkAction.action?cmd=getCityTradeInfo&pageIndex=1&pageSize=16&categorynum=003002{jy}&xiaqucode=2201{dq}".format(dq=adtype1[w2],jy=ggtype2[w1])
            tmp = ["gcjs_%s_diqu%s_gg" % (w1, adtype1[w2]), href, ["name","ggstart_time","href",'info'],
                   add_info(f1, {"diqu": w2}), f2]
            data2.append(tmp)
    #gcjs_shiji
    for w1 in ggtype2.keys():
        href="http://www.ccggzy.gov.cn/ccggzy/getxxgkAction.action?cmd=getCityTradeInfo&pageIndex=1&pageSize=18&categorynum=002002{jy}&xiaqucode=220101".format(jy=ggtype2[w1])
        tmp = ["gcjs_%s_diqu001_gg" % (w1), href, ["name","ggstart_time","href",'info'],
               add_info(f1, {"diqu": "市本级"}), f2]
        data2.append(tmp)

    # zfcg_shiji
    for w1 in ggtype3.keys():
        href = "http://www.ccggzy.gov.cn/ccggzy/getxxgkAction.action?cmd=getCityZfcgInfo&pageIndex=1&pageSize=16&categorynum=002001{jy}&xiaqucode=220101&jyfl=%E5%85%A8%E9%83%A8".format(
            jy=ggtype3[w1])
        tmp = ["zfcg_%s_diqu001_gg" % (w1), href, ["name", "ggstart_time", "href", 'info'],
               add_info(f1, {"diqu": "市本级"}), f2]
        data2.append(tmp)

    data1 = data2.copy()

    # data1.append( )
    return data1

data1=get_data()

# pprint(data)


def work(conp,**args):
    est_meta(conp,data=data1,diqu="吉林省长春市",**args)
    est_html(conp,f=f3,**args)
    # est_gg(conp,diqu="吉林省长春市")



if __name__=='__main__':

    work(conp=["postgres","since2015","192.168.3.171","jilin","changchun"],headless=False,num=1,total=2)
    pass