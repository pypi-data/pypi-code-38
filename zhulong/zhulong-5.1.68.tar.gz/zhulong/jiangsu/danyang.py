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
_name_="danyang"
def f3(driver, url):
    driver.get(url)
    try:
        locator = (By.ID, "tblInfo")
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        flag = True
    except:
        locator = (By.CLASS_NAME, "container")
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        flag = False
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
    if flag:
        div = soup.find('table', id='tblInfo')
    else:
        div = soup.find('div', class_='container')
    return div


def f1(driver, num):
    locator = (By.XPATH, '//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a').get_attribute("href")[-50:]
    locator = (By.ID, 'MoreInfoList1_Pager')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    cnum = driver.find_element_by_xpath('//*[@id="MoreInfoList1_Pager"]/table/tbody/tr/td[1]/font[3]/b').text
    if int(cnum) != int(num):
        driver.execute_script("javascript:__doPostBack('MoreInfoList1$Pager','%s')" % num)
        locator = (
        By.XPATH, '//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
    locator = (By.XPATH, '//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr')
    WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr')
    for content in content_list:
        name = content.xpath("./td[2]/a/text()")[0].strip()
        if name == '[':name = content.xpath("./td[2]/a")[0].xpath('string(.)').strip()
        ggstart_time = content.xpath("./td[3]/text()")[0].strip()
        url = "http://www.dyzgw.com.cn" + content.xpath("./td[2]/a/@href")[0]
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//*[@id="MoreInfoList1_Pager"]/table/tbody/tr/td[1]/font[2]/b')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    total_page = int(driver.find_element_by_xpath('//*[@id="MoreInfoList1_Pager"]/table/tbody/tr/td[1]/font[2]/b').text)
    driver.quit()
    return total_page


data = [

    ["gcjs_zhaobiao_gg", "http://www.dyzgw.com.cn/dyzgw/jyxx/001001/001001001/MoreInfo.aspx?CategoryNum=001001001",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zgysjg_gg", "http://www.dyzgw.com.cn/dyzgw/jyxx/001001/001001006/MoreInfo.aspx?CategoryNum=001001006",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://www.dyzgw.com.cn/dyzgw/jyxx/001001/001001007/MoreInfo.aspx?CategoryNum=001001007",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg", "http://www.dyzgw.com.cn/dyzgw/jyxx/001001/001001005/MoreInfo.aspx?CategoryNum=001001005",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_biangeng_gg", "http://www.dyzgw.com.cn/dyzgw/jyxx/001001/001001002/MoreInfo.aspx?CategoryNum=001001002",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_kongzhijia_gg", "http://www.dyzgw.com.cn/dyzgw/jyxx/001001/001001004/MoreInfo.aspx?CategoryNum=001001004",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_yucai_gg", "http://www.dyzgw.com.cn/dyzgw/jyxx/001004/001004007/MoreInfo.aspx?CategoryNum=001004007",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_gg", "http://www.dyzgw.com.cn/dyzgw/jyxx/001004/001004001/MoreInfo.aspx?CategoryNum=001004001",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_jingjia_gg", "http://www.dyzgw.com.cn/dyzgw/jyxx/001004/001004008/MoreInfo.aspx?CategoryNum=001004008",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg", "http://www.dyzgw.com.cn/dyzgw/jyxx/001004/001004002/MoreInfo.aspx?CategoryNum=001004002",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg", "http://www.dyzgw.com.cn/dyzgw/jyxx/001004/001004005/MoreInfo.aspx?CategoryNum=001004005",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_yucai_bumen_gg",
     "http://www.dyzgw.com.cn/dyzgw/jyxx/001013/001013006/MoreInfo.aspx?CategoryNum=001013006",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":'部门'}), f2],
    ["zfcg_zhaobiao_bumen_gg",
     "http://www.dyzgw.com.cn/dyzgw/jyxx/001013/001013001/MoreInfo.aspx?CategoryNum=001013001",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":'部门'}), f2],
    ["zfcg_biangeng_bumen_gg", "http://www.dyzgw.com.cn/dyzgw/jyxx/001013/001013003/MoreInfo.aspx?CategoryNum=001013003",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":'部门'}), f2],
    ["zfcg_zhongbiao_bumen_gg",
     "http://www.dyzgw.com.cn/dyzgw/jyxx/001013/001013004/MoreInfo.aspx?CategoryNum=001013004",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":'部门'}), f2],

    ["gcjs_shuili_jiaotong_zhaobiao_gg",
     "http://www.dyzgw.com.cn/dyzgw/jyxx/001012/001012001/MoreInfo.aspx?CategoryNum=001012001",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"gctype":"水利,交通"}), f2],
    ["gcjs_shuili_jiaotong_zhongbiao_gg",
     "http://www.dyzgw.com.cn/dyzgw/jyxx/001012/001012002/MoreInfo.aspx?CategoryNum=001012002",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"gctype":"水利,交通"}), f2],
    ["gcjs_shuili_jiaotong_kongzhijia_gg",
     "http://www.dyzgw.com.cn/dyzgw/jyxx/001012/001012004/MoreInfo.aspx?CategoryNum=001012004",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"gctype":"水利,交通"}), f2],
    ["gcjs_shuili_jiaotong_biangeng_gg",
     "http://www.dyzgw.com.cn/dyzgw/jyxx/001012/001012003/MoreInfo.aspx?CategoryNum=001012003",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"gctype":"水利,交通"}), f2],

    ["jqita_zhaobiao_1_gg", "http://www.dyzgw.com.cn/dyzgw/jyxx/001014/001014001/MoreInfo.aspx?CategoryNum=001014001",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"综合交易"}), f2],
    ["jqita_zhaobiao_2_gg", "http://www.dyzgw.com.cn/dyzgw/jyxx/001014/001014002/MoreInfo.aspx?CategoryNum=001014002",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"综合交易"}), f2],




    ["gcjs_zhaobiao_zhen_gg", "http://www.dyzgw.com.cn/dyzgw/jyxx/001010/001010001/MoreInfo.aspx?CategoryNum=001010001",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area":"镇级项目"}), f2],
    ["gcjs_biangeng_zhen_gg", "http://www.dyzgw.com.cn/dyzgw/jyxx/001010/001010002/MoreInfo.aspx?CategoryNum=001010002",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area":"镇级项目"}), f2],

    ["gcjs_zhongbiao_zhen_gg", "http://www.dyzgw.com.cn/dyzgw/jyxx/001010/001010003/MoreInfo.aspx?CategoryNum=001010003",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area":"镇级项目"}), f2],
    ["gcjs_zhongbiao_zhen_wsjj_gg", "http://www.dyzgw.com.cn/dyzgw/jyxx/001010/001010005/MoreInfo.aspx?CategoryNum=001010005",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"area":"镇级项目","method":"网上竞价"}), f2],

]


def work(conp,**kwargs):
    est_meta(conp, data=data, diqu="江苏省丹阳市",**kwargs)
    est_html(conp, f=f3,**kwargs)


if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "jiangsu", "danyang"])
    # driver = webdriver.Chrome()
    # driver.get("http://www.dyzgw.com.cn/dyzgw/jyxx/001014/001014002/MoreInfo.aspx?CategoryNum=001014002")
    # print(f1(driver, 1))
    # f2(driver)
    # for i in range(100,120):f1(driver,i)
