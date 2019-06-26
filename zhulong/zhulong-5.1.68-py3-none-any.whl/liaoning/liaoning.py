import json
import re

from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong.util.etl import est_tbs, est_gg, est_cdc, est_meta, est_html_work, est_html_cdc, est_html
import time

_name_ = 'liaoning'


def f1(driver, num):
    locator = (By.XPATH, '//*[@id="MoreInfoListjyxx1_DataGrid1"]/tbody/tr[1]/td/div/div/h4/a')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    val = driver.find_element_by_xpath('//*[@id="MoreInfoListjyxx1_DataGrid1"]/tbody/tr[1]/td/div/div/h4/a').text
    locator = (By.ID, "MoreInfoListjyxx1_ys")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    cnum = driver.find_element_by_id('MoreInfoListjyxx1_ys').text.split("/")[0]
    if int(cnum) != int(num):
        driver.execute_script("javascript:__doPostBack('MoreInfoListjyxx1$Pager','{}')".format(num))
        locator = (By.XPATH, '//*[@id="MoreInfoListjyxx1_DataGrid1"]/tbody/tr[1]/td/div/div/h4/a')
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
        locator = (By.XPATH,
                   "//*[@id='MoreInfoListjyxx1_DataGrid1']/tbody/tr[1]/td/div/div/h4/a[not(contains(string(),'%s'))]" % val)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table[@id="MoreInfoListjyxx1_DataGrid1"]/tbody/tr')

    data = []
    for content in content_list:
        name = content.xpath(".//div[@class='publicont']//h4/a/text()")[0].strip()
        area = content.xpath(".//p/span[@class='span_on'][1]/text()")[0].strip()
        ggtype = content.xpath(".//p/span[@class='span_on'][3]/text()")[0].strip()
        new_url = "http://www.lnggzy.gov.cn" + content.xpath(".//div[@class='publicont']//h4/a/@href")[0].strip()
        try:
            ggstart_time = content.xpath(".//div[@class='publicont']//h4/span/text()")[0].strip()
        except:
            ggstart_time = '无法选取时间'

        info = json.dumps({'area': area, 'ggtype': ggtype}, ensure_ascii=False)
        temp = [name, ggstart_time, new_url, info]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.ID, "MoreInfoListjyxx1_ys")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    total_page = driver.find_element_by_id('MoreInfoListjyxx1_ys').text.split("/")[1]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@id='tblInfo'] | //form[@id='form1']")
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
    if div == None:    div = soup.find('form', id='form1')

    return div


data = [
    # 城市页面 ---  工程建设招标
    ["zfcg_zhaobiao_gg",
     "http://www.lnggzy.gov.cn/lnggzy/showinfo/Morejyxx.aspx?timebegin=2000-01-01&timeend=2018-11-20&timetype=10&num1=001&num2=001001&jyly=005&word=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://www.lnggzy.gov.cn/lnggzy/showinfo/Morejyxx.aspx?timebegin=2000-01-01&timeend=2018-11-20&timetype=10&num1=001&num2=001002&jyly=005&word=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://www.lnggzy.gov.cn/lnggzy/showinfo/Morejyxx.aspx?timebegin=2000-01-01&timeend=2018-11-20&timetype=10&num1=001&num2=001004&jyly=005&word=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_gg",
     "http://www.lnggzy.gov.cn/lnggzy/showinfo/Morejyxx.aspx?timebegin=2000-01-01&timeend=2018-11-20&timetype=10&num1=002&num2=001001&jyly=005&word=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://www.lnggzy.gov.cn/lnggzy/showinfo/Morejyxx.aspx?timebegin=2000-01-01&timeend=2018-11-20&timetype=10&num1=002&num2=001003&jyly=005&word=",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://www.lnggzy.gov.cn/lnggzy/showinfo/Morejyxx.aspx?timebegin=2000-10-19&timeend=2000-01-01&timetype=10&num1=002&num2=001004&jyly=005&word=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="辽宁省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    # work(conp=["postgres", "since2015", "192.168.3.171", "liaoning", "liaoning"])
    url = 'http://www.lnggzy.gov.cn/lnggzy/InfoDetail/Default.aspx?InfoID=0bf110b9-0040-4eac-a698-cf017a7cb026&CategoryNum=005013002001'
    driver = webdriver.Chrome()
    print(f3(driver, url))
