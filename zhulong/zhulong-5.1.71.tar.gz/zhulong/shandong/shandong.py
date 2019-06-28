import time
import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from zhulong.util.etl import add_info,est_meta,est_html,est_tbs
from collections import OrderedDict


_name_="shandong"


def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='ewb-list']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        locator = (By.XPATH, "//ul[@class='m-pagination-page']/li[@class='active']")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        cnum = 1
    if num != int(cnum):
        if "moreinfo" in url:
            s = "/%d.html" % (num) if num > 1 else "/moreinfo.html"
            url = re.sub("/moreinfo\.html", s, url)
        elif num == 1:
            url = re.sub("/[0-9]*\.html", "/moreinfo.html", url)
        else:
            s = "/%d.html" % (num) if num > 1 else "/moreinfo.html"
            url = re.sub("/[0-9]*\.html", s, url)
        val = driver.find_element_by_xpath("//ul[@class='ewb-list']/li[1]/a").get_attribute('href')[-35:]
        driver.get(url)
        locator = (By.XPATH, "//ul[@class='ewb-list']/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    ul = soup.find("ul", class_="ewb-list")
    lis = ul.find_all("li")
    data = []
    for li in lis:
        a = li.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        link = "http://www.sdsggzyjyzx.gov.cn" + a["href"]
        span = li.find("span", class_="ewb-list-date").text.strip()
        tmp = [title, span, link]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"]=None
    return df


def f2(driver):
    locator = (By.XPATH, "//ul[@class='ewb-list']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//ul[@class='m-pagination-page']/li[last()]")
        page = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        page = 1
    driver.quit()
    return int(page)


def f3(driver,url):
    driver.get(url)
    locator=(By.XPATH,"//div[@class='ewb-article'][string-length()>30]")
    WebDriverWait(driver,10).until(EC.presence_of_all_elements_located(locator))
    before=len(driver.page_source)
    time.sleep(0.1)
    after=len(driver.page_source)
    i=0
    while before!=after:
        before=len(driver.page_source)
        time.sleep(0.1)
        after=len(driver.page_source)
        i+=1
        if i>5:break
    page=driver.page_source
    soup=BeautifulSoup(page,'html.parser')
    div=soup.find('div',class_='ewb-article')
    return div



data = [
        ["gcjs_zhaobiao_gg", "http://www.sdsggzyjyzx.gov.cn/003/003004/003004001/moreinfo.html",
         ["name", "ggstart_time", "href", "info"], f1, f2],

        ["gcjs_zhongbiao_gg", "http://www.sdsggzyjyzx.gov.cn/003/003004/003004002/moreinfo.html",
         ["name", "ggstart_time", "href", "info"], f1, f2],
        #
        ["zfcg_zhaobiao_gg", "http://www.sdsggzyjyzx.gov.cn/003/003001/003001001/moreinfo.html",
         ["name", "ggstart_time", "href","info"],f1,f2],
        #
        ["zfcg_zhongbiao_gg", "http://www.sdsggzyjyzx.gov.cn/003/003001/003001002/moreinfo.html",
         ["name", "ggstart_time", "href","info"],f1,f2],
        #
        ["zfcg_biangeng_gg", "http://www.sdsggzyjyzx.gov.cn/003/003001/003001003/moreinfo.html",
         ["name", "ggstart_time", "href", "info"], f1, f2],

        ["yiliao_gqita_yiyaocaigou_tongzhi_gg", "http://www.sdsggzyjyzx.gov.cn/003/003002/003002001/moreinfo.html",
         ["name", "ggstart_time", "href","info"],add_info(f1,{'jylx':'医药采购','gglx':'通知'}),f2],
        #
        ["yiliao_gqita_yiyaocaigou_gg", "http://www.sdsggzyjyzx.gov.cn/003/003002/003002002/moreinfo.html",
         ["name", "ggstart_time", "href","info"],add_info(f1,{'jylx':'医药采购'}),f2],
        #
        ["yiliao_gqita_haocaicaigou_tongzhi_gg","http://www.sdsggzyjyzx.gov.cn/003/003005/003005001/moreinfo.html",
         ["name", "ggstart_time", "href","info"],add_info(f1,{'jylx':'耗材采购','gglx':'通知'}),f2],

        ["yiliao_gqita_haocaicaigou_gg", "http://www.sdsggzyjyzx.gov.cn/003/003005/003005002/moreinfo.html",
         ["name", "ggstart_time", "href","info"],add_info(f1,{'jylx':'耗材采购'}),f2],

        ["yiliao_gqita_yimiaocaigou_tongzhi_gg", "http://www.sdsggzyjyzx.gov.cn/003/003006/003006001/moreinfo.html",
         ["name", "ggstart_time", "href","info"],add_info(f1,{'jylx':'疫苗采购','gglx':'通知'}),f2],

        ["yiliao_gqita_yimiaocaigou_gg", "http://www.sdsggzyjyzx.gov.cn/003/003006/003006002/moreinfo.html",
         ["name", "ggstart_time", "href","info"],add_info(f1,{'jylx':'疫苗采购'}),f2],

    ]



def work(conp,**args):
    est_meta(conp,data=data,diqu="山东省省会")
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","shandong","shandong"])


# 网址变更：http://www.sdsggzyjyzx.gov.cn/003/003004/003004001/moreinfo.html
# 修改时间：2019/5/16