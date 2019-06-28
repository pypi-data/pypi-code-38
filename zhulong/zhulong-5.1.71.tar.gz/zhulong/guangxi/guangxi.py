import json
import re
import time

from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong.util.etl import est_meta, est_html, add_info

_name_="guangxi"
def f1(driver,num):
    locator = (By.XPATH,'//*[@id="MoreInfoList1_DataGrid1"]//a')
    WebDriverWait(driver,20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//*[@id="MoreInfoList1_DataGrid1"]//a').text
    cnum = driver.find_element_by_xpath("//font[@color='red']").text
    if int(cnum) != int(num):
        driver.execute_script("javascript:__doPostBack('MoreInfoList1$Pager','%s')"%num)
        locator = (By.XPATH, '//*[@id="MoreInfoList1_DataGrid1"]//a[not(contains(string(),"%s"))]'%val)
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    page = driver.page_source
    body = etree.HTML(page)
    data = []
    content_list = body.xpath('//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr')
    for content in content_list:
        name = content.xpath("./td[2]/a/@title")[0]
        if "/001004004/" in driver.current_url:
            name_temp = content.xpath("./td[2]/a")[0].xpath("string()")
            type = re.findall('\[.*\]',name_temp)
            info = json.dumps({'type':type},ensure_ascii=False)
        else:
            info = None
        ggstart_time = content.xpath("./td[3]/text()")[0].strip()
        url = "http://gxggzy.gxzf.gov.cn" + content.xpath("./td[2]/a/@href")[0]
        temp = [name, ggstart_time, url,info]
        data.append(temp)

    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.ID,"MoreInfoList1_Pager")
    WebDriverWait(driver,20).until(EC.visibility_of_element_located(locator))
    total_page = driver.find_element_by_xpath("//div[@id='MoreInfoList1_Pager']/table//font[2]").text
    driver.quit()
    return int(total_page)

def f3(driver, url):
    driver.get(url)
    locator = (By.ID, "tblInfo")
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
    div = soup.find('table', id='tblInfo')
    return div


data =[

    ["gcjs_fangjianshizheng_zhaobiao_gg",
     "http://gxggzy.gxzf.gov.cn/gxzbw/jyxx/001001/001001001/MoreInfo.aspx?CategoryNum=001001001",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"房建市政"}), f2],
    ["gcjs_fangjianshizheng_biangeng_gg",
     "http://gxggzy.gxzf.gov.cn/gxzbw/jyxx/001001/001001002/MoreInfo.aspx?CategoryNum=001001002",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"房建市政"}), f2],
    ["gcjs_fangjianshizheng_kongzhijia_gg",
     "http://gxggzy.gxzf.gov.cn/gxzbw/jyxx/001001/001001004/MoreInfo.aspx?CategoryNum=001001004",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"房建市政"}), f2],
    ["gcjs_fangjianshizheng_zhongbiaohx_gg",
     "http://gxggzy.gxzf.gov.cn/gxzbw/jyxx/001001/001001005/MoreInfo.aspx?CategoryNum=001001005",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"房建市政"}), f2],
    ["gcjs_fangjianshizheng_zhongbiao_gg",
     "http://gxggzy.gxzf.gov.cn/gxzbw/jyxx/001001/001001006/MoreInfo.aspx?CategoryNum=001001006",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"房建市政"}), f2],

    ["gcjs_tielu_zhaobiao_gg",
     "http://gxggzy.gxzf.gov.cn/gxzbw/jyxx/001010/001010001/MoreInfo.aspx?CategoryNum=001010001",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"铁路"}), f2],
    ["gcjs_tielu_biangeng_gg",
     "http://gxggzy.gxzf.gov.cn/gxzbw/jyxx/001010/001010002/MoreInfo.aspx?CategoryNum=001010002",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"铁路"}), f2],
    ["gcjs_tielu_kongzhijia_gg",
     "http://gxggzy.gxzf.gov.cn/gxzbw/jyxx/001010/001010003/MoreInfo.aspx?CategoryNum=001010003",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"铁路"}), f2],
    ["gcjs_tielu_zhongbiaohx_gg",
     "http://gxggzy.gxzf.gov.cn/gxzbw/jyxx/001010/001010004/MoreInfo.aspx?CategoryNum=001010004",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"铁路"}), f2],
    ["gcjs_tielu_zhongbiao_gg",
     "http://gxggzy.gxzf.gov.cn/gxzbw/jyxx/001010/001010005/MoreInfo.aspx?CategoryNum=001010005",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"铁路"}), f2],
    #

    ["gcjs_shuili_zhaobiao_gg",
     "http://gxggzy.gxzf.gov.cn/gxzbw/jyxx/001011/001011001/MoreInfo.aspx?CategoryNum=001011001",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"水利"}), f2],
    ["gcjs_shuili_zhongbiaohx_gg",
     "http://gxggzy.gxzf.gov.cn/gxzbw/jyxx/001011/001011002/MoreInfo.aspx?CategoryNum=001011002",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"水利"}), f2],
    ["gcjs_shuili_zhongbiao_gg",
     "http://gxggzy.gxzf.gov.cn/gxzbw/jyxx/001011/001011005/MoreInfo.aspx?CategoryNum=001011005",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"水利"}), f2],
    ["gcjs_shuili_biangeng_gg",
     "http://gxggzy.gxzf.gov.cn/gxzbw/jyxx/001011/001011003/MoreInfo.aspx?CategoryNum=001011003",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"水利"}), f2],

    ["gcjs_jiaotong_zhaobiao_gg",
     "http://gxggzy.gxzf.gov.cn/gxzbw/jyxx/001012/001012001/MoreInfo.aspx?CategoryNum=001012001",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"交通"}), f2],
    ["gcjs_jiaotong_biangeng_gg",
     "http://gxggzy.gxzf.gov.cn/gxzbw/jyxx/001012/001012002/MoreInfo.aspx?CategoryNum=001012002",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"交通"}), f2],
    ["gcjs_jiaotong_kongzhijia_gg",
     "http://gxggzy.gxzf.gov.cn/gxzbw/jyxx/001012/001012003/MoreInfo.aspx?CategoryNum=001012003",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"交通"}), f2],
    ["gcjs_jiaotong_zhongbiao_gg",
     "http://gxggzy.gxzf.gov.cn/gxzbw/jyxx/001012/001012004/MoreInfo.aspx?CategoryNum=001012004",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"交通"}), f2],
    ["gcjs_jiaotong_zhongbiaohx_gg",
     "http://gxggzy.gxzf.gov.cn/gxzbw/jyxx/001012/001012005/MoreInfo.aspx?CategoryNum=001012005",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"交通"}), f2],

    ["zfcg_zhaobiao_gg",
     "http://gxggzy.gxzf.gov.cn/gxzbw/jyxx/001004/001004001/MoreInfo.aspx?CategoryNum=001004001",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://gxggzy.gxzf.gov.cn/gxzbw/jyxx/001004/001004002/MoreInfo.aspx?CategoryNum=001004002",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://gxggzy.gxzf.gov.cn/gxzbw/jyxx/001004/001004004/MoreInfo.aspx?CategoryNum=001004004",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["yiliao_zhaobiao_gg",
     "http://gxggzy.gxzf.gov.cn/gxzbw/jyxx/001009/001009001/MoreInfo.aspx?CategoryNum=001009001",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["yiliao_zhongbiao_gg",
     "http://gxggzy.gxzf.gov.cn/gxzbw/jyxx/001009/001009002/MoreInfo.aspx?CategoryNum=001009002",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["yiliao_biangeng_gg",
     "http://gxggzy.gxzf.gov.cn/gxzbw/jyxx/001009/001009003/MoreInfo.aspx?CategoryNum=001009003",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]

def work(conp,**arg):
    est_meta(conp, data=data, diqu="广西省",**arg)
    est_html(conp, f=f3,**arg)



if __name__ == "__main__":
    conp=["postgres", "since2015", "192.168.3.171", "guangxi", "guangxi"]
    work(conp)