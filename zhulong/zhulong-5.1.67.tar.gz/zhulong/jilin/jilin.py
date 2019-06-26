import math
import random
import time
from os.path import join, dirname

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from collections import defaultdict
import json
from fake_useragent import UserAgent


from zhulong.util.etl import est_tbs, est_meta, est_html, gg_existed

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url="http://www.hljcg.gov.cn/xwzs!queryXwxxqx.action?lbbh=42301"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)
# #



_name_='jilin'

def f1(driver, num):

    main_url=driver.current_url
    url = re.sub('&page=(\d+?)&', '&page={}&'.format(num), main_url)

    area_codes = defaultdict(str)
    area_code = {"122201004232188615": "长春市",
             "12220000412759478T": "省本级",
             "1222010056393822XT": "长春市",
             "73700954-4":"省本级",
             "12220100423200207X": "省本级",
             "12220200782609514F": "吉林市",
             "34004150-3": "辽源市",
             "112203007645929828": "四平市",
             "66011618-0": "松原市",
             "122200005740930828": "省本级",
             "73256854-X":"延边州",
             "73256678-X": "通化市",
             "66429601-9": "白城市",
             "12220600737041237Q": "白山市",
             "01382732-2":"长春市",
             "122030000105": "四平市",
             "41270618-1":"四平市",
             "112203000135292377":"四平市",
             "112203000135298353": "四平市",
             "11220300413126808N": "四平市",
             "112200007710693483": "长白山",
             "11222400MB14602364": "延边州",
             "12220100MB10780025": "长春市",
             "12220500MB1143476B": "通化市",
             "12220800MB11528661": "白城市",
             "12220400412763282Y": "辽源市",
             "12220700MB1837064Y": "松原市",
             "12220300MB0125428T": "四平市",
             }
    area_codes.update(area_code)

    data_ = []

    ua=UserAgent()


    headers={
        "User-Agent": ua.chrome
    }

    time.sleep(random.random())
    req = requests.get(url,headers=headers)
    if req.status_code != 200:
        print(req.status_code)
        raise ValueError

    response = req.text

    datas = re.findall('{"title":.*?"}', response)
    for data in datas:

        name = re.findall('"title":"(.*?)"', data)[0] if re.findall('"title":"(.*?)"', data) else 'null'
        address = re.findall('"area":"(.*?)"', data)[0]
        if address not in area_codes.keys():
            area_codes[address]='吉林省'

        address = area_codes[address]
        ggstart_time = re.findall('"timestamp":"(.*?)"', data)[0]
        href = re.findall('"docpuburl":"(.*?)"', data)[0]

        if 'http' in href:
            href = href
        else:
            href = 'http://www.jl.gov.cn' + href

        info={'diqu':address}
        info=json.dumps(info,ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]

        data_.append(tmp)


    df = pd.DataFrame(data=data_)


    return df


def f2(driver):
    url=driver.current_url
    req=requests.get(url)

    if req.status_code == 200:
        total=int(re.findall('"recordnum":"(\d+)"',req.text)[0])
        total=math.ceil(total/17)
    else:
        raise ValueError

    total = int(total)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="ewb-article"]')

    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

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
    div = soup.find('div', class_="ewb-article-info")

    return div


data = [
    ["gcjs_zhaobiao_gg","http://was.jl.gov.cn/was5/web/search?channelid=237687&page=1&prepage=17&searchword=gtitle%3C%3E%27%27%20and%20gtitle%3C%3E%27null%27%20and%20tType=%27%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE%27%20%20%20and%20iType=%27%E6%8B%9B%E6%A0%87%E5%85%AC%E5%91%8A%27%20%20%20&callback&callback=result",["name","ggstart_time","href","info"],f1,f2],
    ["gcjs_biangeng_gg","http://was.jl.gov.cn/was5/web/search?channelid=237687&page=1&prepage=17&searchword=gtitle%3C%3E%27%27%20and%20gtitle%3C%3E%27null%27%20and%20tType=%27%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE%27%20%20%20and%20iType=%27%E5%8F%98%E6%9B%B4%E5%85%AC%E5%91%8A%E5%B7%A5%E7%A8%8B%27%20%20%20&callback&callback=result",["name","ggstart_time","href","info"],f1,f2],
    ["gcjs_zhongbiao_gg","http://was.jl.gov.cn/was5/web/search?channelid=237687&page=2&prepage=17&searchword=gtitle%3C%3E%27%27%20and%20gtitle%3C%3E%27null%27%20and%20tType=%27%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE%27%20%20%20and%20iType=%27%E4%B8%AD%E6%A0%87%E7%BB%93%E6%9E%9C%E5%85%AC%E5%91%8A%27%20%20%20&callback&callback=result",["name","ggstart_time","href","info"],f1,f2],
    ["gcjs_zhongbiaohx_gg","http://was.jl.gov.cn/was5/web/search?channelid=237687&page=2&prepage=17&searchword=gtitle%3C%3E%27%27%20and%20gtitle%3C%3E%27null%27%20and%20tType=%27%E5%B7%A5%E7%A8%8B%E5%BB%BA%E8%AE%BE%27%20%20%20and%20iType=%27%E4%B8%AD%E6%A0%87%E5%80%99%E9%80%89%E4%BA%BA%E5%85%AC%E7%A4%BA%27%20%20%20&callback&callback=result",["name","ggstart_time","href","info"],f1,f2],

    ["zfcg_zhaobiao_gg","http://was.jl.gov.cn/was5/web/search?channelid=237687&page=1&prepage=17&searchword=gtitle%3C%3E%27%27%20and%20gtitle%3C%3E%27null%27%20and%20tType=%27%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD%27%20and%20iType=%27%E9%87%87%E8%B4%AD%E5%85%AC%E5%91%8A%27%20&callback&callback=result",["name","ggstart_time","href","info"],f1,f2],
    ["zfcg_biangeng_gg","http://was.jl.gov.cn/was5/web/search?channelid=237687&page=1&prepage=17&searchword=gtitle%3C%3E%27%27%20and%20gtitle%3C%3E%27null%27%20and%20tType=%27%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD%27%20and%20iType=%27%E5%8F%98%E6%9B%B4%E5%85%AC%E5%91%8A%27%20&callback&callback=result",["name","ggstart_time","href","info"],f1,f2],
    ["zfcg_zhongbiao_gg", "http://was.jl.gov.cn/was5/web/search?channelid=237687&page=1&prepage=17&searchword=gtitle%3C%3E%27%27%20and%20gtitle%3C%3E%27null%27%20and%20tType=%27%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD%27%20%20and%20iType=%27%E4%B8%AD%E6%A0%87%E5%85%AC%E5%91%8A%27%20%20&callback&callback=result", ["name", "ggstart_time", "href", "info"], f1,f2],

    # 单一性来源无法爬取
    # 医药采购数据太少，未爬取
]

def work(conp,**args):
    est_meta(conp,data=data,diqu="吉林省吉林省",**args)
    est_html(conp,f=f3,**args)

if __name__=='__main__':

    work(conp=["postgres", "since2015", "192.168.3.171", "jilin", "jilin"],headless=False,num=1)