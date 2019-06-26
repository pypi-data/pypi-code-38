import time
from pprint import pprint

import pandas as pd
import re
from collections import OrderedDict
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
from zhulong.util.etl import add_info, est_meta, est_html, est_tbs


_name_ = "guangan"



def f1(driver, num):
    locator = (By.XPATH, '//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, '//*[@id="MoreInfoList1_Pager"]/table/tbody/tr/td[1]/font[3]')
        total = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(total)
    except Exception as e:
        cnum = 1
    if num != cnum:
        val = driver.find_element_by_xpath("//*[@id='MoreInfoList1_DataGrid1']/tbody/tr[1]/td[2]/a").get_attribute('href')[-40:]
        driver.execute_script("javascript:__doPostBack('MoreInfoList1$Pager','{}')".format(num))
        locator = (By.XPATH, "//*[@id='MoreInfoList1_DataGrid1']/tbody/tr[1]/td[2]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    tbody = soup.find("table", id="MoreInfoList1_DataGrid1")
    trs = tbody.find_all("tr")
    data = []
    for tr in trs:
        a = tr.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        td = tr.find_all("td")[2].text.strip()
        link = "http://ggzy.guang-an.gov.cn" + a["href"]
        tmp = [title, td, link]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, '//*[@id="MoreInfoList1_Pager"]/table/tbody/tr/td[1]/font[2]')
        total = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        total = int(total)
    except:
        total = 1
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)
    try:
        time.sleep(1)
        al = driver.switch_to_alert()
        al.accept()
        html = driver.page_source
        if "文件存在问题，请联系管理员!" in html:
            return 404
    except:
        time.sleep(1)
    if "Internal Server Error" in driver.page_source:
        return 404

    locator = (By.XPATH, "//div[@class='content'][string-length()>40]")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    before = len(driver.page_source)
    time.sleep(0.3)
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
    div = soup.find("div", attrs={"class":"content", "style":"text-align:center"})
    return div


def get_data():
    data = []
    # 工程建设部分
    xs = OrderedDict([("市本级", "001"), ("广安区", "002"), ("前锋区", "003"), ("岳池县", "004"),
                      ("武胜县", "005"), ("邻水县", "006"), ("华蓥市", "007")])
    ggtype = OrderedDict([("zhaobiao", "001"), ("biangeng", "002"), ("zgysjg", "003"), ("zhongbiaohx", "004"),
                          ("gqita_zhonghxbiangeng", "005"), ("zhaobiao_jingzheng", "007")])

    for w2 in xs.keys():
        for w1 in ggtype.keys():
            p1 = "009%s" % (xs[w2])
            p2 = "009%s%s" % (xs[w2], ggtype[w1])
            href = "http://ggzy.guang-an.gov.cn/gasggzy/gcjs/%s/%s/MoreInfo.aspx?CategoryNum=%s" % (p1, p2, p2)
            tb = "gcjs_%s_diqu%s_gg" % (w1, xs[w2])
            if tb == 'gcjs_gqita_zhonghxbiangeng_diqu003_gg':
                href = "http://ggzy.guang-an.gov.cn/gasggzy/gcjs/009003/009003006/MoreInfo.aspx?CategoryNum=009003006"
            if tb == 'gcjs_zhaobiao_jingzheng_diqu003_gg':
                href = 'http://ggzy.guang-an.gov.cn/gasggzy/gcjs/009003/009003008/MoreInfo.aspx?CategoryNum=009003008'

            col = ["name", "ggstart_time", "href", "info"]
            info = {"diqu": w2}
            if w1 == 'gqita_zhonghxbiangeng':
                info['gglx']="中标候选人公示变更"
            if w1 == 'zhaobiao_jingzheng':
                info['gglx']="竞争性谈判公告"
            tmp = [tb, href, col, add_info(f1, info), f2]
            data.append(tmp)

    # 政府采购部分
    # 招标
    zbfs = OrderedDict([("zhaobiao", "002"), ("gqita_zhong_liu", "003"), ("biangeng", "004"), ("gqita", "005")])

    for w2 in xs.keys():
        for w1 in zbfs.keys():
            p1 = "010%s" % (xs[w2])
            p2 = "010%s%s" % (xs[w2], zbfs[w1])
            href = "http://ggzy.guang-an.gov.cn/gasggzy/zfcg/%s/%s/MoreInfo.aspx?CategoryNum=%s" % (p1, p2, p2)
            col = ["name", "ggstart_time", "href", "info"]
            tb = "zfcg_%s_diqu%s_gg" % (w1, xs[w2])
            tmp = [tb, href, col, add_info(f1, {"diqu": w2}), f2]
            data.append(tmp)

    # 国有企业
    ggtype2 = OrderedDict([("zhaobiao", "001"), ("biangeng", "002"), ("gqita_zhong_liu", "003"), ("gqita", "004")])
    gq = OrderedDict([("工程建设", "001"), ("企业采购", "002")])

    for w2 in gq.keys():
        for w1 in ggtype2.keys():
            p1 = "012%s" % (gq[w2])
            p2 = "012%s%s" % (gq[w2], ggtype2[w1])
            href = "http://ggzy.guang-an.gov.cn/gasggzy/gyqy/%s/%s/MoreInfo.aspx?CategoryNum=%s" % (p1, p2, p2)
            col = ["name", "ggstart_time", "href", "info"]
            tb = "qsy_%s_lx%s_gg" % (w1, gq[w2])

            tmp = [tb, href, col, add_info(f1, {"lx": w2,"jylx":"国有企业"}), f2]
            data.append(tmp)
    data1 = data.copy()
    return data1
    # 创建data

data = get_data()



def work(conp, **args):
    est_meta(conp, data=data, diqu="四川省广安市",**args)
    est_html(conp,f=f3,**args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "sichuan", "guangan"])




