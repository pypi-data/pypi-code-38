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
from zhulong.util.etl import add_info,est_meta,est_html,est_tbs


_name_="tongxiang"


def f1(driver, num):
    locator = (By.XPATH, "(//a[@class='ewb-list-name-1'])[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//td[@class='huifont']")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    cnum = re.findall(r'(\d+)/', st)[0]
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("(//a[@class='ewb-list-name-1'])[1]").get_attribute('href')[-40:]
        if "Paging" not in url:
            s = "&Paging=%d" % (num) if num > 1 else "&Paging=1"
            url+=s
        elif num == 1:
            url = re.sub("Paging=[0-9]*", "Paging=1", url)
        else:
            s = "Paging=%d" % (num) if num > 1 else "Paging=1"
            url = re.sub("Paging=[0-9]*", s, url)
        driver.get(url)
        try:
            locator = (By.XPATH, "(//a[@class='ewb-list-name-1'])[1][not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            driver.refresh()
            locator = (By.XPATH, "(//a[@class='ewb-list-name-1'])[1][not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("ul", class_='ewb-dynamic-list')
    trs = table.find_all("li")
    data = []
    for tr in trs:
        info = {}
        a = tr.find("a")
        if a.find('font'):
            gglx = a.find('font').extract().text.strip()
            gglx = re.findall(r'(\w+)', gglx)[0]
            info['gglx'] = gglx
        try:
            title = a["title"].strip()
        except:
            title = a.text.strip()
        td = tr.find("span", class_='ewb-list-date-1').text.strip()
        link = "http://ztb.txggfw.cn"+a['href'].strip()
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:
            info = None
        tmp = [title, td, link, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):
    locator = (By.XPATH, "(//a[@class='ewb-list-name-1'])[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//td[@class='huifont']")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    num = int(re.findall(r'/(\d+)', st)[0])
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='article-content'][string-length()>40]")
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
    div = soup.find('div', class_="article-content")
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://ztb.txggfw.cn/txcms/showinfo/moreinfolist.aspx?categorynum=007001",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_bian_bu_gg",
     "http://ztb.txggfw.cn/txcms/showinfo/moreinfolist.aspx?categorynum=007003",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://ztb.txggfw.cn/txcms/showinfo/moreinfolist.aspx?categorynum=007004",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://ztb.txggfw.cn/txcms/showinfo/moreinfolist.aspx?categorynum=007005",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhaobiao_gg",
     "http://ztb.txggfw.cn/txcms/showinfo/moreinfolist.aspx?categorynum=008001001",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_yucai_gg",
     "http://ztb.txggfw.cn/txcms/showinfo/moreinfolist.aspx?categorynum=008001002",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_gqita_bian_bu_gg",
     "http://ztb.txggfw.cn/txcms/showinfo/moreinfolist.aspx?categorynum=008001003",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhongbiao_gg",
     "http://ztb.txggfw.cn/txcms/showinfo/moreinfolist.aspx?categorynum=008001004",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_hetong_gg",
     "http://ztb.txggfw.cn/txcms/showinfo/moreinfolist.aspx?categorynum=008001005",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ###
    ["qsy_zhaobiao_gg",
     "http://ztb.txggfw.cn/txcms/showinfo/moreinfolist.aspx?categorynum=011002001",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'jylx':'其他交易','gglx':'代发公告'}), f2],

    ["qsy_zhongbiao_gg",
     "http://ztb.txggfw.cn/txcms/showinfo/moreinfolist.aspx?categorynum=011002002",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'jylx':'其他交易','gglx':'代发公示'}), f2],

    ["jqita_zhaobiao_gg",
     "http://ztb.txggfw.cn/txcms/showinfo/moreinfolist.aspx?categorynum=011003001",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'jylx':'镇(街道)交易信息'}), f2],

    ["jqita_zhongbiao_gg",
     "http://ztb.txggfw.cn/txcms/showinfo/moreinfolist.aspx?categorynum=011003002",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'jylx':'镇(街道)交易信息'}), f2],
]


def work(conp,**args):
    est_meta(conp,data=data,diqu="浙江省桐乡市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","zhejiang","tongxiang"])

