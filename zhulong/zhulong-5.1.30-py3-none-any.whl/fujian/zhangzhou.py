from collections import OrderedDict
from os.path import dirname, join
import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write,db_command,db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import json
from zhulong.util.etl import add_info, est_meta, est_html, est_tbs, gg_existed
from zhulong.util.conf import get_conp

_name_="zhangzhou"





def f1(driver, num):
    url = driver.current_url
    locator = (By.XPATH, "//table[@width='99%']/tbody/tr[1]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//td[@valign='bottom']/font[3]/b")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(st)
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@width='99%']/tbody/tr[1]/td/a").get_attribute('href')[-40:]
        if "?Paging" not in url:
            s = "?Paging=%d" % (num) if num > 1 else "?Paging=1"
            url = url + s
        elif num == 1:
            url = re.sub("Paging=[0-9]*", "Paging=1", url)
        else:
            s = "Paging=%d" % (num) if num > 1 else "Paging=1"
            url = re.sub("Paging=[0-9]*", s, url)
            # print(cnum)
        driver.get(url)
        locator = (By.XPATH, "//table[@width='99%']/tbody/tr[1]/td/a[not(contains(@href, '{}'))]".format(val))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table", width='99%')
    trs = table.find_all("tr", height="22")
    data = []
    for tr in trs:
        a = tr.find('a')
        try:
            title = a["title"].strip()
        except:
            title = a.text.strip()

        link = a["href"].strip()
        if 'http' in link:
            href = link
        else:
            href = "http://www.zzgcjyzx.com"+link
        td = tr.find("td", width="80").text.strip()
        tmp = [title, td, href]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f2(driver):
    url = driver.current_url
    time.sleep(2)
    if ('本栏目暂时没有内容' in driver.page_source) or ('404' in driver.title):
        return 0
    num = int(driver.find_element_by_xpath("//td[@valign='bottom']/font[2]/b").text.strip())
    if num == 0:
        return 0
    locator = (By.XPATH, "//table[@width='99%']/tbody/tr[1]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//td[@align='notset']/a[last()]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        num = int(driver.find_element_by_xpath("//td[@valign='bottom']/font[2]/b").text.strip())
        for _ in range(num-1):
            try:
                locator = (By.XPATH, "//table[@width='99%']/tbody/tr[1]/td/a")
                WebDriverWait(driver, 5).until(EC.presence_of_element_located(locator))
                locator = (By.XPATH, "//td[@valign='bottom']/font[3]/b")
                str_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
                num = int(str_1)
                break
            except:
                time.sleep(1)
                driver.find_element_by_xpath("//img[@src='/Front//images/page/prevn.gif']").click()
    except:
         num = int(driver.find_element_by_xpath("//td[@valign='bottom']/font[2]/b").text.strip())
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    time.sleep(1)
    if ('404' in driver.title) or ('抱歉，系统发生了错误' in driver.page_source):
        return 404
    locator = (By.XPATH, "//table[@id='tblInfo'][string-length()>10]")
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
    div = soup.find('table', id="tblInfo")
    # div=div.find_all('div',class_='ewb-article')[0]
    return div


def get_data():
    data = []
    # 工程建设部分
    xs = OrderedDict([("云霄县", "001"), ("漳浦县 ", "002"), ("诏安县", "003"), ("长泰县", "004"), ("东山县", "005"), ("南靖县", "006"),
                      ("平和县", "007"), ("华安县", "008"), ("台商(角美)", "009"), ("龙海市", "010")])
    # "http://www.bzggzyjy.gov.cn/bzweb/002/002004/002004001/"
    ggtype = OrderedDict([("zhaobiao", "001"), ("gqita_bian_da", "002"), ("kongzhijia", "003"), ("zhongbiaohx", "004"), ("zsjg", "005"), ("zhongbiao", "006")])

    for w1 in xs.keys():
        for w2 in ggtype.keys():
            p1 = "002004%s" % (xs[w1])
            p2 = "002004%s%s" % (xs[w1], ggtype[w2])
            href = "http://www.zzgcjyzx.com/Front/gcxx/002004/%s/%s/" % (p1, p2)

            tb = "gcjs_%s_diqu%s_gg" % (w2, xs[w1])
            col = ["name", "ggstart_time", "href", "info"]
            tmp = [tb, href, col, add_info(f1, {"diqu": w1}), f2]
            data.append(tmp)

    data1 = data.copy()
    remove_arr = []
    for w in data:
        if w[0] in remove_arr: data1.remove(w)
    return data1
    # 创建data

data1 = get_data()



data2 = [

    ["gcjs_zhaobiao_shigong_gg",
     "http://www.zzgcjyzx.com/Front/gcxx/002001/002001001/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gctype':"施工"}),f2],

    ["gcjs_zhaobiao_jianli_gg",
     "http://www.zzgcjyzx.com/Front/gcxx/002001/002001002/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gctype':"监理"}),f2],

    ["gcjs_zhaobiao_sheji_gg",
     "http://www.zzgcjyzx.com/Front/gcxx/002001/002001003/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gctype':"设计"}), f2],

    ["gcjs_zhaobiao_qita_gg",
     "http://www.zzgcjyzx.com/Front/gcxx/002001/002001005/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ###
    ["gcjs_gqita_bian_da_shigong_gg",
     "http://www.zzgcjyzx.com/Front/gcxx/002003/002003001/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_bian_da_jianli_gg",
     "http://www.zzgcjyzx.com/Front/gcxx/002003/002003002/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_bian_da_sheji_gg",
     "http://www.zzgcjyzx.com/Front/gcxx/002003/002003003/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_bian_da_qita_gg",
     "http://www.zzgcjyzx.com/Front/gcxx/002003/002003005/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ###
    ["gcjs_gqita_zhong_liu_gg",
     "http://www.zzgcjyzx.com/Front/gcxx/002002/002002001/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://www.zzgcjyzx.com/Front/gcxx/002002/002002006/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_kongzhijia_gg",
     "http://www.zzgcjyzx.com/Front/gcxx/002002/002002002/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]

data = data1 + data2


def work(conp,**args):
    est_meta(conp,data=data,diqu="福建省漳州市",**args)
    est_html(conp,f=f3,**args)



if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","fujian","zhangzhou"])

    # driver=webdriver.Chrome()
    # url = "http://www.zzgcjyzx.com/Front/gcxx/002003/002003005/"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    # driver = webdriver.Chrome()
    # url = "http://www.zzgcjyzx.com/Front/gcxx/002003/002003005/"
    # driver.get(url)
    # for i in range(1, 3):
    #     df=f1(driver, i)
    #     print(df.values)
    #     for m in df[2].values:
    #         f = f3(driver, m)
    #         print(f)
