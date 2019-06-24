from threading import Thread

from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

import pandas as pd
from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html, add_info
import time
flag = True
_name_="yancheng"
def f2(driver):
    if "moreinfo_search_fl1_Pager" in driver.page_source:
        locator = (By.XPATH, '//*[@id="moreinfo_search_fl1_Pager"]/table/tbody/tr/td[1]/font')
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
        total_page = int(driver.find_element_by_xpath('//*[@id="moreinfo_search_fl1_Pager"]//td[1]/font[2]/font/b').text)
    else:
        locator = (By.XPATH, '//*[@id="MoreInfoList1_Pager"]//td[1]/font')
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
        total_page = int(driver.find_element_by_xpath('//*[@id="MoreInfoList1_Pager"]//td[1]/font[2]/b').text)
    driver.quit()
    return total_page


def f1(driver, num):
    if "moreinfo_search_fl1_DataGrid1" in driver.page_source:
        locator = (By.ID, "moreinfo_search_fl1_DataGrid1")
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        val = driver.find_element_by_xpath('//*[@id="moreinfo_search_fl1_DataGrid1"]/tbody/tr[1]/td[2]/a').get_attribute("href")[-40:]
        cnum = int(driver.find_element_by_xpath('//*[@id="moreinfo_search_fl1_Pager"]//td[1]/font[3]/font/b').text)
        if int(num) != cnum:
            if "MoreInfoList1$Pager" in driver.page_source:
                driver.execute_script("javascript:__doPostBack('MoreInfoList1$Pager','%s')" % num)
            else:
                driver.execute_script("javascript:__doPostBack('moreinfo_search_fl1$Pager','%s')" % num)
            locator = (
                By.XPATH,
                '//*[@id="moreinfo_search_fl1_DataGrid1"]/tbody/tr[1]/td[2]/a[not(contains(@href,"%s"))]' % val)
            WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
        data = []
        page = driver.page_source
        body = etree.HTML(page)
        content_list = body.xpath("//td[@id='moreinfo_search_fl1_tdcontent']//tr")
        for content in content_list:
            name = content.xpath("./td/a/text()")[0]
            ggstart_time = content.xpath("./td[3]/text()")[0].strip()
            url = "http://ggzy.ycsp.gov.cn" + content.xpath("./td/a/@href")[0]
            temp = [name, ggstart_time, url]
            data.append(temp)
        df = pd.DataFrame(data=data)
        df["info"] = None
        return df
    else:
        locator = (By.ID, "MoreInfoList1_DataGrid1")
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        val = driver.find_element_by_xpath('//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a').get_attribute("href")[-40:]
        cnum = int(driver.find_element_by_xpath('//*[@id="MoreInfoList1_Pager"]//td[1]/font[3]/b').text)
        if int(num) != cnum:
            if "MoreInfoList1$Pager" in driver.page_source:
                driver.execute_script("javascript:__doPostBack('MoreInfoList1$Pager','%s')" % num)
            else:
                driver.execute_script("javascript:__doPostBack('moreinfo_search_fl1$Pager','%s')" % num)
            locator = (By.XPATH,'//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a[not(contains(@href,"%s"))]' % val)
            WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
        data = []
        page = driver.page_source
        body = etree.HTML(page)
        content_list = body.xpath("//td[@id='MoreInfoList1_tdcontent']//tr")
        for content in content_list:
            name = content.xpath("./td/a/text()")[0]
            ggstart_time = content.xpath("./td[3]/text()")[0].strip()
            url = "http://ggzy.ycsp.gov.cn" + content.xpath("./td/a/@href")[0]
            temp = [name, ggstart_time, url]
            data.append(temp)
        df = pd.DataFrame(data=data)
        df["info"] = None
        return df


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@id='tblInfo']")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))

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

    div = soup.find('table', id='tblInfo')
    return div


data = [

    ["gcjs_zhaobiao_gg", "http://ggzy.ycsp.gov.cn/front/showinfo/moreinfo_search.aspx?categoryNum=009&type=001",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg", "http://ggzy.ycsp.gov.cn/front/showinfo/moreinfo_search.aspx?categoryNum=009&type=003",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_kongzhijia_gg", "http://ggzy.ycsp.gov.cn/front/showinfo/moreinfo_search.aspx?categoryNum=009&type=004",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zgysjg_gg", "http://ggzy.ycsp.gov.cn/front/showinfo/moreinfo_search.aspx?categoryNum=009&type=005",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg", "http://ggzy.ycsp.gov.cn/front/showinfo/moreinfo_search.aspx?categoryNum=009&type=006",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_dayi_gg", "http://ggzy.ycsp.gov.cn/front/showinfo/moreinfo_search.aspx?categoryNum=009&type=002",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ##
    ["gcjs_zhaobiao_hwfw_gg", "http://ggzy.ycsp.gov.cn/front/showinfo/moreinfo_search.aspx?categoryNum=010&type=001",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"货物服务"}), f2],

    ["gcjs_zhongbiaohx_hwfw_gg", "http://ggzy.ycsp.gov.cn/front/showinfo/moreinfo_search.aspx?categoryNum=010&type=007",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"货物服务"}), f2],

    ["gcjs_kongzhijia_hwfw_gg", "http://ggzy.ycsp.gov.cn/front/showinfo/moreinfo_search.aspx?categoryNum=010&type=004",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"货物服务"}), f2],

    ["gcjs_liubiao_gg", "http://ggzy.ycsp.gov.cn/front/showinfo/moreinfo_search.aspx?categoryNum=010&type=005",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_hwfw_gg", "http://ggzy.ycsp.gov.cn/front/showinfo/moreinfo_search.aspx?categoryNum=010&type=003",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"货物服务"}), f2],

    ["gcjs_dayi_hwfw_gg", "http://ggzy.ycsp.gov.cn/front/showinfo/moreinfo_search.aspx?categoryNum=010&type=002",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"货物服务"}), f2],
    #
    ["zfcg_zhaobiao_gg", "http://ggzy.ycsp.gov.cn/front/showinfo/moreinfo_search.aspx?categoryNum=011&type=001",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_gqita_zhong_liu_gg", "http://ggzy.ycsp.gov.cn/front/showinfo/moreinfo_search.aspx?categoryNum=011&type=003",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_yucai_gg", "http://ggzy.ycsp.gov.cn/front/showinfo/moreinfo_search.aspx?categoryNum=011&type=004",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_dayi_gg", "http://ggzy.ycsp.gov.cn/front/showinfo/moreinfo_search.aspx?categoryNum=011&type=002",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["yiliao_zhaobiao_gg", "http://ggzy.ycsp.gov.cn/front/yyhcsjcg/021001/MoreInfo.aspx?CategoryNum=021001",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhaobiao_gg", "http://ggzy.ycsp.gov.cn/front/showinfo/moreinfo_search.aspx?categoryNum=013&type=001",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_zhon_zhonghx_gg",
     "http://ggzy.ycsp.gov.cn/front/showinfo/moreinfo_search.aspx?categoryNum=013&type=003",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_dayi_gg",
     "http://ggzy.ycsp.gov.cn/front/showinfo/moreinfo_search.aspx?categoryNum=013&type=002",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["jqita_zhaobiao_zjfb_gg",
     "http://ggzy.ycsp.gov.cn/front/showinfo/moreinfo_search.aspx?categoryNum=013&type=004",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"method":"直接发包"}), f2],

]


def work(conp,**kwargs):
    est_meta(conp, data=data, diqu="江苏省盐城市",**kwargs)
    est_html(conp, f=f3,**kwargs)

#
# 江苏盐城  网站打不开
# date ： 2019年4月4日17:20:45
#




if __name__ == '__main__':
    conp=["postgres", "since2015", "192.168.3.171", "jiangsu", "yancheng"]
    import sys
    arg=sys.argv
    if len(arg) >3:
        work(conp,num=int(arg[1]),total=int(arg[2]),html_total=int(arg[3]))
    elif len(arg) == 2:
        work(conp, html_total=int(arg[1]))
    else:
        work(conp)