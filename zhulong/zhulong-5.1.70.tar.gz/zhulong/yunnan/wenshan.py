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


from zhulong.util.etl import est_tbs, est_meta, est_html, est_gg


# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hengyang.gov.cn/jyxx/jsgc/zbgg_64796/index.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_='wenshan'


def f1(driver,num):
    locator = (By.XPATH, '//div[@class="news"]/table/tbody/tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum = driver.find_element_by_xpath('//a[@class="cur"]').text.strip()

    if int(cnum) != num:
        val = driver.find_element_by_xpath('//div[@class="news"]/table/tbody/tr[2]//a').get_attribute('href')[-30:-5]

        driver.execute_script("pagination({});return false;".format(num))

        locator = (By.XPATH, '//div[@class="news"]/table/tbody/tr[2]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))


    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='news').find('table')
    trs = div.find_all('tr')

    if ("jsgcZbgg" in url) or ('cggg' in url):
        data=parse_1(trs)
    elif 'jsgcBgtz' in url:
        data=parse_2(trs)
    elif ('jsgcZbyc' in url) or ('zfcgYcgg' in url):
        data=parse_4(trs)
    else:
        data=parse_3(trs,url)


    df=pd.DataFrame(data=data)

    return df
def parse_1(trs):
    data = []
    for i in range(1, len(trs)):
        tr = trs[i]
        tds = tr.find_all('td')
        index_num = tds[1].get_text()
        href = tds[2].a['href']
        name = tds[2].a['title']
        ggstart_time = tds[3].get_text()
        ggend_time = tds[4].get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://wsggzy.cn' + href
        info = {'index_num': index_num,'ggend_time':ggend_time}
        info = json.dumps(info, ensure_ascii=False)
        tmp = [ name, href, ggstart_time, info]
        data.append(tmp)
    return data

def parse_2(trs):
    data = []
    for i in range(1, len(trs)):
        tr = trs[i]
        tds = tr.find_all('td')
        index_num = tds[1].get_text()
        title = tds[2].get_text()
        href = tds[3].a['href']
        name = tds[3].a['title']
        ggstart_time = tds[4].get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://wsggzy.cn' + href
        info = {'index_num': index_num,'title':title}
        info = json.dumps(info, ensure_ascii=False)
        tmp = [name, href, ggstart_time,info]
        data.append(tmp)
    return data
def parse_3(trs,url):
    data = []
    for i in range(1, len(trs)):
        tr = trs[i]
        tds = tr.find_all('td')
        index_num = tds[1].get_text()

        href = tds[2].a['href']
        if 'jsgcZbjggs' in url:
            name = tds[2]['title']
        else:
            name=tds[2].a['title']
        ggstart_time = tds[3].get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://wsggzy.cn' + href
        info = {'index_num': index_num}
        info = json.dumps(info, ensure_ascii=False)
        tmp = [ name, href, ggstart_time,info]
        data.append(tmp)

    return data
def parse_4(trs):
    data = []
    for i in range(1, len(trs)):
        tr = trs[i]
        tds = tr.find_all('td')
        index_num = tds[1].get_text()

        href = tds[2].a['href']
        name = tds[2].a['title']
        yctype = tds[3].get_text()
        ggstart_time = tds[4].get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://wsggzy.cn' + href
        info = {'index_num': index_num,'yctype':yctype}
        info = json.dumps(info, ensure_ascii=False)
        tmp = [ name, href,  ggstart_time,info]
        data.append(tmp)

    return data

def f2(driver):
    locator = (By.XPATH, '//div[@class="news"]/table/tbody/tr[2]/td[3]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath('//div[@class="mmggxlh"]/a[last()-1]').text
    total = int(page)
    driver.quit()
    return total

def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="news-layout"]')

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

    div=soup.find('div',class_="news-layout")

    return div

data=[
    #
    ["gcjs_zhaobiao_gg","http://wsggzy.cn/jyxx/jsgcZbgg",[ "name", "href", "ggstart_time", "info"],f1,f2],
    ["zfcg_zhaobiao_gg","http://wsggzy.cn/jyxx/zfcg/cggg",[ "name", "href", "ggstart_time", "info"],f1,f2],

    ["gcjs_gqita_da_bian_gg","http://wsggzy.cn/jyxx/jsgcBgtz",[ "name", "href", "ggstart_time","info"],f1,f2],

    ["gcjs_zhongbiaohx_gg","http://wsggzy.cn/jyxx/jsgcpbjggs",[ "name", "href", "ggstart_time","info"],f1,f2],

    ["gcjs_zhongbiao_gg","http://wsggzy.cn/jyxx/jsgcZbjggs",[ "name", "href", "ggstart_time","info"],f1,f2],

    ["gcjs_liubiao_gg","http://wsggzy.cn/jyxx/jsgcZbyc",[ "name", "href", "ggstart_time","info"],f1,f2],
    ["zfcg_liubiao_gg","http://wsggzy.cn/jyxx/zfcg/zfcgYcgg",[ "name", "href", "ggstart_time","info"],f1,f2],

    ["zfcg_gqita_da_bian_gg","http://wsggzy.cn/jyxx/zfcg/gzsx",[ "name", "href", "ggstart_time","info"],f1,f2],
    ["zfcg_zhongbiaohx_gg","http://wsggzy.cn/jyxx/zfcg/zbjggs",[ "name", "href", "ggstart_time","info"],f1,f2],


]

def work(conp,**args):
    est_meta(conp,data=data,diqu="云南省文山市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","yunnan_new","wenshan"]
    # conp=["postgres","since2015","192.168.3.171","test","lch"]

    work(conp=conp,num=10)