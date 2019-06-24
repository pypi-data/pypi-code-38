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


# url="http://ggzyjy.rkzszf.gov.cn/col/col918/index.html?uid=3919&pageNum=1"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_='rikaze'

def f1(driver,num):
    locator = (By.XPATH, '//div[@class="default_pgContainer"]/ul/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url

    if re.findall('html$',url):
        cnum=1
    else:
        cnum = url.rsplit('=', maxsplit=1)[1]

    if int(cnum) != num:
        main_url = url.rsplit('=', maxsplit=1)[0]
        val = driver.find_element_by_xpath('//div[@class="default_pgContainer"]/ul/li[1]/a').get_attribute(
            "href")[-20:]
        url = main_url + '=' + str(num)

        driver.get(url)

        locator = (By.XPATH, '//div[@class="default_pgContainer"]/ul/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='default_pgContainer')
    lis = div.find_all('li')
    for li in lis:
        href = li.a['href']
        name = li.a.get_text()
        ggstart_time = li.find('span').get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://ggzyjy.rkzszf.gov.cn' + href

        tmp = [name, href, ggstart_time]
        data.append(tmp)

    df=pd.DataFrame(data=data)
    df['info']=None
    return df



def f2(driver):
    locator = (By.XPATH, '//div[@class="default_pgContainer"]/ul/li[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    if re.findall('html$',url):
        total=1
    else:
        page = driver.find_element_by_xpath('//span[@class="default_pgTotalPage"]').text
        total=int(page)

    driver.quit()
    return total

def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@id="zoom"][string-length()>10]')

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
    div = soup.find('div', id="zoom")

    return div

data=[
    #包含,招标,中标
    ["gcjs_gqita_zhao_zhong_gg","http://ggzyjy.rkzszf.gov.cn/col/col918/index.html?uid=3919&pageNum=1",[ "name", "href", "ggstart_time","info"],f1,f2],
    #包含招标,流标
    ["gcjs_gqita_zhao_liu_gg","http://ggzyjy.rkzszf.gov.cn/col/col910/index.html?uid=4015&pageNum=1",[ "name", "href", "ggstart_time","info"],f1,f2],
    ["zfcg_zhaobiao_gg","http://ggzyjy.rkzszf.gov.cn/col/col1034/index.html",[ "name", "href", "ggstart_time","info"],f1,f2],
    ["zfcg_biangeng_gg","http://ggzyjy.rkzszf.gov.cn/col/col1035/index.html",[ "name", "href", "ggstart_time","info"],f1,f2],
    ["zfcg_liubiao_gg","http://ggzyjy.rkzszf.gov.cn/col/col1036/index.html",[ "name", "href", "ggstart_time","info"],f1,f2],

]

def work(conp,**args):
    est_meta(conp,data=data,diqu="西藏自治区日喀则市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':

    conp=["postgres","since2015","192.168.4.175","xizang","rikaze"]

    work(conp=conp,headless=False,num=1)