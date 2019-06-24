import random
import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
import pandas as pd
from zhulong.util.etl import est_meta, est_html, add_info

_name_ = "huhehaote"


def f1(driver, num):
    # 容易崩，加睡眠时间
    time.sleep(random.randint(3,7))
    locator = (By.XPATH, "//td[@id='MoreInfoList1_tdcontent']")
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))

    val = driver.find_element_by_xpath('//*[@id="MoreInfoList1_DataGrid1"]/tbody/tr[1]/td[2]/a').get_attribute("href")[-40:]
    srcs = driver.find_elements_by_xpath('//div[@id="MoreInfoList1_Pager"]/img')
    cnum = ''
    for s in srcs:
        tmp = s.get_attribute("src")
        cnum_temp = re.findall('(\d+)', tmp)
        if cnum_temp!=[]:cnum+=cnum_temp[0]

    if int(cnum) != int(num):
        driver.execute_script("javascript:__doPostBack('MoreInfoList1$Pager','%s')" % num)
        locator = (By.XPATH, "//*[@id='MoreInfoList1_DataGrid1']/tbody/tr[1]/td[2]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located(locator))
    # return cnum, num
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//table[@id='MoreInfoList1_DataGrid1']//tr")
    for content in content_list:
        name = content.xpath("./td/a/text()")[0].strip()
        ggstart_time = content.xpath("./td[last()]/text()")[0].strip()
        url = "http://ggzy.huhhot.gov.cn" + content.xpath("./td/a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@id='MoreInfoList1_Pager']")
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
    # xpath 可以通过超链接内容包含某个关键字进行定位
    try:
        total_page = re.findall("(\d+)", driver.find_element_by_xpath(
            "//div[@id='MoreInfoList1_Pager']/a[last()]").get_attribute("title"))[0]
    except:
        total_page = 1
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@id='tblInfo']")
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
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
    ["gcjs_zhaobiao_gg",
     "http://ggzy.huhhot.gov.cn/hsweb/004/004001/004001001/MoreInfo.aspx?CategoryNum=004001001",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_bian_da_gg",
     "http://ggzy.huhhot.gov.cn/hsweb/004/004001/004001002/MoreInfo.aspx?CategoryNum=004001002",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://ggzy.huhhot.gov.cn/hsweb/004/004001/004001003/MoreInfo.aspx?CategoryNum=004001003",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_pingbiao_gg",
     "http://ggzy.huhhot.gov.cn/hsweb/004/004001/004001004/MoreInfo.aspx?CategoryNum=004001004",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://ggzy.huhhot.gov.cn/hsweb/004/004002/004002001/MoreInfo.aspx?CategoryNum=004002001",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_jj_gg",
     "http://ggzy.huhhot.gov.cn/hsweb/004/004002/004002005/MoreInfo.aspx?CategoryNum=004002005",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"协议竞价"}), f2],

    ["zfcg_zhongbiao_jj_gg",
     "http://ggzy.huhhot.gov.cn/hsweb/004/004002/004002006/MoreInfo.aspx?CategoryNum=004002006",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"协议竞价"}), f2],
    ["zfcg_liubiao_jj_gg",
     "http://ggzy.huhhot.gov.cn/hsweb/004/004002/004002006/MoreInfo.aspx?CategoryNum=004002006",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"协议竞价"}), f2],

    ["zfcg_biangeng_gg",
     "http://ggzy.huhhot.gov.cn/hsweb/004/004002/004002004/MoreInfo.aspx?CategoryNum=004002004",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://ggzy.huhhot.gov.cn/hsweb/004/004002/004002003/MoreInfo.aspx?CategoryNum=004002003",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_liubiao_gg",
     "http://ggzy.huhhot.gov.cn/hsweb/004/004002/004002007/MoreInfo.aspx?CategoryNum=004002007",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_jiaotong_zhaobiao_gg",
     "http://ggzy.huhhot.gov.cn/hsweb/004/004010/004010001/MoreInfo.aspx?CategoryNum=004010001",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_jiaotong_bian_da_gg",
     "http://ggzy.huhhot.gov.cn/hsweb/004/004010/004010002/MoreInfo.aspx?CategoryNum=004010002",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_jiaotong_zhong_zhonghx_gg",
     "http://ggzy.huhhot.gov.cn/hsweb/004/004010/004010003/MoreInfo.aspx?CategoryNum=004010003",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_shuili_zhaobiao_gg",
     "http://ggzy.huhhot.gov.cn/hsweb/004/004011/004011001/MoreInfo.aspx?CategoryNum=004011001",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_shuili_bian_da_gg",
     "http://ggzy.huhhot.gov.cn/hsweb/004/004011/004011002/MoreInfo.aspx?CategoryNum=004011002",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_shuili_zhongbiao_gg",
     "http://ggzy.huhhot.gov.cn/hsweb/004/004011/004011003/MoreInfo.aspx?CategoryNum=004011003",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_dianli_zhaobiao_gg",
     "http://ggzy.huhhot.gov.cn/hsweb/004/004012/004012001/MoreInfo.aspx?CategoryNum=004012001",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_dianli_bian_da_gg",
     "http://ggzy.huhhot.gov.cn/hsweb/004/004012/004012002/MoreInfo.aspx?CategoryNum=004012002",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_dianli_zhongbiao_gg",
     "http://ggzy.huhhot.gov.cn/hsweb/004/004012/004012003/MoreInfo.aspx?CategoryNum=004012003",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **kwargs):
    est_meta(conp, data=data, diqu="内蒙古自治区呼和浩特市", **kwargs)
    est_html(conp, f=f3, **kwargs)


if __name__ == "__main__":

    work(conp=["postgres", "since2015", "192.168.3.171", "neimenggu", "huhehaote"])
    # url = "http://ggzy.huhhot.gov.cn/hsweb/004/004001/004001001/MoreInfo.aspx?CategoryNum=004001001"
    # #
    # d = webdriver.Chrome()
    # d.get(url)
    # for i in range(1, 215):
    #     print(f1(d, i))
    #
    # d.quit()
