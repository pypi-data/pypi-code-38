import random
import pandas as pd
import re
import requests
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from zhulong.util.etl import est_html, est_meta, add_info
from zhulong.util.fake_useragent import UserAgent

_name_ = "shaoguan"


def f1(driver, num):
    start_url = driver.current_url
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': user_agent,
        'Host': 'www.sgjyzx.com',
        }
    payloadData = {
        'searchvalue': '',
        'businessAnnounce.dpId': '',
        'pageSize': 20,
        'page': num,
        'sortField': 'RELEASETIME',
        'sortOrder': 'DESC'
    }
    # 下载超时
    timeOut = 25
    time.sleep(0.5+random.random())
    res = requests.post(url=start_url, headers=headers, data=payloadData, timeout=timeOut)
    # 需要判断是否为登录后的页面
    if res.status_code != 200:
        raise ConnectionError('response status code is %s' % res.status_code)

    html = res.text
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find("table", id="dataList")
    trs1 = div.find_all("tr", class_="listRow")
    trs2 = div.find_all("tr", class_="listAlternatingRow")
    data = []
    for tr in trs1:
        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()

        td = tr.find('td', class_="tdRight", align="center").text.strip()
        href = a['href'].strip()
        link = 'http://www.sgjyzx.com' + href
        span = tr.find('span', style="color:blue;").text.strip()
        a = re.findall(r'(.*)\|', span)[0].strip()
        info = {'diqu':'{}'.format(a)}
        info = json.dumps(info, ensure_ascii=False)
        tmp = [title, td, link, info]
        data.append(tmp)
    for tr in trs2:
        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        td = tr.find('td', class_="tdRight", align="center").text.strip()
        href = a['href'].strip()
        link = 'http://www.sgjyzx.com' + href
        span = tr.find('span', style="color:blue;").text.strip()
        a = re.findall(r'(.*)\|', span)[0].strip()
        info = {'diqu': '{}'.format(a)}
        info = json.dumps(info, ensure_ascii=False)
        tmp = [title, td, link, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df




def f2(driver):
    start_url = driver.current_url
    page_num = get_pageall(start_url)
    driver.quit()
    return int(page_num)


def get_pageall(start_url):
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': user_agent,
        'Host': 'www.sgjyzx.com',
        }
    payloadData = {
        'searchvalue': '',
        'businessAnnounce.dpId': '',
        'pageSize': 20,
        'page': 1,
        'sortField': 'RELEASETIME',
        'sortOrder': 'DESC'
    }
    # 下载超时
    timeOut = 25
    time.sleep(0.8+ random.random())
    res = requests.post(url=start_url, headers=headers, data=payloadData, timeout=timeOut)
    # 需要判断是否为登录后的页面
    if res.status_code != 200:
        raise ConnectionError('response status code is %s'%res.status_code)

    html = res.text
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='pagination page-mar')
    ul = div.find('ul', style="text-align: center;")
    span = ul.find_all('span')[-1].text.strip()
    total = re.findall(r'共(\d+)页', span)[0]
    total = int(total)
    return total


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@class='xx-main'][string-length()>30] | //div[@class='xx-main'][string-length()>30]")
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
    div = soup.find('table', class_='xx-main')
    if div == None:
        div = soup.find('div', class_='xx-main')
    return div


data = [
    ["gcjs_gqita_zhao_liu_gg",
     "http://www.sgjyzx.com/businessAnnounceAction!frontBusinessAnnounceIframeList.do?businessAnnounce.announcetype=12",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["gcjs_dayi_gg",
     "http://www.sgjyzx.com/businessAnnounceAction!frontBusinessAnnounceIframeList.do?businessAnnounce.announcetype=13",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["gcjs_zhongbiaohx_1_gg",
     "http://www.sgjyzx.com/businessAnnounceAction!frontBusinessAnnounceIframeList.do?businessAnnounce.announcetype=16",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["gcjs_zhongbiaohx_2_gg",
     "http://www.sgjyzx.com/businessAnnounceAction!frontBusinessAnnounceIframeList.do?businessAnnounce.announcetype=15",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'全过程评标结果公示'}), f2],

    ["gcjs_zhongbiao_gg",
     "http://www.sgjyzx.com/businessAnnounceAction!frontBusinessAnnounceIframeList.do?businessAnnounce.announcetype=17",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhaobiao_gg",
     "http://www.sgjyzx.com/businessAnnounceAction!frontBusinessAnnounceIframeList.do?businessAnnounce.announcetype=00",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["zfcg_biangeng_gg",
     "http://www.sgjyzx.com/businessAnnounceAction!frontBusinessAnnounceIframeList.do?businessAnnounce.announcetype=01",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["zfcg_gqita_zhong_liu_gg",
     "http://www.sgjyzx.com/businessAnnounceAction!frontBusinessAnnounceIframeList.do?businessAnnounce.announcetype=02",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_xiaoe_gg",
     "http://www.sgjyzx.com/businessAnnounceAction!frontBusinessAnnounceIframeList.do?businessAnnounce.announcetype=70",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'小额建设工程交易'}), f2],

    ["gcjs_gqita_bian_zhongz_xiaoe_gg",
     "http://www.sgjyzx.com/businessAnnounceAction!frontBusinessAnnounceIframeList.do?businessAnnounce.announcetype=72",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'小额建设工程交易'}), f2],

    ["gcjs_gqita_zhong_bian_xiaoe_gg",
     "http://www.sgjyzx.com/businessAnnounceAction!frontBusinessAnnounceIframeList.do?businessAnnounce.announcetype=71",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'小额建设工程交易'}), f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省韶关市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guangdong", "shaoguan_test"])


