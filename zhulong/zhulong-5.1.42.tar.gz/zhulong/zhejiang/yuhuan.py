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


_name_="yuhuan"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='filter-content']/ul/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//li[@class='active']/a")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(st)
    except:
        cnum = 1
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@class='filter-content']/ul/li[1]/a").get_attribute('href')[-30:]
        if "pageIndex" not in url:
            s = "?pageIndex=%d" % (num) if num > 1 else "?pageIndex=1"
            url = url + s
        elif num == 1:
            url = re.sub("pageIndex=[0-9]*", "pageIndex=1", url)
        else:
            s = "pageIndex=%d" % (num) if num > 1 else "pageIndex=1"
            url = re.sub("pageIndex=[0-9]*", s, url)
        driver.get(url)
        try:
            locator = (By.XPATH, "//div[@class='filter-content']/ul/li[1]/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            driver.refresh()
            locator = (By.XPATH, "//div[@class='filter-content']/ul/li[1]/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("div", class_="filter-content")
    ul = table.find("ul")
    trs = ul.find_all("li")
    data = []
    for tr in trs:
        a = tr.find("a")
        try:
            title = a["title"].strip()
        except:
            title = a.text.strip()
        link = a["href"]
        td = tr.find("span", class_="time").text.strip()
        span = re.findall(r'(\d+/\d+/\d+)', td)[0]
        links = "https://www.yhjyzx.com"+link.strip()
        tmp = [title, span, links]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='filter-content']/ul/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//*[@id='bootstrappager']/li[last()]/a")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')
        num = re.findall(r'pageIndex=(\d+)', str)[0]
    except:
        num = 1
    driver.quit()
    return int(num)



def f3(driver, url):
    if "DetailTransactionInfo" in url:
        driver.get(url)
        locator = (By.XPATH, "//div[@class='inner-main-content']")
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
        div = soup.find('div', class_="inner-main-content")
        return div
    else:
        driver.get(url)
        locator = (By.XPATH, "//div[@class='inner-main-content'][string-length()>30] | //div[@class='nTab'][string-length()>30]")
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
        div = soup.find('div', class_="details-content")
        if div == None:
            div = soup.find('div', class_='nTab')
        return div


data = [
    ["gcjs_gqita_yuzhaobiao_gg",
     "https://www.yhjyzx.com/TransactionInfo/jsgc/xmdjxx",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'gglx':'项目信息'}),f2],

    ["gcjs_zhaobiao_gg",
     "https://www.yhjyzx.com/BidNotice/jsgc/zbgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_biangeng_gg",
     "https://www.yhjyzx.com/BidNotice/jsgc/bggg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_kaibiao_gg",
     "https://www.yhjyzx.com/BidNotice/jsgc/kbqk",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "https://www.yhjyzx.com/BidNotice/jsgc/zbhxrgs",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "https://www.yhjyzx.com/BidNotice/jsgc/zbjggg",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_hetong_gg",
     "https://www.yhjyzx.com/TransactionInfo/jsgc/ht",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_zbtzs_gg",
     "https://www.yhjyzx.com/TransactionInfo/jsgc/zbtzs",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'gglx':'中标通知书'}), f2],

    ["gcjs_gqita_yanshou_gg",
     "https://www.yhjyzx.com/TransactionInfo/jsgc/lyqk",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #####

    ["zfcg_gqita_yuzhaobiao_gg",
     "https://www.yhjyzx.com/TransactionInfo/zfcg/xmxx",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'gglx':'项目信息'}), f2],

    ["zfcg_yucai_gg",
     "https://www.yhjyzx.com/BidNotice/zfcg/zqyj",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhaobiao_gg",
     "https://www.yhjyzx.com/BidNotice/zfcg/cggg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "https://www.yhjyzx.com/BidNotice/zfcg/bggg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_kaibiao_gg",
     "https://www.yhjyzx.com/BidNotice/zfcg/kbjggg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiaohx_gg",
     "https://www.yhjyzx.com/BidNotice/zfcg/cjhxrgs",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhongbiao_gg",
     "https://www.yhjyzx.com/BidNotice/zfcg/zbjggg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_liubiao_gg",
     "https://www.yhjyzx.com/BidNotice/zfcg/fbgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_zhaobiao_gg",
     "https://www.yhjyzx.com/BidNotice/gyqywzcg/zbgg",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'国有企业物资采购'}), f2],

    ["qsy_biangeng_gg",
     "https://www.yhjyzx.com/BidNotice/gyqywzcg/gzgg",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'国有企业物资采购'}), f2],

    ["qsy_zhongbiao_gg",
     "https://www.yhjyzx.com/BidNotice/gyqywzcg/cjgg",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx':'国有企业物资采购'}), f2],
    ###
    ["qsy_gqita_yuzhaobiao_bumen_gg",
     "https://www.yhjyzx.com/TransactionInfo/bmzb/xmxx",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'部门自行交易','gglx':'项目信息'}), f2],

    ["qsy_zhaobiao_bumen_gg",
     "https://www.yhjyzx.com/BidNotice/bmzb/zbgg",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'部门自行交易'}), f2],

    ["qsy_biangeng_bumen_gg",
     "https://www.yhjyzx.com/BidNotice/bmzb/gzgg",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'部门自行交易'}), f2],

    ["qsy_zhongbiaohx_bumen_gg",
     "https://www.yhjyzx.com/BidNotice/bmzb/cjhxrgs",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx': '部门自行交易'}), f2],
    ###
    ["jqita_zhaobiao_gg",
     "https://www.yhjyzx.com/BidNotice/qtggzyjy/hysyq/zbgg",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx': '其它公共资源交易'}), f2],

    ["jqita_zhongbiaohx_gg",
     "https://www.yhjyzx.com/BidNotice/qtggzyjy/hysyq/cjhxrgs",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx': '其它公共资源交易'}), f2],

    ["jqita_zhongbiao_gg",
     "https://www.yhjyzx.com/BidNotice/qtggzyjy/hysyq/cjgg",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx': '其它公共资源交易'}), f2],
    ###
    ["jqita_zhaobiao_xiangzhen_gg",
     "https://www.yhjyzx.com/BidNotice/Qtxm/xxgg",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx': '乡镇平台交易'}), f2],

    ["jqita_biangeng_xiangzhen_gg",
     "https://www.yhjyzx.com/BidNotice/Qtxm/gzgg",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx': '乡镇平台交易'}), f2],

    ["jqita_zhongbiaohx_xiangzhen_gg",
     "https://www.yhjyzx.com/BidNotice/Qtxm/cjhxrgs",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx': '乡镇平台交易'}), f2],

    ["jqita_zhongbiao_xiangzhen_gg",
     "https://www.yhjyzx.com/BidNotice/Qtxm/cjgg",
     ["name", "ggstart_time", "href", "info"],add_info(f1, {'jylx': '乡镇平台交易'}), f2],
]


def work(conp,**args):
    est_meta(conp,data=data,diqu="浙江省玉环市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","zhejiang","yuhuan"])


