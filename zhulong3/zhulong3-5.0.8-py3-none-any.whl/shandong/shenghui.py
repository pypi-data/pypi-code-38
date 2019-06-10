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

from zhulong3.util.etl import est_tbs, est_meta, est_html, add_info,est_meta_large

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url = "http://www.fzztb.com/CmsPortalWeb/main/project.xhtml"
# driver = webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_ = 'shandong_shenghui'


def f1(driver, num):
    locator = (By.XPATH, '//table[@class="tableCSS"]//tr[2]/td[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath('//div[@id="AspNetPager1"]//span[contains(@style,"red")]').text
    if cnum != str(num):

        val = driver.find_element_by_xpath('//table[@class="tableCSS"]//tr[2]/td[2]//a').get_attribute('href')[-30:-5]

        driver.execute_script("javascript:__doPostBack('AspNetPager1','%s')" % num)

        locator = (By.XPATH, '//table[@class="tableCSS"]//tr[2]/td[2]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url=driver.current_url
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    if 'flag=-1' in url:
        df=parser_zhaobiao(soup)
    elif 'flag=2' in url:
        df=parser_zhongbiao(soup)
    else:
        df=parser_zigeyushen(soup)

    return df

def parser_zhaobiao(soup):
    data=[]
    trs = soup.find('table', class_="tableCSS").find_all('tr')[1:]

    for tr in trs:
        tds = tr.find_all('td')
        href = tds[1].a['href']
        name = tds[1].a['title']
        ggstart_time = tds[3].get_text()
        gg_type1=tds[0].get_text()
        gg_type1=re.findall('\[.+\]',gg_type1)[0]
        gg_type2 = tds[0].span['title'].strip()
        gg_type=gg_type1+gg_type2
        address = tds[2].span['title'].strip()

        if 'http' in href:
            href = href
        else:
            href = 'http://103.239.153.140:88/webztb/' + href

        info = {'gg_type': gg_type, "diqu": address}
        info=json.dumps(info, ensure_ascii=False)
        tmp = [name, ggstart_time, href,info]

        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df

def parser_zhongbiao(soup):
    data=[]
    trs = soup.find('table', class_="tableCSS").find_all('tr')[1:]

    for tr in trs:
        tds = tr.find_all('td')
        href = tds[1].a['href']
        name = tds[1].a['title']
        ggstart_time = tds[2].get_text().strip()

        address = tds[0].span['title']

        if 'http' in href:
            href = href
        else:
            href = 'http://103.239.153.140:88/webztb/' + href


        info = { "diqu": address}
        info=json.dumps(info, ensure_ascii=False)
        tmp = [name, ggstart_time, href,info]

        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df

def parser_zigeyushen(soup):
    data=[]
    trs = soup.find('table', class_="tableCSS").find_all('tr')[1:]

    for tr in trs:
        tds = tr.find_all('td')
        href = tds[1].a['href']
        name = tds[1].a['title']
        ggstart_time = '1'

        bumen = tds[0].span['title'].strip()
        biaoduan = tds[2].a['title'].strip()
        fail_num=tds[3].get_text().strip()

        if 'http' in href:
            href = href
        else:
            href = 'http://103.239.153.140:88/webztb/' + href

        info = { "bumen": bumen,"biaoduan":biaoduan,"fail_num":fail_num}
        info=json.dumps(info, ensure_ascii=False)

        tmp = [name, ggstart_time, href,info]
        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df



def f2(driver):
    locator = (By.XPATH, '//table[@class="tableCSS"]//tr[2]/td[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//div[@id="AspNetPager1"]/a[last()] | //div[@id="AspNetPager1"]/div[1]/a[last()]').get_attribute('href')

    total = re.findall("javascript:__doPostBack\('AspNetPager1','(\d+?)'\)", total)[0].strip()
    total = int(total)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    try:
        locator = (By.XPATH,
               '//div[@id="htmlTable"][string-length()>10] | //div[@class="content"][string-length()>10]')

        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    except:
        if 'www.sdzb.gov.cn' in driver.current_url:
            return
        else:
            raise TimeoutError
    time.sleep(0.1)
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

    div = soup.find('div', id="htmlTable")
    if div == None:
        div = soup.find('div',class_='content')

    return div


data = [

    #包含招标,其他
    ["gcjs_zhaobiao_gg", "http://103.239.153.140:88/webztb/MoreNews_GG.aspx?areacode=&flag=-1&pname=",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://103.239.153.140:88/webztb/MoreNews_GG.aspx?areacode=&flag=2&pname=",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zgys_gg", "http://103.239.153.140:88/webztb/ztbZgysResult.aspx",["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="山东省省会", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch2", "shandong_shenghui"])