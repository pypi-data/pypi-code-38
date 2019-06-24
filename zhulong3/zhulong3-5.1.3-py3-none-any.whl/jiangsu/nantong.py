import math
import re

import requests
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong3.util.etl import est_html, est_meta, add_info
import time

_name_ = 'jiangsu_nantong'


def f1(driver, num):
    locator = (By.XPATH, '//font[@color="red"][2]/b |//font[@color="blue"][2]/b')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val_temp = driver.find_element_by_xpath("//table[contains(@id,'ist1_DataGrid1')]/tbody/tr[1]/td[2]/a").get_attribute("onclick")
    # print(val_temp)
    if val_temp == None:
        val = driver.find_element_by_xpath("//table[contains(@id,'ist1_DataGrid1')]/tbody/tr[1]/td[2]/a").get_attribute("href")[-60:]
    elif "window.open" in val_temp:
        val = val_temp[-120:-80]
    else:
        val = val_temp[-30:]
    cnum_temp = driver.find_element_by_xpath('//font[@color="red"][2]/b |//font[@color="blue"][2]/b').text
    if '/' not in cnum_temp:
        cnum = driver.find_element_by_xpath('//font[@color="red"]/b').text
    else:
        cnum = re.findall(r'(\d)+\/', cnum_temp)[0]
    locator = (By.XPATH, "//table[contains(@id,'ist1_DataGrid1')]/tbody/tr")
    # print('val',val)
    if int(cnum) != int(num):
        if "ZaoBiao" in driver.current_url:
            driver.execute_script("javascript:__doPostBack('MoreXiangMuList1$Pager','%s')"%num)
        elif "ZhongBiao" in driver.current_url:
            driver.execute_script("javascript:__doPostBack('morezhongbiaolist1$Pager','%s')"%num)
        elif "ZiGeYS" in driver.current_url or "ZuiGaoXJ" in driver.current_url:
            driver.execute_script("javascript:__doPostBack('MoreZGYSGSList1$Pager','%s')"%num)
        else:
            driver.execute_script("javascript:__doPostBack('MoreInfoList1$Pager','%s')"%num)
        locator = (By.XPATH, '//table[contains(@id,"ist1_DataGrid1")]//tr[1]/td/a[not(contains(@onclick,"%s"))]|//table[contains(@id,"ist1_DataGrid1")]//tr[1]/td/a[not(contains(@href,"%s"))]' % (val,val))
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//table[contains(@id,'ist1_DataGrid1')]//tr")
    for content in content_list:
        name = content.xpath("./td[2]/a/text()")[0].strip()
        url_temp = content.xpath("./td[2]/a/@onclick")
        # print(url_temp)
        if "ZiGeYS" in driver.current_url:
            try:
                try:
                    # print(re.findall(r"\'(.+?)\'",url_temp[0]))
                    rowId,bdguid = re.findall(r"\'(.+?)\'",url_temp[0])
                    url = "http://www.ntcetc.cn/ntztb/YW_Info/ZiGeYS/ViewZGYSDetailNew.aspx?RowID=%s&bdguid=%s"%(rowId,bdguid)
                except:
                    rowId = re.findall(r"\'(.+?)\'",url_temp[0])
                    # print(rowId[0])
                    url = "http://www.ntcetc.cn/ntztb/YW_Info/ZiGeYS/ViewZGYSDetail.aspx?RowID=%s"%rowId[0]
            except:
                url ="无正确的url"
        elif url_temp == []:
            url = content.xpath("./td[2]/a/@href")[0]
        elif "window.open" in url_temp[0]:
            if "ZuiGaoXJ" in driver.current_url and "http://www.ntcetc.cn" not in url_temp:
                url = "http://www.ntcetc.cn/ntztb/YW_Info/ZuiGaoXJ/" + re.findall(r'\"(.*?)\"', content.xpath("./td[2]/a/@onclick")[0].strip())[0]
            else:
                url = re.findall(r'\"(.*?)\"', content.xpath("./td[2]/a/@onclick")[0].strip())[0]
        else:
            url = ("http://www.ntcetc.cn/ntztb/YW_Info/ZaoBiaoReport/XiangMuZhuanYeGongGao.aspx?ID=" if "ZhongBiao" not in driver.current_url else "http://www.ntcetc.cn/ntztb/YW_Info/ZhongBiaoGS/ZhongBiaoDetailInfo.aspx?ID=") + re.findall(r'(\d+)', content.xpath("./td[2]/a/@onclick")[0].strip())[0]
        if url.count('www')>1:url ='http://www' + url.rsplit('www')[-1]
        ggstart_time = content.xpath("./td[last()]/text()")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(url,name)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//font[@color="red"][2]/b |//font[@color="blue"][2]/b')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_temp = driver.find_element_by_xpath('//font[@color="red"][2]/b |//font[@color="blue"][2]/b').text
    if '/' in total_temp:
        total_page = re.findall(r'\/(\d+)', total_temp)[0]
    else:
        total_page=total_temp
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//form[@id="Form1"]|//table[@id="Table1"]')
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
    soup = BeautifulSoup(page, 'lxml')

    div = soup.find('table',id='Table1')
    if not div:
        div = soup.find('table', id='InfoDetail1_tblInfo')
        if not div:div = soup.find('form', id='Form1')
    return div



data = [
    ["gcjs_zhaobiao_gg",
     "http://www.ntcetc.cn/ntztb/YW_Info/ZaoBiaoReport/MoreReportList_NT_CopyCZ.aspx?CategoryNum=002",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zgysjg_gg",
     "http://www.ntcetc.cn/ntztb/YW_Info/ZiGeYS/MoreYSList_FromCZ.aspx?categoryNum=006",
     ["name", "ggstart_time", "href",  "info"], f1, f2],
    ["gcjs_kongzhijia_gg",
     "http://www.ntcetc.cn/ntztb/YW_Info/ZuiGaoXJ/MoreZGXJList.aspx",
     ["name", "ggstart_time", "href",  "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://www.ntcetc.cn/ntztb/ShowInfo/moreinfo.aspx?categoryNum=018",
     ["name", "ggstart_time", "href",  "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://www.ntcetc.cn/ntztb/YW_Info/ZhongBiaoGS/MoreResultList_NT_CopyCZ.aspx",
     ["name", "ggstart_time", "href",  "info"], f1, f2],

    ["gcjs_gqita_pmbiangeng_gg",
     "http://www.ntcetc.cn/ntztb/ShowInfo/moreinfo.aspx?categoryNum=012",
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{'Tag':'项目经理变更'}), f2],



]


def work(conp, **args):
    est_meta(conp, data=data, diqu="江苏省南通市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "jiangsu_nantong"]
    work(conp,num=25,pageloadtimeout=50)
    # driver = webdriver.Chrome()
    # driver.get("http://www.ntcetc.cn/ntztb/YW_Info/ZiGeYS/MoreYSList_FromCZ.aspx?categoryNum=006")
    # f1(driver, 4)
    # f1(driver, 10)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://www.ntcetc.cn/ntztb/YW_Info/ZaoBiaoReport/XiangMuZhuanYeGongGao.aspx?ID=59236'))
    # driver.close()
