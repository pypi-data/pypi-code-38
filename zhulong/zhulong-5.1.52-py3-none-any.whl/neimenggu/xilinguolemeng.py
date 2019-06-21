import json
import re
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
import pandas as pd
from zhulong.util.etl import est_meta, est_html, add_info

_name_ = "xilinguolemeng"


def f1(driver, num):
    locator = (By.XPATH,"//form[@id='form1']/div/table/tbody/tr[1]")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//form[@id='form1']/div/table/tbody/tr[1]/td/a").get_attribute("href")[-50:]

    locator = (By.XPATH, "//td[@class='yahei redfont']")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    cnum = driver.find_element_by_xpath("//td[@class='yahei redfont']").text

    if int(cnum) != int(num):
        url = re.sub(r"Paging=\d+", 'Paging='+str(num),driver.current_url)
        # print(url)
        driver.get(url)
        locator = (By.XPATH, "//form[@id='form1']/div/table/tbody/tr[1]/td/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//form[@id='form1']/div/table/tbody/tr[@height='27']")
    for content in content_list:
        ggtype = content.xpath('./td[2]/font/text()')[0].strip()
        name = content.xpath("./td/a/text()")[0].strip()
        if name == []:name = None
        ggstart_time = content.xpath("./td[4]/text()")[0].strip().strip('[').strip(']')
        url = "http://xmzwggzy.xlgl.gov.cn" + content.xpath("./td/a/@href")[0].strip()
        info = json.dumps({'ggtype': ggtype }, ensure_ascii=False)
        temp = [name, ggstart_time, url,info]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    # df["info"] = None
    return df

def f2(driver):
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//td[@class="huifont"]')))
    total_page = re.findall('\/(\d+)',driver.find_element_by_xpath('//td[@class="huifont"]').text)[0]

    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    try:
        locator = (By.XPATH, "//table[@id='tblInfo']")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        flag =True
    except:
        locator = (By.XPATH, "//td[@align='left' and @valign='top']")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        flag=False
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
        div=soup.findAll('td',attrs={"align":"left","valign":"top"})[0]
    return div


data = [
    ["gcjs_zhaobiao_mengji_gg",
     "http://xmzwggzy.xlgl.gov.cn/xmweb/showinfo/zbgg_moreNew.aspx?categoryNum=009001005001&categoryNum2=009002006001&categoryNum3=009003003001&categoryNum4=009004003001&categoryNum5=009002008&Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"盟级"}), f2],
    ["gcjs_zhongbiao_mengji_gg",
     "http://xmzwggzy.xlgl.gov.cn/xmweb/showinfo/zbgg_more.aspx?categoryNum=009001005004&categoryNum2=009002006002&categoryNum3=009003003002&categoryNum4=009004003002&Paging=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"盟级"}), f2],
    ["gcjs_biangeng_mengji_gg",
     "http://xmzwggzy.xlgl.gov.cn/xmweb/showinfo/zbgg_more.aspx?categoryNum=009001005005&categoryNum2=009002006004&categoryNum3=009003003004&categoryNum4=009004003004&Paging=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"盟级"}), f2],

    ["gcjs_zhaobiao_qixianji_gg",
     "http://xmzwggzy.xlgl.gov.cn/xmweb/showinfo/zbgg_more.aspx?categoryNum=009001006001&categoryNum2=009002007001&categoryNum3=009003004001&categoryNum4=009004004001&Paging=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"旗县级"}), f2],
    ["gcjs_zhongbiao_qixianji_gg",
     "http://xmzwggzy.xlgl.gov.cn/xmweb/showinfo/zbgg_more.aspx?categoryNum=009001006004&categoryNum2=009002007002&categoryNum3=009003004002&categoryNum4=009004004002&Paging=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"旗县级"}), f2],
    ["gcjs_biangeng_qixianji_gg",
     "http://xmzwggzy.xlgl.gov.cn/xmweb/showinfo/zbgg_more.aspx?categoryNum=009001006005&categoryNum2=009002007004&categoryNum3=009003004004&categoryNum4=009004004004&Paging=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"area":"旗县级"}), f2],


]


def work(conp, **kwargs):
    est_meta(conp, data=data, diqu="内蒙古自治区锡林郭勒盟", **kwargs)
    est_html(conp, f=f3, **kwargs)


if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "neimenggu", "xilinguolemeng"])
    # url = "http://xmzwggzy.xlgl.gov.cn/xmweb/showinfo/zbgg_more.aspx?categoryNum=009001006005&categoryNum2=009002007004&categoryNum3=009003004004&categoryNum4=009004004004&Paging=1"
    # driver = webdriver.Chrome()
    # driver.get(url)
    # f1(driver,1)
    # f1(driver,5)
    # print(f2(driver))