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


from zhulong.util.etl import est_tbs, est_meta, est_html, est_gg, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hengyang.gov.cn/jyxx/jsgc/zbgg_64796/index.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_='xizang'

def f1(driver,num):
    locator = (By.XPATH, '//ul[@class="x-main-jr-top-content"]/li[1]/p/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum = re.findall('PAGE=(\d+?)', url)[0]

    if int(cnum) != num:
        val = driver.find_element_by_xpath('//ul[@class="x-main-jr-top-content"]/li[1]/p/a').get_attribute('href')[-30:-5]
        main_url = url.rsplit('=', maxsplit=1)[0]
        url = main_url + '=' + str(num)
        driver.get(url)

        locator = (By.XPATH, '//ul[@class="x-main-jr-top-content"]/li[1]/p/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('ul', class_='x-main-jr-top-content')
    lis = div.find_all('li')
    for li in lis:
        href = li.p.a['href']
        name = li.p.a.get_text()
        ggstart_time = li.find('span', class_='jr-t-date').get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.xzzbtb.gov.cn' + href

        tmp = [name, href, ggstart_time]
        data.append(tmp)

    df=pd.DataFrame(data=data)
    df['info']=None
    return df



def f2(driver):
    locator = (By.XPATH, '//ul[@class="x-main-jr-top-content"]/li[1]/p/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath('//div[@class="pagination"]').text
    page = re.findall('/(\d+)页', page)[0]
    total=int(page)
    driver.quit()
    return total

def f4(driver,num):
    locator = (By.XPATH, '//div[@class="c1-body"]/div[1]/div[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    if 'index.jhtml' in url:
        cnum=1
    else:
        cnum = re.findall('index_(\d+)\.jhtml', url)[0]

    if int(cnum) != num:
        val = driver.find_element_by_xpath('//div[@class="c1-body"]/div[1]/div[1]/a').get_attribute('href')[-15:-5]
        main_url=url.rsplit('/',maxsplit=1)[0]
        if num == 1:
            url=main_url+'/index.jhtml'
        else:
            url=main_url+'/index_'+str(num)+'.jhtml'
        driver.get(url)

        locator = (By.XPATH, '//div[@class="c1-body"]/div[1]/div[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='c1-body')
    lis = div.find_all('div',class_='c1-bline')
    for li in lis:
        href = li.find('div',class_='f-left').a['href']
        name = li.find('div',class_='f-left').a['title']
        ggstart_time = li.find('div',class_='f-right').get_text()


        if 'http' in href:
            href = href
        else:
            href = 'http://www.xzcs.gov.cn' + href

        tmp = [name, href, ggstart_time]
        data.append(tmp)

    df = pd.DataFrame(data=data)
    df['info'] = None
    return df

def f5(driver):
    locator = (By.XPATH, '//div[@class="c1-body"]/div[1]/div[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath('//div[@class="pagination"]').text
    page = re.findall('/(\d+)页', page)[0]
    total = int(page)
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)
    try:
        mark=0
        driver.switch_to.frame('main')
    except:
        mark=1
    try:
        locator = (By.XPATH, '//div[@id="myPrintArea"] | //div[@class="x-main-news-content"]')
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    except:
        if mark == 0:
            locator = (By.XPATH, '/html/body')
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        else:
            raise TimeoutError

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
    driver.switch_to.parent_frame()

    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', id="myPrintArea")
    if div==None:
        div=soup.find('div', class_="x-main-news-middle")
        if div == None:
            if mark == 0:
                div = soup.find('body')
            else:
                raise ValueError

    return div

data=[
    #
    ["gcjs_zhaobiao_1_gg","http://www.xzzbtb.gov.cn/xz/publish-notice!tenderNoticeView.do?PAGE=1",[ "name", "href", "ggstart_time","info"],f1,f2],
    ["gcjs_zhaobiao_lasa_gg","http://www.xzzbtb.gov.cn/xz/publish-notice!sccinNoticeView.do?PAGE=1",[ "name", "href", "ggstart_time","info"],add_info(f1,{"diqu":"拉萨市"}),f2],
    ["gcjs_zhongbiaohx_gg","http://www.xzzbtb.gov.cn/xz/publish-notice!preAwardNoticeView.do?PAGE=1",[ "name", "href", "ggstart_time","info"],f1,f2],


    ["gcjs_zhaobiao_2_gg","http://www.xzcs.gov.cn/zbggzbgg/index.jhtml",[ "name", "href", "ggstart_time","info"],f4,f5],
    ["gcjs_zhongbiao_gg","http://www.xzcs.gov.cn/zhbgg/index.jhtml",[ "name", "href", "ggstart_time","info"],f4,f5],

]

def work(conp,**args):
    est_meta(conp,data=data,diqu="西藏自治区西藏",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","xizang","xizang"]

    work(conp=conp,)
