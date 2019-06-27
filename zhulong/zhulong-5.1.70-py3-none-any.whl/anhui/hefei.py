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

from zhulong.util.etl import est_tbs, est_meta, est_html, gg_existed, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]

#
# url="http://ggzy.hefei.gov.cn/jyxx/002001/002001001/moreinfo_jyxxgg.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)
_name_='hefei'


def f4(driver,num):
    url=driver.current_url
    locator = (By.XPATH, '//li[@class="ewb-list-item clearfix"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    if 'moreinfo' in url:
        cnum=1
    else:
        cnum = re.findall('\/(\d+?).html', url)[0]

    main_url = url.rsplit('/', maxsplit=1)[0]
    if int(cnum) != num:
        if num==1:
            url=main_url+'/moreinfo2.html'
        else:
            url = main_url + '/' + str(num) + '.html'

        val = driver.find_element_by_xpath('//li[@class="ewb-list-item clearfix"][1]//a').get_attribute(
            "href")[-30:-5]

        driver.get(url)

        locator = (By.XPATH, '//li[@class="ewb-list-item clearfix"][1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data_ = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    ul=soup.find('ul',class_='ewb-list')
    lis=ul.find_all('li')
    for li in lis:
        address = li.find('span', class_='ewb-label1 l').get_text().strip('】').strip('【')
        href = li.a['href'].strip('.')
        name = li.a.get_text()
        ggstart_time = li.find('span', class_='ewb-list-date r').get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://ggzy.hefei.gov.cn' + href
        info={'address':address}
        info=json.dumps(info,ensure_ascii=False)
        
        tmp = [name, ggstart_time, href,info]
        
        data_.append(tmp)
    df = pd.DataFrame(data=data_)
    
    return df


def f1(driver,num):

    locator = (By.XPATH, '//ul[@class="ewb-right-item"]/li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url

    if 'moreinfo' in url:
        cnum=1
    else:
        cnum = re.findall('\/(\d+?).html', url)[0]

    main_url = url.rsplit('/', maxsplit=1)[0]

    if int(cnum) != num:

        if num == 1:
            if ('002001001' in url) or ('002002001' in url):
                url=main_url + '/moreinfo_jyxxgg.html'
            elif '002001003' in url:
                url=main_url+'/moreinfo_jyxxgs.html'
            elif '002002004' in url:
                url=main_url + '/moreinfo_jyxxzfcggs.html'
            else:
                url = main_url + '/moreinfo_jyxx.html'
        else:
            url = main_url + '/' + str(num) + '.html'

        val = driver.find_element_by_xpath('//ul[@class="ewb-right-item"]/li[1]//a').get_attribute("href")[-30:-5]
        driver.get(url)
        locator = (By.XPATH, '//ul[@class="ewb-right-item"]/li[1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data_ = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('ul', class_='ewb-right-item')
    lis = div.find_all('li')
    for li in lis:
        address = li.find('span', class_='ewb-label1 l').get_text().strip('】').strip('【')

        href = li.a['href'].strip('.')
        name = li.find('span', class_='ewb-context l').get_text().strip()
        ggstart_time = li.find('span', recursive=False).get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://ggzy.hefei.gov.cn' + href

        info={'diqu':address}
        info=json.dumps(info,ensure_ascii=False)
        tmp = [name, ggstart_time, href,info]

        data_.append(tmp)

   
    df=pd.DataFrame(data=data_)
    # df['info']=None
    return df


def f2(driver):
    locator = (By.XPATH, '//li[@class="ewb-list-item clearfix"][1]//a | //ul[@class="ewb-right-item"]/li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        page = driver.find_element_by_xpath('//*[@id="index"]').text
        total = re.findall('/(\d+)', page)[0]
        total = int(total)
    except:
        total=1

    driver.quit()
    return total

def f3(driver,url):

    driver.get(url)
    locator = (By.XPATH, '//div[@data-role="body"] | //div[@class="ewb-main"]')

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

    div = soup.find('div', attrs={'data-role': "body"})
    if div == None:
        div = soup.find('div', class_='ewb-main')
    else:
        divs = div.find_all('div', class_="ewb-info-bd hidden")
        for d in divs:
            d.extract()

    return div


data=[
    #
    ["gcjs_zhaobiao_gg","http://ggzy.hefei.gov.cn/jyxx/002001/002001001/moreinfo_jyxxgg.html",[ 'name', 'ggstart_time', 'href','info'],f1,f2],
    ["gcjs_gqita_da_bian_gg","http://ggzy.hefei.gov.cn/jyxx/002001/002001002/moreinfo_jyxx.html",[  'name', 'ggstart_time', 'href','info'],f1,f2],
    ["gcjs_zhongbiaohx_gg","http://ggzy.hefei.gov.cn/jyxx/002001/002001003/moreinfo_jyxxgs.html",[  'name', 'ggstart_time', 'href','info'],f1,f2],
    ["gcjs_zhongbiao_gg","http://ggzy.hefei.gov.cn/jyxx/002001/002001004/moreinfo_jyxx.html",[  'name', 'ggstart_time', 'href','info'],f1,f2],

    ["zfcg_zhaobiao_gg","http://ggzy.hefei.gov.cn/jyxx/002002/002002001/moreinfo_jyxxgg.html",[ 'name', 'ggstart_time', 'href','info'],f1,f2],
    ["zfcg_gqita_da_bian_gg","http://ggzy.hefei.gov.cn/jyxx/002002/002002002/moreinfo_jyxx.html",[  'name', 'ggstart_time', 'href','info'],f1,f2],
    ["zfcg_zhongbiao_gg","http://ggzy.hefei.gov.cn/jyxx/002002/002002004/moreinfo_jyxxzfcggs.html",[  'name', 'ggstart_time', 'href','info'],f1,f2],
    #
    ["qsy_zhaobiao_gg","http://ggzy.hefei.gov.cn/jyxx/002008/002008001/moreinfo_jyxx.html",[  'name', 'ggstart_time', 'href','info'],f1,f2],
    ["qsy_biangeng_gg","http://ggzy.hefei.gov.cn/jyxx/002008/002008002/moreinfo_jyxx.html",[  'name', 'ggstart_time', 'href','info'],f1,f2],
    ["qsy_gqita_zhong_liu_gg","http://ggzy.hefei.gov.cn/jyxx/002008/002008003/moreinfo_jyxx.html",[  'name', 'ggstart_time', 'href','info'],f1,f2],

    ["qsy_zhaobiao_danyilaiyuan_gg","http://ggzy.hefei.gov.cn/gggs/003003/moreinfo2.html",[  'name', 'ggstart_time', 'href','info'],add_info(f4,{'zbfs':"单一来源"}),f2],
    ["qsy_yucai_gg","http://ggzy.hefei.gov.cn/gggs/003002/moreinfo2.html",[  'name', 'ggstart_time', 'href','info'],f4,f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="安徽省合肥市",**args)
    est_html(conp,f=f3,**args)

if __name__=='__main__':
    conp = ["postgres", "since2015", "192.168.4.175", "anhui", "hefei"]

    work(conp=conp)

