import pandas as pd
import re
from lxml import etree
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


_name_="panzhihua"


def f1_data(driver, num):
    url = driver.current_url
    locator = (By.XPATH, "//ul[@class='news_list']/li[1]/a")
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-30:]
    try:
        cnum = re.findall(r'PageIndex=(\d+)&', url)[0]
    except:
        cnum = 1

    if num != int(cnum):
        if "PageIndex" not in url:
            s = "&PageIndex=%d" % (num) if num > 1 else "&PageIndex=1"
            url = url + s
        elif num == 1:
            url = re.sub("PageIndex=[0-9]*", "PageIndex=1", url)
        else:
            s = "PageIndex=%d" % (num) if num > 1 else "PageIndex=1"
            url = re.sub("PageIndex=[0-9]*", s, url)
        driver.get(url)
        try:
            locator = (
            By.XPATH, "//ul[@class='news_list']/li[1]/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            driver.refresh()
            locator = (By.XPATH, "//ul[@class='news_list']/li[1]/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("ul", class_='news_list')
    trs = table.find_all("li")
    data = []
    for tr in trs:
        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        link = "http://ggzy.panzhihua.gov.cn:8009" + a['href'].strip()
        td = tr.find("span", class_="date").text.strip()
        tmp = [title, td, link]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f1(driver, num):
    url = driver.current_url
    if 'http://ggzy.panzhihua.gov.cn:8009/' in url:
        df = f1_data(driver, num)
        return df
    locator = (By.XPATH, "//li[@class='clearfloat']/table/tbody/tr[2]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//a[@class='cur']")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//li[@class='clearfloat']/table/tbody/tr[2]/td/a").get_attribute('href')[-35:]
        driver.execute_script('pagination({});return false;'.format(num))
        try:
            locator = (By.XPATH, "//li[@class='clearfloat']/table/tbody/tr[2]/td/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            driver.refresh()
            locator = (By.XPATH, "//li[@class='clearfloat']/table/tbody/tr[2]/td/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("li", class_='clearfloat')
    table = table.find('table')
    trs = table.find_all("tr")
    data = []
    for tr in trs[1:]:
        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        link = "http://www.pzhggzy.cn" + a['href'].strip()
        tds = tr.find_all("td")
        if len(tds)<=4:
            ggstart_time=tds[3].text.strip()
        else:
            hx=[tds[-1].text.strip(),tds[-2].text.strip()]
            ggstart_time= hx[0] if re.search('[0-9]{2}-',hx[0]) else hx[1]


        tmp = [title, ggstart_time, link]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df



def f2(driver):
    url = driver.current_url
    if 'http://ggzy.panzhihua.gov.cn:8009/' in url:
        locator = (By.XPATH, "//ul[@class='news_list']/li[1]/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, "//div[@class='page_bar']/a[last()]")
            trs = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')
            num = re.findall(r'PageIndex=(\d+)&', trs)[0]
        except:
            num = 1
        driver.quit()
        return int(num)
    else:
        locator = (By.XPATH, "//li[@class='clearfloat']/table/tbody/tr[2]/td/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, "//div[@class='mmggxlh']/a[last()-1]")
            num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        except:
            num = 1
        driver.quit()
        return int(num)



def f3(driver, url):
    driver.get(url)
    try:
        alart = driver.switch_to.alert
        alart.accept()
    except:
        pass
    locator = (By.XPATH, "//div[@class='container'] | //div[@class='main_con']")
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
    div = soup.find('div', class_='content_all_nr')
    if div == None:
        div = soup.find('div', class_='con')
    return div



data = [

    ["gcjs_zhaobiao_gg",
     "http://www.pzhggzy.cn/jyxx/jsgcZbgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_bian_bu_gg",
     "http://www.pzhggzy.cn/jyxx/jsgcBgtz",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zgysjg_gg",
     "http://www.pzhggzy.cn/jyxx/jsgcKbjl",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.pzhggzy.cn/jyxx/jsgcpbjggs",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_zhonghxbiangeng_gg",
     "http://www.pzhggzy.cn/jyxx/jsgcZbhxrbggs",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gglx':'评标结果变更公示'}), f2],

    ["gcjs_zhongbiao_gg",
     "http://www.pzhggzy.cn/jyxx/jsgcZbjggs",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_hetong_gg",
     "http://www.pzhggzy.cn/jyxx/jsgcHtgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_liubiao_gg",
     "http://www.pzhggzy.cn/jyxx/jsgcZbyc",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://www.pzhggzy.cn/jyxx/zfcg/cggg",
    ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_biangeng_gg",
     "http://www.pzhggzy.cn/jyxx/zfcg/gzsx",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://www.pzhggzy.cn/jyxx/zfcg/zbjggs",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_liubiao_gg",
     "http://www.pzhggzy.cn/jyxx/zfcg/zfcgYcgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["qsy_zhaobiao_gg",
     "http://www.pzhggzy.cn/jyxx/qtjy/crgg",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'jylx':'其他交易'}), f2],

    ["qsy_biangeng_gg",
     "http://www.pzhggzy.cn/jyxx/qtjy/bytz",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'其他交易'}), f2],

    ["qsy_gqita_zhong_liu_gg",
     "http://www.pzhggzy.cn/jyxx/qtjy/cjqr",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'其他交易'}), f2],
     #
    ["zfcg_zhaobiao_wsjj_gg",
     "http://ggzy.panzhihua.gov.cn:8009/JyWeb/TradeInfo/XuQiuGongGaoGetList?PageIndex=1&PageSize=20&XinXiType=10&XinXiSubType=1&XiangMu_Area=0&X-Requested-With=XMLHttpRequest&_=1543886123743",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zblx':'网上竞价'}), f2],

    ["zfcg_zhongbiao_wsjj_gg",
     "http://ggzy.panzhihua.gov.cn:8009/JyWeb/TradeInfo/ChengJiaoGongGaoGetList?PageIndex=1&PageSize=20&XinXiType=10&XinXiSubType=2&XiangMu_Area=0&X-Requested-With=XMLHttpRequest&_=1543886123746",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zblx':'网上竞价'}), f2],

    ["zfcg_biangeng_wsjj_gg",
     "http://ggzy.panzhihua.gov.cn:8009/JyWeb/TradeInfo/BianGengGongGaoGetList?PageIndex=1&PageSize=20&XinXiType=10&XinXiSubType=4&XiangMu_Area=0&X-Requested-With=XMLHttpRequest&_=1543838563469",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zblx':'网上竞价'}), f2],

    ["zfcg_liubiao_wsjj_gg",
     "http://ggzy.panzhihua.gov.cn:8009/JyWeb/TradeInfo/JingJiaShiBaiShanPinGetList?PageIndex=1&PageSize=20&XinXiType=10&XinXiSubType=5&XiangMu_Area=0&X-Requested-With=XMLHttpRequest&_=1543886123748",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zblx':'网上竞价'}), f2],
]



def work(conp,**args):
    est_meta(conp,data=data,diqu="四川省攀枝花市",**args)
    est_html(conp,f=f3,**args)

# 修改时间：2019/6/27
# 需要在设置headless=None，不然gcjs_zhaobiao_gg没有数据，故应在Windows上跑
if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","sichuan","panzhihua"],headless=None)


