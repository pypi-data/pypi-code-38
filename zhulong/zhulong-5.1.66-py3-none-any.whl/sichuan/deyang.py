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
import json
from zhulong.util.etl import add_info,est_meta,est_html,est_tbs
from zhulong.util.fake_useragent import UserAgent

_name_="deyang"



endTime = time.strftime('%Y-%m-%d',time.localtime(time.time()))



def f1(driver, num):
    url = driver.current_url
    menuCode = re.findall(r'menuCode=(.*)', url)[0]
    stsrt_url = url.rsplit('/', maxsplit=1)[0]
    Data = {
        'page': (num-1),
        'time': 'customize',
        'areaCode': '',
        'menuCode': menuCode,
        'menuTypeCode': '',
        'contentTypeCode': '',
        'keyname': '',
        'startTime': '2016-11-28',
        'endTime': endTime,
        'areaCodeFlag': '',
        # '_csrf': '89190fe0-6f2e-434c-b9b2-4b7388910709',
    }
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'User-Agent': user_agent,
    }
    sesion = requests.session()
    res = sesion.post(url=stsrt_url, headers=headers, data=Data)
    # 需要判断是否为登录后的页面
    if res.status_code == 200:
        page = res.text
        if page:
            soup = BeautifulSoup(page, 'html.parser')
            div = soup.find('div', class_="search-result").ul
            lis = div.find_all('li')
            data_list = []
            for li in lis:
                a = li.find('a')
                title = a.text.strip()
                link = 'http://www.dyggzy.com' + a['href'].strip()
                span = li.find('span', class_="time").text.strip()
                try:
                    td = re.findall(r'\[(.*?)\]', title)[0]
                except:
                    td = ''
                p = li.find('p')
                try:
                    yw_type = p.find_all('span')[0].text.strip()
                except:
                    yw_type = ''
                try:
                    xx_type = p.find_all('span')[1].text.strip()
                except:
                    xx_type = ''
                a = {"diqu": td, 'yw_type':yw_type, 'xx_type':xx_type}
                info = json.dumps(a, ensure_ascii=False)
                tmp = [title, span, link, info]
                data_list.append(tmp)
            df = pd.DataFrame(data_list)
            return df


def f2(driver):
    url = driver.current_url
    menuCode = re.findall(r'menuCode=(.*)', url)[0]
    stsrt_url = url.rsplit('/', maxsplit=1)[0]
    Data = {
        'page': 0,
        'time': 'customize',
        'areaCode': '',
        'menuCode': menuCode,
        'menuTypeCode': '',
        'contentTypeCode': '',
        'keyname': '',
        'startTime': '2016-11-28',
        'endTime': endTime,
        'areaCodeFlag': '',
        # '_csrf': '89190fe0-6f2e-434c-b9b2-4b7388910709',
    }
    num = get_pagenum(stsrt_url, Data)
    driver.quit()
    return num



def get_pagenum(stsrt_url, Data):
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'User-Agent': user_agent
        }
    sesion = requests.session()
    res = sesion.post(url=stsrt_url, headers=headers, data=Data)
    # 需要判断是否为登录后的页面
    if res.status_code == 200:
        page = res.text
        if page:
            soup = BeautifulSoup(page, 'html.parser')
            div = soup.find('div', class_="pagenations")
            atrs = div.find_all('span')[0].text.strip()
            num = re.findall(r'共(\d+)页', atrs)[0]
            return int(num)





def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='detail-box'][string-length()>40]")
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
    div = soup.find('div', class_="detail-box")
    return div


data = [
    ["gcjs_gqita_gg",
     "http://ggzyxx.deyang.gov.cn/pub/showJyxxContent/menuCode=JYGCJS",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_gg",
     "http://ggzyxx.deyang.gov.cn/pub/showJyxxContent/menuCode=JYCG",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_gqita_gg",
     "http://ggzyxx.deyang.gov.cn/pub/showJyxxContent/menuCode=JYSSGQY",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'jylx':'市属国企'}), f2],

    ["jqita_gqita_gg",
     "http://ggzyxx.deyang.gov.cn/pub/showJyxxContent/menuCode=JYQT",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'其他交易'}), f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="四川省德阳市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","sichuan","deyang"])


