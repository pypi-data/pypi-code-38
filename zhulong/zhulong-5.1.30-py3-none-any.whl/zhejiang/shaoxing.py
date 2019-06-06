import pandas as pd
import re

import requests
from zhulong.util.fake_useragent import UserAgent
from lxml import etree
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


_name_="shaoxing"



def f1(driver, num):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s'% proxy}
    except:
        proxies = ''
    url = driver.current_url
    columnid = re.findall(r'col/col(\d+)/', url)[0]
    unitid = re.findall(r'uid=(\d+)', url)[0]
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    start_url = "http://ggb.sx.gov.cn/module/jpage/dataproxy.jsp?startrecord={}&endrecord={}&perpage=15".format(
        ((num - 1) * 3 * 15 + 1), (num * 3 * 15))
    headers = {
        'User-Agent': user_agent,
    }
    data = {
        "col": 1,
        "appid": 1,
        "webid": 3003,
        "path": "/",
        "columnid": columnid,
        "sourceContentType": 1,
        "unitid": unitid,
        "webname": "绍兴公共资源交易网",
        "permissiontype": 0,
    }
    if proxies:
        res = requests.post(url=start_url, headers=headers, data=data, proxies=proxies)
    else:
        res = requests.post(url=start_url, headers=headers, data=data)
    if res.status_code == 200:
        page = res.text
        if page:
            page = re.findall(r'<recordset>(.*)</recordset>', page)[0]
            soup = BeautifulSoup(page, 'html.parser')
            divs = soup.find_all('record')
            data_list = []
            for div in divs:
                lis = re.findall(r'CDATA\[(.*)\]\]></record>', str(div))[0]
                soup = BeautifulSoup(lis, 'html.parser')
                lis = soup.find_all('li')
                for li in lis:
                    a = li.find('a')
                    title = a.text.strip()
                    link = 'http://ggb.sx.gov.cn' + a['href'].strip()
                    span = li.find('span').text.strip()
                    span = re.findall(r'\[(.*)\]', span)[0]
                    if re.findall('^【(.*?)】', title):
                        diqu = re.findall('^【(.*?)】', title)[0]
                        if ('区' in diqu) or ('县' in diqu) or ('市' in diqu):
                            info = json.dumps({'diqu':diqu}, ensure_ascii=False)
                        else:
                            info = json.dumps({'xmly': diqu}, ensure_ascii=False)
                    else:
                        info = None
                    tmp = [title, span, link, info]
                    data_list.append(tmp)
            df = pd.DataFrame(data_list)
            return df


def f2(driver):
    locator = (By.XPATH, "//*[@id='4685909']/div/ul[1]/li/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//span[@class='default_pgTotalPage']")
    num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    if int(num)/3 == int(int(num)/3):
        num = int(int(num) / 3)
    else:
        num = int(int(num) / 3) + 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@style='margin:0 auto;']")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find('table', attrs={'style':'margin:0 auto;','border':False})
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://ggb.sx.gov.cn/col/col1518854/index.html?uid=4685909&pageNum=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zgysjg_gg",
     "http://ggb.sx.gov.cn/col/col1518855/index.html?uid=4685909&pageNum=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiaohx_gg",
     "http://ggb.sx.gov.cn/col/col1518856/index.html?uid=4685909&pageNum=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiao_gg",
     "http://ggb.sx.gov.cn/col/col1518857/index.html?uid=4685909&pageNum=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],


    ["zfcg_yucai_gg",
     "http://ggb.sx.gov.cn/col/col1518859/index.html?uid=4685909&pageNum=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhaobiao_gg",
     "http://ggb.sx.gov.cn/col/col1518860/index.html?uid=4685909&pageNum=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhongbiao_gg",
     "http://ggb.sx.gov.cn/col/col1518861/index.html?uid=4685909&pageNum=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],


    ["zfcg_liubiao_gg",
     "http://ggb.sx.gov.cn/col/col1518862/index.html?uid=4685909&pageNum=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],


    ["qsy_zhaobiao_gg",
     "http://ggb.sx.gov.cn/col/col1518878/index.html?uid=4685909&pageNum=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'非中心交易(公告代发)项目'}),f2],

    ["qsy_zhongbiao_gg",
     "http://ggb.sx.gov.cn/col/col1518879/index.html?uid=4685909&pageNum=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'非中心交易(公告代发)项目'}),f2],

    ["gcjs_zhaobiao_quxian_gg",
     "http://ggb.sx.gov.cn/col/col1518891/index.html?uid=4685909&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'区、县(市)'}), f2],

    ["gcjs_zhongbiaohx_quxian_gg",
     "http://ggb.sx.gov.cn/col/col1518892/index.html?uid=4685909&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'区、县(市)'}), f2],

    ["gcjs_zhongbiao_quxian_gg",
     "http://ggb.sx.gov.cn/col/col1518893/index.html?uid=4685909&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'区、县(市)'}), f2],


    ["zfcg_yucai_quxian_gg",
     "http://ggb.sx.gov.cn/col/col1518894/index.html?uid=4685909&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'区、县(市)'}), f2],

    ["zfcg_gqita_zhao_da_quxian_gg",
     "http://ggb.sx.gov.cn/col/col1518895/index.html?uid=4685909&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'区、县(市)'}), f2],

    ["zfcg_zhongbiao_quxian_gg",
     "http://ggb.sx.gov.cn/col/col1518896/index.html?uid=4685909&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'区、县(市)'}), f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="浙江省绍兴市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","zhejiang","shaoxing"])



