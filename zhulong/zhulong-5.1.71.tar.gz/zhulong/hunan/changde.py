import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write, db_command, db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import json
from zhulong.util.etl import  est_html, est_meta, add_info

_name_ = "changde"




def f1(driver, num):
    locator = (By.XPATH, "//table[@id='MoreinfoList1_DataGrid1']//tr[3]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//div[@id='MoreinfoList1_Pager']//font[@color='red']")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = int(driver.find_element_by_xpath("//div[@id='MoreinfoList1_Pager']//font[@color='red']").text)
    if cnum != num:
        val = driver.find_element_by_xpath("//table[@id='MoreinfoList1_DataGrid1']//tr[3]//a").get_attribute("href")[
              -40:]
        driver.execute_script("__doPostBack('MoreinfoList1$Pager','%d')" % num)
        locator = (By.XPATH, "//table[@id='MoreinfoList1_DataGrid1']//tr[3]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source

    soup = BeautifulSoup(page, "html.parser")

    tb = soup.find("table", id="MoreinfoList1_DataGrid1")

    trs = tb.find_all("tr")  # [2:] if num!=1 else tb.find_all("tr")[1:]
    data = []
    for tr in trs:
        test = tr.text.strip()
        if len(test) < 20: continue
        tds = tr.find_all("td")
        ggstart_time = tds[2].text.strip()
        ggend_time = tds[3].text.strip()
        a = tr.find("a")
        name = a["title"]
        href = "http://jyyw.changde.gov.cn" + a["href"]

        tmp = [name, href, ggstart_time, ggend_time]
        dt = json.dumps({"ggendtime": ggend_time}, ensure_ascii=False)
        tmp.append(dt)

        data.append(tmp)
    df = pd.DataFrame(data=data)

    # df["info"]=
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@id='MoreinfoList1_Pager']")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    txt = driver.find_element_by_xpath("//div[@id='MoreinfoList1_Pager']").text

    total = re.findall("总页数[^0-9]*([0-9]*)", txt)[0]

    total = int(total)

    driver.quit()

    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.ID, "InfoDetail_tblInfo")

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

    table = soup.find('table', id='InfoDetail_tblInfo')

    # div=div.find_all('div',class_='ewb-article')[0]

    return table


data = [

    ["gcjs_zhaobiao_gg", "http://jyyw.changde.gov.cn/cdweb/showinfo/MoreInfoJSGC.aspx?CategoryNum=004001001",
     ["name", "href", "ggstart_time", "ggend_time", "info"], f1, f2],

    ["gcjs_zhaongbiao_gg", "http://jyyw.changde.gov.cn/cdweb/showinfo/MoreInfoJSGC.aspx?CategoryNum=004001002",
     ["name", "href", "ggstart_time", "ggend_time", "info"], f1, f2],

    ["gcjs_biangeng_gg", "http://jyyw.changde.gov.cn/cdweb/showinfo/MoreInfoJSGC.aspx?CategoryNum=004001002",
     ["name", "href", "ggstart_time", "ggend_time", "info"], f1, f2],

    ["zfcg_zhaobiao_gg", "http://jyyw.changde.gov.cn/cdweb/showinfo/MoreInfoJSGC.aspx?CategoryNum=004002001",
     ["name", "href", "ggstart_time", "ggend_time", "info"], f1, f2],

    ["zfcg_zhongbiao_gg", "http://jyyw.changde.gov.cn/cdweb/showinfo/MoreInfoJSGC.aspx?CategoryNum=004002002",
     ["name", "href", "ggstart_time", "ggend_time", "info"], f1, f2],

    ["zfcg_biangeng_gg", "http://jyyw.changde.gov.cn/cdweb/showinfo/MoreInfoJSGC.aspx?CategoryNum=004002003",
     ["name", "href", "ggstart_time", "ggend_time", "info"], f1, f2],

]


# =["postgres","since2015","127.0.0.1","hunan","changde"]
def work(conp, **args):
    est_meta(conp, data=data, diqu="湖南省常德市", **args)
    est_html(conp, f=f3, **args)
if __name__ == '__main__':

    work(conp=["postgres","since2015","192.168.3.171","hunan","changde"],num=3)

# insert_tb('zfcg_biangen_gg',conp=["postgres","since2015","127.0.0.1","hunan","changde"],diqu="湖南省常德市")
