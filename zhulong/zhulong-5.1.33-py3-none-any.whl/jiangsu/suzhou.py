import json
import re
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong.util.etl import est_html, est_meta, add_info
import requests
import time

_name_ = 'suzhou'
def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//table[@id="tblInfo"]|//form[@id="detailform"]|//div[@id="body"]')
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
    if div == None:
        div = soup.find('form', id='detailform')
        if div ==None:
            div = soup.find('div', id='body')

    # print(div)
    return div


def f1(driver, num):
    if "zfcg" not in driver.current_url:
        locator = (By.XPATH, '//table[contains(@id,"DataGrid1")]/tbody/tr[contains(@style,"height:30px;")]')
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        val = driver.find_element_by_xpath('//table[contains(@id,"DataGrid1")]/tbody/tr[contains(@style,"height:30px;")][1]/td/a').get_attribute("href")[-60:-20]
        locator = (By.CLASS_NAME, 'huifont')
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
        cnum = driver.find_element_by_class_name('huifont').text.split('/')[0]
        if int(cnum) != int(num):
            url = re.sub(r"Paging=\d+",'Paging='+str(num),driver.current_url)
            driver.get(url)
            locator = (By.XPATH, '//table[contains(@id,"DataGrid1")]/tbody/tr[contains(@style,"height:30px;")][1]/td/a[not(contains(@href,"%s"))]' %(val))
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
        data = []
        page = driver.page_source
        body = etree.HTML(page)
        content_list = body.xpath('//table[contains(@id,"DataGrid1")]/tbody/tr[contains(@style,"height:30px;")]')

        for content in content_list:
            name = content.xpath("./td/a/font/text()")[0].strip()
            url = "http://szzyjy.fwzx.suzhou.gov.cn" + content.xpath("./td/a/@href")[0]
            if "002001" in driver.current_url:
                length_col = len(content.xpath('./td'))
                area = content.xpath("./td[2]/text()")[0].strip()
                ggtype = content.xpath("./td[3]/text()")[0].strip()
                company = content.xpath("./td[4]/text()")[0].strip()
                if length_col == 4:
                    ggstart_time = "网页无时间"
                    info = json.dumps({"area":area,"ggtype":ggtype,"company":company},ensure_ascii=False)

                    temp = [name, ggstart_time, url, info]
                elif length_col == 6:
                    ggstart_time = content.xpath("./td[5]/text()")[0].strip()
                    ggstart_end = content.xpath("./td[6]/text()")[0].strip()

                    info = json.dumps({"area":area,"ggtype":ggtype,"company":company,"ggend_time":ggstart_end},ensure_ascii=False)
                    temp = [name, ggstart_time,  url,info]
                else:
                    ggstart_time = content.xpath("./td[5]/text()")[0].strip()
                    info = json.dumps({"area":area,"ggtype":ggtype,"company":company},ensure_ascii=False)
                    temp = [name, ggstart_time, url,info]

            else:
                ggstart_time = content.xpath("./td[4]/text()")[0].strip()
                info =None
                temp = [name, ggstart_time, url,info]
            data.append(temp)
            # print(temp)
        df = pd.DataFrame(data=data)

        return df
    else:
        locator = (By.XPATH, '//ul[@class="clear hiddencontent"]/li/span/a')
        WebDriverWait(driver, 20,poll_frequency=1).until(EC.presence_of_element_located(locator))
        val = driver.find_element_by_xpath('//ul[@class="clear hiddencontent"]/li/span/a').get_attribute("href")[-20:]
        locator = (By.ID, 'pageIndex')
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
        cnum = driver.find_element_by_id('pageIndex').text
        if int(cnum) != int(num):
            if "cgfsqrgg" in driver.current_url:
                driver.execute_script("changePage(%s, 10,'','')"%num)
            else:
                driver.execute_script("changePage('A','','',0,'','',%s, 30)"%num)

            locator = (By.XPATH,'//ul[@class="clear hiddencontent"]/li/span/a[not(contains(@href,"%s"))]' % (val))
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
        data = []
        page = driver.page_source
        body = etree.HTML(page)
        content_list = body.xpath('//ul[@class="clear hiddencontent"]/li')
        for content in content_list:
            name = content.xpath('./span/a/@title')[0].strip()
            ggstart_time = content.xpath('./span[2]/text()')[0].strip('[').strip(']').strip()
            url = 'http://www.zfcg.suzhou.gov.cn'+content.xpath('./span/a/@href')[0].strip().strip('..')
            temp = [name,ggstart_time,url]
            data.append(temp)
            # print(temp)
        df = pd.DataFrame(data=data)
        df['info'] = None
        return df




def f2(driver):
    if "zfcg" not in driver.current_url:
        locator = (By.CLASS_NAME, 'huifont')
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        total_page = int(driver.find_element_by_class_name('huifont').text.split('/')[1])

    else:
        locator = (By.ID, 'totalPage')
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        total_page = int(driver.find_element_by_id('totalPage').text)
    driver.quit()
    return total_page


data = [
    ["gcjs_zhaobiao_gg", "http://szzyjy.fwzx.suzhou.gov.cn/Front/showinfo/jyzxmore.aspx?title=&QuYu=&ZhaoBiaoLB=&ZiShenType=&StartDate=&EndDate=&CategoryNum=002001001&Paging=1",  #//*[@id="moreinfo_zbgg1_DataGrid1"] 5
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_kongzhijia_gg", "http://szzyjy.fwzx.suzhou.gov.cn/Front/showinfo/zgxjmore.aspx?title=&QuYu=&ZhaoBiaoLB=&StartDate=&EndDate=&CategoryNum=002001003&Paging=2",# //*[@id="moreinfo_zgxj1_DataGrid1"] 6
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zgysjg_gg", "http://szzyjy.fwzx.suzhou.gov.cn/Front/showinfo/zgxjmore.aspx?title=&QuYu=&ZhaoBiaoLB=&StartDate=&EndDate=&CategoryNum=002001002&Paging=1",# //*[@id="moreinfo_zgxj1_DataGrid1"] 6
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://szzyjy.fwzx.suzhou.gov.cn/Front/showinfo/zgxjmore.aspx?title=&QuYu=&ZhaoBiaoLB=&StartDate=&EndDate=&CategoryNum=002001005&Paging=1",# //*[@id="moreinfo_zgxj1_DataGrid1"]
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg", "http://szzyjy.fwzx.suzhou.gov.cn/Front/showinfo/zbgsmore.aspx?title=&QuYu=&ZhaoBiaoLB=&ZhongBiaoDanWei=&StartDate=&EndDate=&CategoryNum=002001006&Paging=1", #//*[@id="moreinfo_zbgs1_DataGrid1"] 无时间
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_biangeng_gg", "http://szzyjy.fwzx.suzhou.gov.cn/Front/showinfo/zgxjmore.aspx?title=&QuYu=&ZhaoBiaoLB=&StartDate=&EndDate=&CategoryNum=002001007&Paging=2",  #//*[@id="moreinfo_zgxj1_DataGrid1"]
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_jiaotong_zhaobiao_gg", "http://szzyjy.fwzx.suzhou.gov.cn/Front/showinfo/gcjs_more.aspx?title=&StartDate=&EndDate=&CategoryNum=002002002&Paging=2", #//*[@id="moreinfo_jsgc1_DataGrid1"]  3 列
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_jiaotong_zhongbiao_gg","http://szzyjy.fwzx.suzhou.gov.cn/Front/showinfo/gcjs_more.aspx?title=&StartDate=&EndDate=&CategoryNum=002002004&Paging=2",#//*[@id="moreinfo_jsgc1_DataGrid1"]
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_jiaotong_zhongbiaohx_gg","http://szzyjy.fwzx.suzhou.gov.cn/Front/showinfo/gcjs_more.aspx?title=&StartDate=&EndDate=&CategoryNum=002002003&Paging=2",#//*[@id="moreinfo_jsgc1_DataGrid1"]
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["gcjs_shuili_kongzhijia_gg", "http://szzyjy.fwzx.suzhou.gov.cn/Front/showinfo/gcjs_more.aspx?title=&StartDate=&EndDate=&CategoryNum=002003003&Paging=2",#//*[@id="moreinfo_jsgc1_DataGrid1"]
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuili_zhaobiao_gg", "http://szzyjy.fwzx.suzhou.gov.cn/Front/showinfo/gcjs_more.aspx?title=&StartDate=&EndDate=&CategoryNum=002003001&Paging=2",#//*[@id="moreinfo_jsgc1_DataGrid1"]
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuili_zhongbiaohx_gg", "http://szzyjy.fwzx.suzhou.gov.cn/Front/showinfo/gcjs_more.aspx?title=&StartDate=&EndDate=&CategoryNum=002003006&Paging=2",#//*[@id="moreinfo_jsgc1_DataGrid1"]
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuili_zhongbiao_gg",
     "http://szzyjy.fwzx.suzhou.gov.cn/Front/showinfo/gcjs_more.aspx?title=&StartDate=&EndDate=&CategoryNum=002003005&Paging=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://www.zfcg.suzhou.gov.cn/html/content.shtml?type=A&title=&choose=&projectType=&zbCode=&appcode=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_cgfs_gg",
     "http://www.zfcg.suzhou.gov.cn/html/channel/cgfsqrgg.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"method":"采购方式确认"}), f2],


]


def work(conp,**kwargs):
    est_meta(conp, data=data, diqu="江苏省苏州市",**kwargs)
    est_html(conp, f=f3,**kwargs)


if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "jiangsu", "suzhou"])
    # driver = webdriver.Chrome()
    # driver.get("http://www.zfcg.suzhou.gov.cn/html/channel/cgfsqrgg.shtml")
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # driver.get("http://www.zfcg.suzhou.gov.cn/html/channel/cgfsqrgg.shtml")
    # f1(driver,3)
    # f1(driver,13)
    # f1(driver,23)
    # f1(driver,33)
    # f1(driver,43)
    # driver.quit()
