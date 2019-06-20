import json
import random
import time

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
import json
from zhulong2.util.fake_useragent import UserAgent


from zhulong2.util.etl import est_tbs, est_meta, est_html, gg_existed, est_gg, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hefei.gov.cn/jyxx/002001/002001002/moreinfo_jyxx.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)


_name_ = 'fujian_sanming'


def f1(driver, num):
    proxies_data = webdriver.DesiredCapabilities.CHROME
    proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
    if proxies_chromeOptions:
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    else:
        proxies = {}
    ua=UserAgent()
    locator = (By.XPATH, '//div[@id="htcList"]//tr[1]/td[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    time.sleep(0.1)
    url = driver.current_url

    cookies = driver.get_cookies()

    COOKIES = {}

    for i in cookies:
        COOKIES[i['name']] = i['value']

    sid=re.findall('sid=(.+?)&',url)[0]
    cgfs=re.findall('&cgfs=(.+?)&',url)[0]
    level=re.findall('&level=(.+)$',url)[0]


    url2 = 'http://sm.fjzfcg.gov.cn/n/smzfcg/queryPageData.do'
    data = {
        "page": num,
        "rows": 20,
        "sid": sid,
        "level": level,
        "cgfs": cgfs,
    }

    headers={
        "User-Agent": ua.chrome,
        "Referer":url,
    }

    time.sleep(random.random()+1)
    responce = requests.post(url2, data=data,headers=headers,cookies=COOKIES,proxies=proxies,timeout=10)

    if responce.status_code != 200:
        print(responce.status_code)
        raise ValueError

    data_=[]
    req = responce.text

    reqs = json.loads(req)['list']
    for content in reqs:
        name = content['title']
        href = content['noticeId']
        href = "http://sm.fjzfcg.gov.cn/n/smzfcg/article.do?noticeId=" + href
        ggstart_time = content['time'][:8]
        gg_type = content['type']
        address = content['areaName']
        info={'gg_type':gg_type,'diqu':address}
        info=json.dumps(info,ensure_ascii=False)
        tmp = [name, ggstart_time, href,info]
        print(tmp)
        data_.append(tmp)
    df = pd.DataFrame(data=data_)

    return df


def f2(driver):
    locator = (By.XPATH, '//div[@id="htcList"]//tr[1]/td[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath('//div[@class="pagination"]/a[last()-2]').text.strip()

    total=int(page)

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@id="noticeContentDiv"]')

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    locator = (By.XPATH, '//div[@id="noticeContentDiv"][string-length()>2] | //div[@id="noticeContentDiv"][count(*)>=1]')
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

    div = soup.find('div',id="noticeContentDiv")

    return div


data = [
    ###包含中标,流标
    ["zfcg_gqita_dianzi_diqu1_gg", "http://sm.fjzfcg.gov.cn/n/smzfcg/secpag.do?sid=200100&cgfs=100005004&level=city", ['name', 'ggstart_time',  'href','info'],add_info(f1,{"gclx":"电子反拍"}), f2],
    ["zfcg_gqita_dianzi_diqu2_gg", "http://sm.fjzfcg.gov.cn/n/smzfcg/secpag.do?sid=200100&cgfs=100005004&level=county", ['name', 'ggstart_time', 'href','info'],add_info(f1,{"gclx":"电子反拍"}), f2],
]


##f1中有diqu

def work(conp, **args):
    est_meta(conp, data=data, diqu="福建省三明市", **args)
    est_html(conp, f=f3, **args)

if __name__ == '__main__':
    conp = ["postgres", "since2015", "192.168.3.171", "lch", "fujian_sanming"]

    work(conp=conp,pageloadtimeout=80,pageloadstrategy='none',num=1)