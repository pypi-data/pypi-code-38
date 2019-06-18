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
from zhulong.util.etl import est_meta, est_html, add_info
import requests
import time

_name_ = "changshu"


def f3(driver, url):
    driver.get(url)
    locator = (By.ID, "tblInfo")
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


def f1(driver, num):
    # print(webdriver.DesiredCapabilities.CHROME)
    if driver.page_source.find("iframe") != -1:
        iframe1 = driver.find_element_by_id("frames")
        driver.switch_to.frame(iframe1)
        iframe2 = driver.find_element_by_id("frames")
        driver.switch_to.frame(iframe2)
    locator = (By.XPATH, "//div[@class='jytitle']/a")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//tr[2]/td/div[@class='jytitle']/a").get_attribute("href")[-60:]
    locator = (By.XPATH, '//*[@id="Paging"]//td')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    cnum = int(driver.find_element_by_class_name('huifont').text.split('/')[0])
    if int(cnum) != int(num):
        url = '='.join(driver.current_url.split('=')[:-1]) + "=" + str(num)
        driver.get(url)
        locator = (By.XPATH, '//tr[2]/td/div[@class="jytitle"]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
    locator = (By.XPATH, '//td[@id="tdcontent"]//tr')
    WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//td[@id="tdcontent"]//tr')[1:]
    for content in content_list:
        name = ''.join(content.xpath(".//a/text()")[0].strip().split())
        ggstart_time = content.xpath("./td[2]/text()")[0].strip()
        url = "http://ggzy.changshu.gov.cn" + content.xpath(".//a/@href")[0]
        temp = [name, ggstart_time, url]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    if driver.page_source.find("iframe") != -1:
        iframe1 = driver.find_element_by_id("frames")
        driver.switch_to.frame(iframe1)
        iframe2 = driver.find_element_by_id("frames")
        driver.switch_to.frame(iframe2)
    locator = (By.XPATH, '//*[@id="Paging"]//td')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    total_page = int(driver.find_element_by_class_name('huifont').text.split('/')[1])
    driver.quit()
    return total_page


data = [
    #
    ["gcjs_zhaobiao_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/showinfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004001001001&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_kongzhijia_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/showinfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004001001003&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zgysjg_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/showinfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004001001004&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004001001005&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004001001006&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_jiaotong_dayi_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004001002002&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_jiaotong_zhaobiao_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004001002001&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"gctype":"交通"}), f2],
    ["gcjs_jiaotong_zhongbiaohx_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004001002004&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"gctype":"交通"}), f2],
    ["gcjs_jiaotong_zhongbiao_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004001002003&Paging=1",
     ["name", "ggstart_time", "href", "info"],  add_info(f1,{"gctype":"交通"}), f2],

    ["gcjs_shuili_gqita_bu_bian_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004001003002&Paging=1",
     ["name", "ggstart_time", "href", "info"],  add_info(f1,{"gctype":"水利"}), f2],
    ["gcjs_shuili_zhaobiao_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004001003001&Paging=1",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{"gctype":"水利"}), f2],
    ["gcjs_shuili_biangeng_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004001003002&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"gctype":"水利"}), f2],
    ["gcjs_shuili_zhongbiao_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004001003003&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"gctype":"水利"}), f2],

    ["gcjs_gqita_zhaobiao_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004001004001&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"Tag":"其他工程"}), f2],

    ["gcjs_gqita_zhongbiao_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004001004003&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"Tag":"其他工程"}), f2],

    ["gcjs_zhaobiao_zhenji_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004005004001&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"镇级"}), f2],
    ["gcjs_zhongbiao_zhenji_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004005004003&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"镇级"}), f2],
    ["zfcg_biangeng_zhenji_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004005006002&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"镇级"}), f2],

    ["gcjs_shuili_zhaobiao_zhenji_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004005003001&Paging=1",
     ["name", "ggstart_time", "href", "info"],  add_info(f1,{"area":"镇级"}), f2],

    ["gcjs_shuili_zhongbiao_zhenji_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004005003003&Paging=1",
     ["name", "ggstart_time", "href", "info"],  add_info(f1,{"area":"镇级"}), f2],

    ["gcjs_jiaotong_zhaobiao_zhenji_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004005002001&Paging=1",
     ["name", "ggstart_time", "href", "info"],  add_info(f1,{"area":"镇级"}), f2],

    ["gcjs_jiaotong_zhongbiao_zhenji_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004005002003&Paging=1",
     ["name", "ggstart_time", "href", "info"],  add_info(f1,{"area":"镇级"}), f2],

    ["gcjs_zhaobiao_zhenji_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004005001001&Paging=1",
     ["name", "ggstart_time", "href", "info"],  add_info(f1,{"area":"镇级"}), f2],
    ["gcjs_zhongbiaohx_zhenji_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004005001005&Paging=1",
     ["name", "ggstart_time", "href", "info"],  add_info(f1,{"area":"镇级"}), f2],
    ["gcjs_zhongbiao_zhenji_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004005001006&Paging=1",
     ["name", "ggstart_time", "href", "info"],  add_info(f1,{"area":"镇级"}), f2],

    ["zfcg_zhaobiao_zhenji_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004005005001&Paging=1",
     ["name", "ggstart_time", "href", "info"],  add_info(f1,{"area":"镇级"}), f2],
    ["zfcg_biangeng_zhenji_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004005005002&Paging=1",
     ["name", "ggstart_time", "href", "info"],  add_info(f1,{"area":"镇级"}), f2],
    ["zfcg_zhongbiao_zhenji_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004005005003&Paging=1",
     ["name", "ggstart_time", "href", "info"],  add_info(f1,{"area":"镇级"}), f2],
    ["zfcg_zhongbiao_zhenji_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004005005004&Paging=1",
     ["name", "ggstart_time", "href", "info"],  add_info(f1,{"area":"镇级"}), f2],

    ["jqita_zhaobiao_zhenji_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004005006001&Paging=1",
     ["name", "ggstart_time", "href", "info"],  add_info(f1,{"area":"镇级","Tag":"其他采购"}), f2],
    ["jqita_biangeng_zhenji_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004005006002&Paging=1",
     ["name", "ggstart_time", "href", "info"],  add_info(f1,{"area":"镇级","Tag":"其他采购"}), f2],
    ["jqita_zhongbiao_zhenji_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004005006003&Paging=1",
     ["name", "ggstart_time", "href", "info"],  add_info(f1,{"area":"镇级","Tag":"其他采购"}), f2],

    ["jqita_zhaobiao_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004002002001&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"Tag":"国企及其他采购"}), f2],
    ["jqita_biangeng_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004002002002&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"Tag":"国企及其他采购"}), f2],
    ["jqita_zhongbiao_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004002002003&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"Tag":"国企及其他采购"}), f2],

    ["zfcg_zhaobiao_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004002001001&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004002001002&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004002001003&Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhaobiao_danyilaiyuan_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004002001004&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"method": "单一来源"}), f2],
    ["zfcg_zhaobiao_danyilaiyuan_zhenji_gg",
     "http://ggzy.changshu.gov.cn/changshuFront/ShowInfo/jyzxmore.aspx?title=&StartDate=&EndDate=&CategoryNum=004005005004&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"method": "单一来源", "area": "镇级"}), f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="江苏省常熟市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "jiangsu", "changshu"])
