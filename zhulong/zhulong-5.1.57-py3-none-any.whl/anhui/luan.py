
import time
from collections import OrderedDict
from os.path import dirname, join
from pprint import pprint

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
import json

from zhulong.util.etl import est_tbs, est_meta, est_html, gg_existed, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","changsha"]


# url="http://www.szggzyjy.cn/szfront/jyxx/002001/002001001/002001001001/"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)


_name_='luan'


def f1(driver,num):

    locator = (By.XPATH, '//ul[@class="ewb-palte-item"]/li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    cnum=url.rsplit('=',maxsplit=1)[1]
    if int(cnum) != num:
        val = driver.find_element_by_xpath('//ul[@class="ewb-palte-item"]/li[1]//a').get_attribute('href')[-40:-20]

        url=re.sub('Paging=\d+$','Paging=%s'%num,url)

        driver.get(url)

        locator = (By.XPATH, '//ul[@class="ewb-palte-item"]/li[1]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))


    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find_all('li', class_="ewb-plate-list clearfix")

    for tr in trs:
        href = tr.a['href']
        name = tr.a['title']

        ggstart_time = tr.span.get_text()
        if 'http' in href:
            href = href
        else:
            href = 'http://ggjfwpt.luan.gov.cn' + href

        tmp = [name, ggstart_time, href]

        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"] = None

    return df



def f2(driver):

    locator = (By.XPATH, '//ul[@class="ewb-palte-item"]/li[1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total=driver.find_element_by_xpath('//td[@class="huifont"]').text
    total=re.findall('/(\d+)',total)[0]
    total=int(total)
    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@data-role="tab-content" and not(@class)]/div/table | //div[@class="ewb-detail-info"]')

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
    try:
        div = soup.find('div', attrs={'data-role': "tab-content", 'class': ''})
        table = div.find('table')
        div = table.find('td', class_='infodetail')
    except:
        div = soup.find('div', class_="ewb-detail-info")

        if div == None:
            raise ValueError

    return div



def get_data():
    data = []

    ##zhaobiao
    jytype1=OrderedDict([("gcjs","001"),("zfcg","002")])

    #gcjs
    ggtype1 = OrderedDict([("gqita_da_bian", "002"), ("zhongbiaohx", "003"),("gqita_zhong_liu","004")])
    #zfcg
    ggtype2 = OrderedDict([("gqita_da_bian", "002"),("gqita_zhong_liu","003")])
    #qita
    ggtype3 = OrderedDict([ ("gqita_da_bian", "002"),("gqita_zhonghx_liu","003")])

    #feijizhong
    ggtype4 = OrderedDict([("gqita_da_bian", "002"),("gqita_zhong_liu","003")])

    #xiane
    ggtype5 = OrderedDict([("gqita_zhong_liu", "002")])

    ##zfcg_gcjs
    adtype1 = OrderedDict([('市本级','1'),("金安区", "2"), ("裕安区", "3"), ("叶集区", "4"), ("霍山县", "5"),
                           ("霍邱县","6"),('金寨县','7'),("舒城县", "8")])
    #qita
    adtype3 = OrderedDict([('市本级', '1'),  ("叶集区", "4"), ("霍山县", "5"),
                           ("霍邱县", "6"), ('金寨县', '7'), ("舒城县", "8")])
    #feijizhong
    adtype4 = OrderedDict([('市本级', '1'), ("金安区", "7"), ("裕安区", "8"), ("叶集区", "5"), ("霍山县", "2"),
                           ("霍邱县", "6"), ('金寨县', '3'), ("舒城县", "4")])
    #xiane
    adtype5 = OrderedDict([('市本级', '8'), ("金安区", "1"), ("裕安区", "7"), ("叶集区", "2"), ("霍山县", "3"),
                           ("霍邱县", "4"), ('金寨县', '5'), ("舒城县", "6")])

    ##gcjs_zfcg_zhaobiao
    for w1 in jytype1.keys():
        for w2 in adtype1.keys():
            href = "http://ggjfwpt.luan.gov.cn/laztb/ShowInfo/morezbgg.aspx?CategoryNum=002{jy}00{dq}001&Paging=1".format(
                dq=adtype1[w2], jy=jytype1[w1])
            tmp = ["%s_zhaobiao_diqu%s_gg" % (w1, adtype1[w2]), href, ["name", "ggstart_time", "href", 'info'],
                   add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)

    ##jqita_zhaobiao
    for w2 in adtype3.keys():
        href="http://ggjfwpt.luan.gov.cn/laztb/ShowInfo/morezbgg.aspx?CategoryNum=00200500{dq}001&Paging=1".format(
                dq=adtype3[w2])
        tmp = ["jqita_zhaobiao_diqu%s_gg" % ( adtype3[w2]), href, ["name", "ggstart_time", "href", 'info'],
               add_info(f1, {"diqu": w2}), f2]
        data.append(tmp)

    #qsy_feijizhong_zhaobiao1
    for w2 in adtype4.keys():
        href="http://ggjfwpt.luan.gov.cn/laztb/ShowInfo/morezbgg.aspx?CategoryNum=00200600{dq}001&Paging=1".format(
                dq=adtype4[w2])
        tmp = ["qsy_feijizhong_zhaobiao_diqu%s_gg" % ( adtype4[w2]), href, ["name", "ggstart_time", "href", 'info'],
               add_info(f1, {"diqu": w2}), f2]
        data.append(tmp)

    for w2 in adtype5.keys():
        href="http://ggjfwpt.luan.gov.cn/laztb/ShowInfo/morezbgg.aspx?CategoryNum=00200700{dq}001&Paging=1".format(
                dq=adtype5[w2])
        tmp = ["qsy_feijizhong_zhaobiao_diqu%s_gg" % ( adtype5[w2]), href, ["name", "ggstart_time", "href", 'info'],
               add_info(f1, {"diqu": w2}), f2]
        data.append(tmp)


    #gcjs
    for w1 in ggtype1.keys():
        for w2 in adtype1.keys():
            href = "http://ggjfwpt.luan.gov.cn/laztb/jyxx/002001/00200100{dq}/00200100{dq}{jy}/?Paging=1".format(dq=adtype1[w2],jy=ggtype1[w1])
            tmp = ["gcjs_%s_diqu%s_gg" % (w1, adtype1[w2]), href, ["name","ggstart_time","href",'info'],
                   add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)
    #zfcg
    for w1 in ggtype2.keys():
        for w2 in adtype1.keys():
            href = "http://ggjfwpt.luan.gov.cn/laztb/jyxx/002002/00200200{dq}/00200200{dq}{jy}/?Paging=1".format(dq=adtype1[w2],jy=ggtype2[w1])
            tmp = ["zfcg_%s_diqu%s_gg" % (w1, adtype1[w2]), href, ["name","ggstart_time","href",'info'],
                   add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)
    #qita
    for w1 in ggtype3.keys():
        for w2 in adtype3.keys():
            href = "http://ggjfwpt.luan.gov.cn/laztb/jyxx/002005/00200500{dq}/00200500{dq}{jy}/?Paging=1".format(dq=adtype3[w2],jy=ggtype3[w1])
            tmp = ["jqita_%s_diqu%s_gg" % (w1, adtype3[w2]), href, ["name","ggstart_time","href",'info'],
                   add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)


    for w1 in ggtype4.keys():
        for w2 in adtype4.keys():
            href = "http://ggjfwpt.luan.gov.cn/laztb/jyxx/002006/00200600{dq}/00200600{dq}{jy}/?Paging=1".format(dq=adtype4[w2],jy=ggtype4[w1])
            tmp = ["qsy_feijizhong_%s_diqu%s_gg" % (w1, adtype4[w2]), href, ["name","ggstart_time","href",'info'],
                   add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)

    for w1 in ggtype5.keys():
        for w2 in adtype5.keys():
            href = "http://ggjfwpt.luan.gov.cn/laztb/jyxx/002007/00200700{dq}/00200700{dq}{jy}/?Paging=1".format(dq=adtype5[w2],jy=ggtype5[w1])
            tmp = ["qsy_%s_diqu%s_gg" % (w1, adtype5[w2]), href, ["name","ggstart_time","href",'info'],
                   add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)

    remove_arr = ["qsy_feijizhong_gqita_da_bian_diqu4_gg"]
    data1 = data.copy()
    for w in data:
        if w[0] in remove_arr: data1.remove(w)

    data2=[
        ["jqita_gqita_zhong_liu_diqu1_gg","http://ggjfwpt.luan.gov.cn/laztb/jyxx/002005/002005001/002005001004/?Paging=1",
         ["name", "ggstart_time", "href", 'info'], add_info(f1, {"diqu": '市本级'}), f2],
        ['gcjs_zhaobiao_diqu0_gg','http://ggjfwpt.luan.gov.cn/laztb/sjxm/008001/?Paging=1',["name", "ggstart_time", "href", 'info'], add_info(f1, {"diqu":"省级"}), f2],
        ['gcjs_gqita_da_bian_diqu0_gg','http://ggjfwpt.luan.gov.cn/laztb/sjxm/008002/?Paging=1',["name", "ggstart_time", "href", 'info'], add_info(f1, {"diqu":"省级"}), f2],
        ['gcjs_gqita_zhong_liu_diqu0_gg','http://ggjfwpt.luan.gov.cn/laztb/sjxm/008003/?Paging=1',["name", "ggstart_time", "href", 'info'], add_info(f1, {"diqu":"省级"}), f2],
        ['gcjs_yucai_gg','http://ggjfwpt.luan.gov.cn/laztb/bqgs/?Paging=1',["name", "ggstart_time", "href", 'info'], f1, f2],
    ]

    data1.extend(data2)
    return data1

data=get_data()
# pprint(data)

def work(conp,**args):
    est_meta(conp,data=data,diqu="安徽省六安市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':

    work(conp=["postgres", "since2015", "192.168.3.171", "anhui", "luan"])
    pass
