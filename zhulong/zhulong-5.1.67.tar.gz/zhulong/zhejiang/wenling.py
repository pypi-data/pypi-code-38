import math

import pandas as pd
import re

import requests
from zhulong.util.fake_useragent import UserAgent
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


_name_="wenling"


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
    start_url = "http://new.wl.gov.cn/module/jpage/dataproxy.jsp?startrecord={}&endrecord={}&perpage=15".format(((num - 1) * 3 * 15 + 1), (num * 3 * 15))
    headers = {
        'User-Agent': user_agent,
    }
    data = {
        "col": 1,
        "appid": 1,
        "webid": 2760,
        "path": "/",
        "columnid": columnid,
        "sourceContentType": 1,
        "unitid": unitid,
        "webname": "温岭市门户网站",
        "permissiontype": 0,
    }
    if proxies:
        res = requests.post(url=start_url, headers=headers, data=data, proxies=proxies)
    else:
        res = requests.post(url=start_url, headers=headers, data=data)
    if res.status_code != 200:
        raise ConnectionError
    else:
        page = res.text
        if page:
            page = re.findall(r'<recordset>(.*)</recordset>', page)[0]
            soup = BeautifulSoup(page, 'html.parser')
            divs = soup.find_all('record')
            data_list = []
            for div in divs:
                lis = re.findall(r'CDATA\[(.*)\]\]></record>', str(div))[0]
                soup = BeautifulSoup(lis, 'html.parser')
                lis = soup.find_all('tr')
                for li in lis:
                    info = {}
                    a = li.find('a')
                    title = a.text.strip()
                    link = 'http://new.wl.gov.cn' + a['href'].strip()
                    span = li.find_all('td')[-1].text.strip()
                    if re.findall(r'^\[(.*?)\]', title):
                        diqu = re.findall(r'^\[(.*?)\]', title)[0]
                        info['diqu'] = diqu
                    if info:
                        info = json.dumps(info, ensure_ascii=False)
                    else:
                        info = None
                    tmp = [title, span, link, info]
                    data_list.append(tmp)
            df = pd.DataFrame(data_list)
            return df



def f2(driver):
    locator = (By.XPATH, "//*[@id='4482116']/div/div/table/tbody/tr[1]/td[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//span[@class='default_pgTotalPage']")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = math.ceil(int(st) / 3)
    except:
        num = 1
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    if '404' in driver.title:
        return 404
    locator = (By.XPATH, "//table[@id='c'][string-length()>30]")
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
    div = soup.find('table', id="c")
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://new.wl.gov.cn/col/col1456441/index.html?uid=4482116&pageNum=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_bian_da_gg",
     "http://new.wl.gov.cn/col/col1456443/index.html?uid=4482116&pageNum=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zgysjg_gg",
     "http://new.wl.gov.cn/col/col1456445/index.html?uid=4482116&pageNum=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_kaibiao_gg",
     "http://new.wl.gov.cn/col/col1622986/index.html?uid=4482116&pageNum=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://new.wl.gov.cn/col/col1456442/index.html?uid=4482116&pageNum=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://new.wl.gov.cn/col/col1456444/index.html?uid=4482116&pageNum=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_hetong_gg",
     "http://new.wl.gov.cn/col/col1622988/index.html?uid=4482116&pageNum=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_jizhong_gg",
     "http://new.wl.gov.cn/col/col1456446/index.html?uid=4482116&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'集中采购'}), f2],

    ["zfcg_gqita_zhong_liu_jizhong_gg",
     "http://new.wl.gov.cn/col/col1456447/index.html?uid=4482116&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'集中采购'}), f2],

    ["zfcg_biangeng_jizhong_gg",
     "http://new.wl.gov.cn/col/col1456448/index.html?uid=4482116&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'集中采购'}), f2],

    ["zfcg_hetong_jizhong_gg",
     "http://new.wl.gov.cn/col/col1456449/index.html?uid=4482116&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '集中采购'}), f2],

    ["zfcg_yucai_jizhong_gg",
     "http://new.wl.gov.cn/col/col1456450/index.html?uid=4482116&pageNum=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'zbfs': '集中采购'}),f2],

    ["zfcg_kaibiao_jizhong_gg",
     "http://new.wl.gov.cn/col/col1622990/index.html?uid=4482116&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '集中采购'}), f2],

    ["zfcg_zhaobiao_fensan_gg",
     "http://new.wl.gov.cn/col/col1456451/index.html?uid=4482116&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '分散采购'}), f2],

    ["zfcg_gqita_zhong_liu_fensan_gg",
     "http://new.wl.gov.cn/col/col1456452/index.html?uid=4482116&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '分散采购'}), f2],

    ["zfcg_gqita_bian_bu_fensan_gg",
     "http://new.wl.gov.cn/col/col1456453/index.html?uid=4482116&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '分散采购'}), f2],

    ["zfcg_hetong_fensan_gg",
     "http://new.wl.gov.cn/col/col1622994/index.html?uid=4482116&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '分散采购'}), f2],

    ["qsy_zhaobiao_gg",
     "http://new.wl.gov.cn/col/col1456462/index.html?uid=4482116&pageNum=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx': '其他交易'}), f2],

    ["qsy_zhongbiao_gg",
     "http://new.wl.gov.cn/col/col1456463/index.html?uid=4482116&pageNum=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx': '其他交易'}), f2],

    ["jqita_zhaobiao_gg",
     "http://new.wl.gov.cn/col/col1456464/index.html?uid=4482116&pageNum=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx': '镇街道平台'}), f2],

    ["jqita_gqita_bian_cheng_gg",
     "http://new.wl.gov.cn/col/col1619676/index.html?uid=4482116&pageNum=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx': '镇街道平台'}), f2],

    ["jqita_zhongbiaohx_gg",
     "http://new.wl.gov.cn/col/col1456465/index.html?uid=4482116&pageNum=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx': '镇街道平台'}), f2],

    ["jqita_zhongbiao_gg",
     "http://new.wl.gov.cn/col/col1621639/index.html?uid=4482116&pageNum=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx': '镇街道平台'}), f2],


]


def work(conp,**args):
    est_meta(conp,data=data,diqu="浙江省温岭市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","zhejiang","wenling"])


