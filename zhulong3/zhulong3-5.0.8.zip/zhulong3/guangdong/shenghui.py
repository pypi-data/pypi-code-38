import time

import pandas as pd
import re
from datetime import datetime,timedelta,date
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

from zhulong3.util.etl import est_tbs, est_meta, est_html,add_info,est_meta_large,est_gg

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url = "http://www.fzztb.com/CmsPortalWeb/main/project.xhtml"
# driver = webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_ = 'guangdong_shenghui'


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="tablist"]/dl[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = driver.find_element_by_xpath('//span[@class="cpb"]').text

    mark_dict={"Default":"ZbList1","BidList":"BidList1","OutTender":"OutList1","GovTender":"GovList1"}

    mark=re.findall('Ztb/(.+?).aspx',url)[0]


    if cnum != str(num):
        if mark != 'Default':
            val=driver.find_element_by_xpath('//div[@class="tablist"]/dl[1]//a').get_attribute('href')[-30:-5]
        else:
            val = driver.find_element_by_xpath('//div[@class="tablist"]/dl[1]//a').get_attribute('onclick')[-30:-5]

        driver.execute_script(
            "javascript:__doPostBack('ctl00$ctl00$WebAjaxContent$WebAjaxContent${mark1}$pager$netPager','{num}')".format(mark1=mark_dict[mark],num=num))

        if mark != 'Default':
            locator = (By.XPATH, '//div[@class="tablist"]/dl[1]//a[not(contains(@href,"{}"))]'.format(val))
        else:
            locator = (By.XPATH, '//div[@class="tablist"]/dl[1]//a[not(contains(@onclick,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))


    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')


    if 'BidList.aspx' in url:
        df=parser_zhongbiao(soup)
    elif 'Default' in url:
        df=parser_zhaobiao(soup)
    else:
        df=parser_qita(soup)

    return df

def parser_zhaobiao(soup):
    data=[]
    trs = soup.find('div', class_="tablist").find_all('dl')
    for tr in trs:
        href = tr.find('a')['onclick']
        name = tr.find('a')['title'].strip()
        content = tr.find('div', attrs={'class': ''})
        dts = content.find_all('dt')
        address = dts[0].get_text().strip()
        gg_type = dts[1].get_text().strip().strip('类别：')
        ggend_time = dts[2].get_text().strip().strip('截止：')
        ggstart_time = dts[3].get_text().strip().strip('发布：')

        ggend_time_t = date.today()
        if '天' in ggstart_time:
            if '今天' in ggstart_time:
                ggstart_time=ggend_time_t.strftime("%Y-%m-%d")
            else:
                interval_time = re.findall('(\d+)天前', ggstart_time)[0]
                interval_time = timedelta(days=int(interval_time))
                ggstart_time_t = ggend_time_t - interval_time
                ggstart_time = ggstart_time_t.strftime("%Y-%m-%d")

        href = re.findall("OpenDetail\('(.+)'\)", href)[0]

        if 'http' in href:
            href = href
        else:
            href = "http://www.gdcic.net/Ztb/ZbDetail.aspx?kid="+href

        info = {'gg_type': gg_type, "diqu": address, 'ggend_time': ggend_time}
        info = json.dumps(info, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)

    df = pd.DataFrame(data=data)

    return df

def parser_zhongbiao(soup):
    data=[]
    trs = soup.find('div', class_="tablist").find_all('dl')
    for tr in trs:
        href = tr.find('a')['href']
        name = tr.find('a').get_text().strip()
        dts = tr.find_all('dt')
        ggstart_time = dts[-1].get_text().strip().strip('')

        if 'http' in href:
            href = href
        else:
            href = "http://www.gdcic.net/Ztb/"+href

        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None

    return df


def parser_qita(soup):
    data=[]
    trs = soup.find('div', class_="tablist").find_all('dl')
    for tr in trs:
        href = tr.find('a')['href']
        name = tr.find('a')['title'].strip()
        content = tr.find('div', attrs={'class': ''})
        dts = content.find_all('dt')
        address = dts[0].get_text().strip()
        gg_type = dts[1].get_text().strip().strip('类别：')
        ggend_time = dts[2].get_text().strip().strip('截止：')
        ggstart_time = dts[3].get_text().strip().strip('发布：')

        ggend_time_t = date.today()
        if '天' in ggstart_time:
            if '今天' in ggstart_time:
                ggstart_time=ggend_time_t.strftime("%Y-%m-%d")
            else:
                interval_time = re.findall('(\d+)天前', ggstart_time)[0]
                interval_time = timedelta(days=int(interval_time))
                ggstart_time_t = ggend_time_t - interval_time
                ggstart_time = ggstart_time_t.strftime("%Y-%m-%d")

        if 'http' in href:
            href = href
        else:
            href = "http://www.gdcic.net/Ztb/"+href

        info = {'gg_type': gg_type, "diqu": address, 'ggend_time': ggend_time}
        info = json.dumps(info, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="tablist"]/dl[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath(
        '//div[@class="pages"]/ul/div/a[last()]').get_attribute('href')

    total = re.findall("'(\d+?)'", total)[0].strip()
    total = int(total)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               '//div[@class="col-L"][string-length()>10]')

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

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
    div = soup.find('div', class_="col-L")
    return div


data = [

    #包含招标,其他
    ["gcjs_zhaobiao_gg", "http://www.gdcic.net/Ztb/Default.aspx",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg", "http://www.gdcic.net/Ztb/BidList.aspx",["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhaobiao_diqu2_gg", "http://www.gdcic.net/Ztb/OutTender.aspx",["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"省外标讯"}), f2],
    ["gcjs_zhaobiao_diqu3_gg", "http://www.gdcic.net/Ztb/GovTender.aspx",["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"政府重大工程"}), f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="广东省省会", **args)
    est_html(conp, f=f3, **args)
    # est_gg(conp,diqu="广东省省会")



if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch2", "guangdong_shenghui"],headless=False,num=1)
    # work(conp=["postgres", "since2015", "10.30.30.64", "gcjs", "guangdong_shenghui"],headless=False,num=1)