import datetime
import json
import time

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
from zhulong2.util.fake_useragent import UserAgent

from zhulong2.util.etl import est_tbs, est_meta, est_html, gg_existed, est_gg, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://www.lczfcg.gov.cn/goods/publish/channel.jsp?Keyword=&Year=2019&Month=-1&Area=&Channel=%B2%C9%B9%BA%B9%AB%CA%BE&Careful=%BD%F8%BF%DA%B2%FA%C6%B7%B9%AB%CA%BE&Fashion="
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)


_name_='shandong_liaocheng'


def f1(driver,num):
    proxies_data = webdriver.DesiredCapabilities.CHROME
    proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
    if proxies_chromeOptions:
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    else:
        proxies = {}

    ua=UserAgent()

    url=driver.current_url
    year_month=date_list[-num]

    year_=year_month.split('-')[0]
    month_=year_month.split('-')[1]

    s='&Year={year_}&Month={month_}&'.format(year_=year_,month_=month_)
    url_=re.sub('&Year=.+?&Month=.+?&',s,url)

    req=requests.get(url_,proxies=proxies,headers={'User-Agent':ua.chrome},timeout=20)

    data = []
    if req.status_code != 200:
        raise ValueError

    soup = BeautifulSoup(req.text, 'html.parser')

    div = soup.find_all('td', attrs={"bgcolor": '#FFFFFF', "class": 'TD'})[1].find('table')

    trs = div.find_all('tr', recursive=False)

    if len(trs)<2:
        return pd.DataFrame(data=[['1','2000-1-1','1',json.dumps({"hreftype":"不可抓网页","tag":"假数据"})],])

    for i in range(0, len(trs), 2):
        tr = trs[i]

        if len(tr.get_text()) < 10:
            continue
        tds = tr.find_all('td', class_="TD")
        spans = tds[0].find_all('span')
        href = spans[0].a['href']
        if 'http' in href:
            href = href
        else:
            href = "http://www.lczfcg.gov.cn/goods/publish/" + href
        name = spans[0].a.b.get_text().strip('.').strip()
        company = spans[1].get_text().strip()
        ggstart_time = tds[1].get_text().strip()
        info={'company':company}
        info=json.dumps(info,ensure_ascii=False)
        tmp = [name, ggstart_time, href,info]

        data.append(tmp)

    df=pd.DataFrame(data=data)


    return df


def f2(driver):
    proxies_data = webdriver.DesiredCapabilities.CHROME
    proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
    if proxies_chromeOptions:
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    else:
        proxies = {}

    ua = UserAgent()

    url=driver.current_url
    global date_list
    date_list=[]
    YEAR = []

    req = requests.get(url, proxies=proxies,headers={'User-Agent': ua.chrome}, timeout=20)

    if req.status_code != 200:
        raise ValueError
    html = BeautifulSoup(req.text, 'html.parser')
    '//td[@bgcolor="#FFFFFF"][not(@class)]//tr[1]/td[2]/a'
    years = html.find('td', attrs={"bgcolor": '#FFFFFF', "class": ''}).find('tr').find_all('td')[1].find_all('a')
    for year in years:
        year = year.get_text().strip('年').strip()
        YEAR.append(year)

    now_time = datetime.date.today()
    count_month=re.findall('\-(\d+)\-',str(now_time))[0]

    total=(len(YEAR)-1)*12+int(count_month)

    for num in range(1, total + 1):
        year_ = YEAR[num // 12 if num % 12 != 0 else num // 12 - 1]
        month_ = num % 12
        if month_ == 0: month_ = 12
        date_str = str(year_) + '-' + str(month_)
        date_list.append(date_str)

    driver.quit()
    return total



def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//td[@bgcolor="#FFFFFF"][not(@class)][string-length()>10]')

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

    div = soup.find('td', attrs={'bgcolor': '#FFFFFF','class':False})
    if div == None:
        raise ValueError

    return div

data=[
        #
    ["zfcg_zhaobiao_gg", "http://www.lczfcg.gov.cn/goods/publish/channel.jsp?Keyword=&Year=2018&Month=1&Area=&Channel=%B2%C9%B9%BA%B9%AB%B8%E6&Careful=%B2%C9%B9%BA%B9%AB%B8%E6&Fashion=",['name', 'ggstart_time', 'href', 'info'], f1, f2],
    ["zfcg_zhongbiao_gg", "http://www.lczfcg.gov.cn/goods/publish/channel.jsp?Keyword=&Year=2018&Month=1&Area=&Channel=%B2%C9%B9%BA%B9%AB%B8%E6&Careful=%B3%C9%BD%BB%B9%AB%B8%E6&Fashion=",['name', 'ggstart_time', 'href', 'info'], f1, f2],
    ["zfcg_biangeng_gg", "http://www.lczfcg.gov.cn/goods/publish/channel.jsp?Keyword=&Year=2018&Month=1&Area=&Channel=%B2%C9%B9%BA%B9%AB%B8%E6&Careful=%B1%E4%B8%FC%B9%AB%B8%E6&Fashion=",['name', 'ggstart_time', 'href', 'info'], f1, f2],
    ["zfcg_liubiao_gg", "http://www.lczfcg.gov.cn/goods/publish/channel.jsp?Keyword=&Year=2018&Month=1&Area=&Channel=%B2%C9%B9%BA%B9%AB%B8%E6&Careful=%D6%D5%D6%B9%B9%AB%B8%E6&Fashion=",['name', 'ggstart_time', 'href', 'info'], f1, f2],

    ["zfcg_yucai_gg", "http://www.lczfcg.gov.cn/goods/publish/channel.jsp?Keyword=&Year=2018&Month=1&Area=&Channel=%B2%C9%B9%BA%B9%AB%CA%BE&Careful=%D0%E8%C7%F3%B9%AB%CA%BE&Fashion=",['name', 'ggstart_time', 'href', 'info'], f1, f2],
    ["zfcg_yanshou_gg", "http://www.lczfcg.gov.cn/goods/publish/channel.jsp?Keyword=&Year=2018&Month=1&Area=&Channel=%B2%C9%B9%BA%B9%AB%CA%BE&Careful=%D1%E9%CA%D5%B9%AB%CA%BE&Fashion=",['name', 'ggstart_time', 'href', 'info'], f1, f2],
    ["zfcg_gqita_ppp_gg", "http://www.lczfcg.gov.cn/goods/publish/channel.jsp?Keyword=&Year=2018&Month=1&Area=&Channel=%B2%C9%B9%BA%B9%AB%CA%BE&Careful=PPP%CF%EE%C4%BF%B9%AB%CA%BE&Fashion=",['name', 'ggstart_time', 'href', 'info'], add_info(f1,{"tag":"PPP项目"}), f2],
    ["zfcg_zhaobiao_danyilaiyuan_gg", "http://www.lczfcg.gov.cn/goods/publish/channel.jsp?Keyword=&Year=2018&Month=-1&Area=&Channel=%B2%C9%B9%BA%B9%AB%CA%BE&Careful=%B5%A5%D2%BB%C0%B4%D4%B4%B9%AB%CA%BE&Fashion=",['name', 'ggstart_time', 'href', 'info'], add_info(f1,{"tag":"单一来源"}), f2],
    ["zfcg_gqita_jinkou_gg", "http://www.lczfcg.gov.cn/goods/publish/channel.jsp?Keyword=&Year=2019&Month=-1&Area=&Channel=%B2%C9%B9%BA%B9%AB%CA%BE&Careful=%BD%F8%BF%DA%B2%FA%C6%B7%B9%AB%CA%BE&Fashion=",['name', 'ggstart_time', 'href', 'info'], add_info(f1,{"tag":"进口产品"}), f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="山东省聊城市",**args)
    est_html(conp,f=f3,**args)

if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","lch","shandong_liaocheng"]

    work(conp=conp,headless=False,cdc_total=2,num=1,total=2)