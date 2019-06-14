import json
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

_name_ = 'jiangsu_yangzhou'


def f1(driver, num):
    locator = (By.XPATH, '//font[@color="red"][2]/b')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath("//table[contains(@id,'List1_DataGrid1')]/tbody/tr[1]/td[2]/a").get_attribute("onclick")[-100:-80]
    cnum_temp = driver.find_element_by_xpath('//font[@color="red"][2]/b').text
    cnum = re.findall(r'(\d)+\/', cnum_temp)[0]
    locator = (By.XPATH, "//table[contains(@id,'List1_DataGrid1')]/tbody/tr")

    if int(cnum) != int(num):
        if "ChangePM" in driver.current_url:
            driver.execute_script("javascript:__doPostBack('MoreChangePMList1$Pager','%s')"%num)
        elif "ZhongBiao" in driver.current_url:
            driver.execute_script("javascript:__doPostBack('MoreZhongBiaoGSList1$Pager','%s')"%num)
        elif "ZiGeYS" in driver.current_url:
            driver.execute_script("javascript:__doPostBack('MoreZiGeYSList1$Pager','%s')"%num)
        else:
            driver.execute_script("javascript:__doPostBack('MoreInfoList1$Pager','%s')"%num)
        locator = (By.XPATH, "//table[contains(@id,'List1_DataGrid1')]//tr[1]/td/a[not(contains(@onclick,'%s'))]" % val)
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//table[contains(@id,'List1_DataGrid1')]//tr")
    for content in content_list:
        try:
            name = content.xpath("./td[2]/a/@title")[0].strip()+content.xpath("./td[2]/font/text()")[0].strip()
        except:
            name = content.xpath("./td[2]/a/@title")[0].strip()
        url = driver.current_url.rsplit('/',maxsplit=1)[0] + '/' + re.findall(r'\(\"(.*?)\"', content.xpath("./td[2]/a/@onclick")[0].strip())[0]
        project_type = content.xpath("./td[last()-1]/text()")[0].strip()
        ggstart_time = content.xpath("./td[last()]/text()")[0].strip()
        info = json.dumps({'project_type':project_type},ensure_ascii=False)
        
        temp = [name, ggstart_time, url, info]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, '//font[@color="red"][2]/b')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_temp = driver.find_element_by_xpath('//font[@color="red"][2]/b').text
    total_page = re.findall(r'\/(\d+)', total_temp)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    time.sleep(0.1)
    if "404" in driver.page_source:
        return "404 - 找不到文件或目录。"
    locator = (By.XPATH, '//table[@id="Table1"]')
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
    div = soup.find('table', id='Table1')
    return div



data = [
    ["gcjs_zhaobiao_gg",
     "http://www.yzcetc.com/yzcetc/YW_Info/ZaoBiaoReport/MoreReportList_YZ_New.aspx?CategoryNum=003",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zgysjg_gg",
     "http://www.yzcetc.com/yzcetc/YW_Info/ZiGeYS/MoreYSList.aspx?CategoryNum=003",
     ["name", "ggstart_time", "href",  "info"], f1, f2],
    ["gcjs_kongzhijia_gg",
     "http://www.yzcetc.com/yzcetc/YW_Info/ZuiGaoXJ/MoreZGXJList.aspx?CategoryNum=003",
     ["name", "ggstart_time", "href",  "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://www.yzcetc.com/yzcetc/YW_Info/ZhongBiaoHXRGS/MoreHXRGSList_YZ_New.aspx?CategoryNum=003",
     ["name", "ggstart_time", "href",  "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://www.yzcetc.com/yzcetc/YW_Info/ZhongBiaoGS/MoreGSList_YZ_New.aspx?CategoryNum=003",
     ["name", "ggstart_time", "href",  "info"], f1, f2],

    ["gcjs_zhaobiao_zjfb_gg",
     "http://www.yzcetc.com/yzcetc/YW_info/ZhongBiaoGS/MoreGSList_YZ_ZJ.aspx?categoryNum=003",
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{'Tag':'直接发包'}), f2],
    ["gcjs_zhongbiao_zhuanye_gg",
     "http://www.yzcetc.com/yzcetc/YW_Info/ZhongBiaoGS/MoreGSList_ZhuanYe.aspx?CategoryNum=003",
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{'Tag':'专业中标公示'}), f2],
    ["gcjs_gqita_pmbiangeng_gg",
     "http://www.yzcetc.com/yzcetc/YW_Info/ChangePM/MorePMChangeList.aspx?CategoryNum=003",
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{'Tag':'项目经理变更'}), f2],



]


def work(conp, **args):
    est_meta(conp, data=data, diqu="江苏省扬州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "jiangsu_yangzhou"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://www.yzcetc.com/yzcetc/YW_Info/ZhongBiaoGS/MoreGSList_YZ_New.aspx?CategoryNum=003")
    # for i in range(1,10):f1(driver,i)
    # print('-'*20)
    # driver.get("http://www.yzcetc.com/yzcetc/YW_Info/ZaoBiaoReport/MoreReportList_YZ_New.aspx?CategoryNum=003")
    # for i in range(1,10):f1(driver,i)
    # print('-'*20)
    # driver.get("http://www.yzcetc.com/yzcetc/YW_Info/ZuiGaoXJ/MoreZGXJList.aspx?CategoryNum=003")
    # for i in range(1,10):f1(driver,i)
    # print('-'*20)
    # driver.get("http://www.yzcetc.com/yzcetc/YW_Info/ChangePM/MorePMChangeList.aspx?CategoryNum=003")
    # for i in range(1,10):f1(driver,i)
    # driver = webdriver.Chrome()
    # print(f3(driver, 'http://www.yzcetc.com/yzcetc/YW_Info/ZaoBiaoReport/ViewReportDetail_New_Now.aspx?GongGaoGuid=GG_f7aff6dd-0f52-4bab-9aca-44ae0c1b7297&categoryNum=003&siteid=1'))
    # driver.close()
    # driver.quit()
