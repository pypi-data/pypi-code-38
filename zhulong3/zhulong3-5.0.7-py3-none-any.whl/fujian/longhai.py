import time
from collections import OrderedDict
from pprint import pprint

import pandas as pd
import re
import math
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

from zhulong3.util.etl import est_tbs, est_meta, est_html, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]

#
# url = "http://www.fzztb.com/CmsPortalWeb/main/project.xhtml"
# driver = webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_ = 'fujian_longhai'


def f1(driver, num):
    locator = (By.XPATH, '(//table[@width="99%"])[2]//tr[@height="22"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = re.findall('Paging=(\d+)', url)[0]

    if cnum != str(num):
        val = driver.find_element_by_xpath('(//table[@width="99%"])[2]//tr[@height="22"][1]//a').get_attribute('href')[
              -30:]
        url = url.rsplit('=', maxsplit=1)[0] + '=%s' % num
        driver.get(url)

        locator = (
        By.XPATH, '(//table[@width="99%"])[2]//tr[@height="22"][1]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find_all('table', width="99%")[1]
    trs = div.find_all('tr', attrs={"height": '22'})
    for tr in trs:
        tds = tr.find_all('td')

        href = tds[1].a['href']
        name = tds[1].a['title']
        ggstart_time = tds[2].get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.zzgcjyzx.com' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)

    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):

    locator = (By.XPATH, '(//table[@width="99%"])[2]//tr[@height="22"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = int(driver.find_element_by_xpath('//tr[@height="30"]//font[2]/b').text)

    if total > 2:

        url=driver.current_url
        val = driver.find_element_by_xpath('(//table[@width="99%"])[2]//tr[@height="22"][1]//a').get_attribute('href')[
              -30:]
        url = url.rsplit('=', maxsplit=1)[0] + '=%s' % (math.ceil(int(total)/2))
        driver.get(url)

        locator = (
            By.XPATH, '(//table[@width="99%"])[2]//tr[@height="22"][1]//a[not(contains(@href,"{}"))]'.format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        total = driver.find_element_by_xpath('//tr[@height="30"]//font[2]/b').text

    total = int(total)

    driver.quit()

    return total



def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH,
               '//td[@id="TDContent"]')

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

    div = soup.find('td', id="TDContent")


    return div




def get_data():
    data = []

    ggtype2=OrderedDict([('zhaobiao','001'),('dayi','002'),('xianzhijia','003'),('jieguo','004'),('zhongbiao','006')])

    adtype4=OrderedDict([('云霄县','001'),('漳浦县','002'),('诏安县','003'),('长泰县','004'),('东山县','005'),
                         ('南靖县','006'),('平和县','007'),('华安县','008'),('台商','009'),('龙海市','010')])

    adtype1 = OrderedDict([('施工','1'),("监理", "2"), ("勘察设计", "3"), ("其他", "5")])
    adtype2 = OrderedDict([('施工','1'),("监理", "2"), ("勘察设计", "3"), ("其他", "5")])
    adtype3 = OrderedDict([('zhongbiaohx','1'),("zhongbiao", "6"),('xianzhijia','2')])



    #zhaobiao
    for w2 in adtype1.keys():
        href="http://www.zzgcjyzx.com/Front/gcxx/002001/00200100{adtype}/?Paging=1".format(adtype=adtype1[w2])
        tmp=["gcjs_zhaobiao_jytype%s_diqu1_gg"%adtype1[w2],href,["name","ggstart_time","href",'info'],add_info(f1,{"jy_type":w2,"diqu":'市本级'}),f2]
        data.append(tmp)

    #dayi
    for w2 in adtype2.keys():
        href="http://www.zzgcjyzx.com/Front/gcxx/002003/00200300{adtype}/?Paging=1".format(adtype=adtype1[w2])
        tmp=["gcjs_dayi_jytype%s_diqu1_gg"%adtype1[w2],href,["name","ggstart_time","href",'info'],add_info(f1,{"jy_type":w2,"diqu":'市本级'}),f2]
        data.append(tmp)

    #xinxi
    for w2 in adtype3.keys():
        href="http://www.zzgcjyzx.com/Front/gcxx/002002/00200200{adtype}/?Paging=1".format(adtype=adtype3[w2])
        tmp=["gcjs_%s_diqu1_gg"%w2,href,["name","ggstart_time","href",'info'],add_info(f1,{"jy_type":"","diqu":'市本级'}),f2]
        data.append(tmp)

    #quxian
    for w1 in ggtype2.keys():
        for w2 in adtype4.keys():
            href="http://www.zzgcjyzx.com/Front/gcxx/002004/002004{adtype}/002004{adtype}{ggtype}/?Paging=1".format(ggtype=ggtype2[w1],adtype=adtype4[w2])
            tmp=["gcjs_%s_diqu%s_gg"%(w1,int(adtype4[w2])+1),href,["name","ggstart_time","href",'info'],add_info(f1,{"jy_type":"",'diqu':w2}),f2]
            data.append(tmp)

    remove_arr = ["gcjs_zhaobiao_diqu11_gg",'gcjs_dayi_diqu11_gg',"gcjs_xianzhijia_diqu11_gg","gcjs_zhongbiao_diqu11_gg"]
    #
    data1 = data.copy()
    for w in data:
        if w[0] in remove_arr: data1.remove(w)


    return data1



data = get_data()

def work(conp, **args):
    est_meta(conp, data=data, diqu="福建省龙海市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "lch2", "fujian_longhai"])
    # pass