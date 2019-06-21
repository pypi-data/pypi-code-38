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


from zhulong2.util.etl import est_tbs, est_meta, est_html, est_gg, est_meta_large

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hengyang.gov.cn/jyxx/jsgc/zbgg_64796/index.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_='hunan_changde'


def f1(driver,num):

    locator = (By.XPATH, '//div[@class="list-group"]/a[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath('//ul[@class="pagination"]/li[last()]/span').text.strip()

    cnum = re.findall('当前第(\d+?)页', cnum)[0]

    if int(cnum) != num:

        val = driver.find_element_by_xpath('//div[@class="list-group"]/a[1]').get_attribute('href')[-15:]

        driver.execute_script("javascript:goPage({});".format(num-1))

        locator = (By.XPATH, '//div[@class="list-group"]/a[1][not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='list-group')
    ass = div.find_all('a', recursive=False)
    for li in ass:

        href = li['href']
        name = li.h5.get_text().strip()
        name = re.findall('.+? ', name)[0].strip()

        ggstart_time = li.h5.small.get_text()
        ggstart_time = re.findall('\d+年\d+月\d+日', ggstart_time)[0]
        ul = li.find('ul', class_="list-inline")
        trs = ul.find_all('li')
        address = trs[0].get_text()
        pm = trs[1].get_text()
        cg_type = trs[2].get_text()
        cgr = trs[3].get_text()
        dljg = trs[4].get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://changd.ccgp-hunan.gov.cn' + href
        info={'diqu':address,'gclx':pm,'zbfs':cg_type,'cgdw':cgr,'zbdl':dljg}
        info=json.dumps(info,ensure_ascii=False)
        tmp = [name, ggstart_time,  href,info]

        data.append(tmp)

    df=pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="list-group"]/a[1]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total = driver.find_element_by_xpath('//ul[@class="pagination"]/li[last()]/span').text.strip()

    total = re.findall('共(.+?)页', total)[0].replace(',','')
    total = int(total)

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="container" and @style="background:#FFFFFF;"]/div[2][string-length()>10]')

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
    div1 = soup.find('div', attrs={"class": "container", "style": "background:#FFFFFF;"})
    div2 = div1.find_next_sibling('div', class_="container")
    div = str(div1) + str(div2)
    div = BeautifulSoup(div, 'html.parser')

    return div


def chang(f,num1):
    def wrap(*arg):
        driver=arg[0]
        locator = (By.XPATH, '//div[@class="list-group"]/a[1]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            driver.find_element_by_xpath('//a[@class="btn btn-default btn-danger"]')
        except:
            cnum = driver.find_element_by_xpath('//ul[@class="pagination"]/li[last()]/span').text.strip()
            cnum=re.findall('共.+?页',cnum)[0]
            driver.find_element_by_xpath('//table[@class="table table-bordered  table-striped  table-condensed"]//tr[2]//a[{num1}]'.format(num1=num1)).click()
            locator = (By.XPATH, '//ul[@class="pagination"]/li[last()]/span[not(contains(text(),"%s"))]' % cnum)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*arg)
    return wrap


data=[

    ["zfcg_zhaobiao_gg","http://changd.ccgp-hunan.gov.cn/f/m/noticechannel/c_2",["name", "ggstart_time",  "href",'info'],chang(f1,2),chang(f2,2)],
    ["zfcg_zgys_gg","http://changd.ccgp-hunan.gov.cn/f/m/noticechannel/c_2",["name", "ggstart_time",  "href",'info'],chang(f1,3),chang(f2,3)],
    ["zfcg_zhongbiao_gg","http://changd.ccgp-hunan.gov.cn/f/m/noticechannel/c_2",["name", "ggstart_time",  "href",'info'],chang(f1,4),chang(f2,4)],
    ["zfcg_biangeng_gg","http://changd.ccgp-hunan.gov.cn/f/m/noticechannel/c_2",["name", "ggstart_time",  "href",'info'],chang(f1,5),chang(f2,5)],

    ## f1中 info中有zbfs,不用在此加info
    ["zfcg_zhaobiao_danyilaiyuan_gg","http://changd.ccgp-hunan.gov.cn/f/m/noticechannel/c_2",["name", "ggstart_time",  "href",'info'],chang(f1,6),chang(f2,6)],
    ["zfcg_zhaobiao_jingjia_gg","http://changd.ccgp-hunan.gov.cn/f/m/noticechannel/c_2",["name", "ggstart_time",  "href",'info'],chang(f1,7),chang(f2,7)],

]

def work(conp,**args):
    est_meta(conp,data=data,diqu="湖南省常德市",**args)
    est_html(conp,f=f3,**args)



if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","lch","hunan_changde"]

    work(conp=conp,headless=False,num=1,cdc_total=1)