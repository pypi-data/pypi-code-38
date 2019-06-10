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

_name_ = 'heilongjiang_shenghui'


def f1(driver, num):
    locator = (By.XPATH, '//div[@id="pageZone"]/span')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    total_temp = driver.find_element_by_xpath('//div[@id="pageZone"]/span').text
    cnum = int(re.findall('第(\d+)\/', total_temp)[0])

    locator = (By.XPATH, '//div[@id="listZone"]')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//div[@id="listZone"]/ul/li[1]/a').get_attribute('href')[-30:]
    if int(cnum) != int(num):
        url = re.sub(r"page=\d+","page=%s"%(str(num)),driver.current_url)
        # print(url)
        driver.get(url)
        locator = (By.XPATH, '//div[@id="listZone"]/ul/li[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//div[@id="listZone"]/ul/li')
    for content in content_list:
        name = content.xpath("./a/@title")[0].strip()
        url = "http://ztb.hljjs.gov.cn/"+content.xpath("./a/@href")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip().strip('(').strip(')')
        temp = [name, ggstart_time,url]
        data.append(temp)
        # print('temp',temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@id="pageZone"]/span')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_temp = driver.find_element_by_xpath('//div[@id="pageZone"]/span').text
    total_page = int(re.findall('\/(\d+)页',total_temp)[0])
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='cArea']")
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
    div = soup.find('div', class_='cArea')
    return div



data = [

    ["gcjs_zhaobiao_kcsj_gg",
     "http://ztb.hljjs.gov.cn/list_bidyw2.aspx?CategoryID=2&Sort=18101&page=1",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"type":"勘察设计"}), f2],
    ["gcjs_zhaobiao_sg_gg",
     "http://ztb.hljjs.gov.cn/list_bidyw2.aspx?CategoryID=2&Sort=18102&page=1",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"type":"施工"}), f2],
    ["gcjs_zhaobiao_jl_gg",
     "http://ztb.hljjs.gov.cn/list_bidyw2.aspx?CategoryID=2&Sort=18103&page=1",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"type":"监理"}), f2],
    ["gcjs_zhaobiao_sb_gg",
     "http://ztb.hljjs.gov.cn/list_bidyw2.aspx?CategoryID=2&Sort=18104&page=1",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"type":"设备"}), f2],


    ["gcjs_zhongbiaohx_kcsj_gg",
     "http://ztb.hljjs.gov.cn/list_bidyw2.aspx?CategoryID=5&Sort=18101&page=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"勘察设计"}), f2],
    ["gcjs_zhongbiaohx_sg_gg",
     "http://ztb.hljjs.gov.cn/list_bidyw2.aspx?CategoryID=5&Sort=18102&page=1",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"type":"施工"}), f2],
    ["gcjs_zhongbiaohx_jl_gg",
     "http://ztb.hljjs.gov.cn/list_bidyw2.aspx?CategoryID=5&Sort=18103&page=1",
     ["name", "ggstart_time", "href","info"], add_info(f1,{"type":"监理"}), f2],
    ["gcjs_zhongbiaohx_sb_gg",
     "http://ztb.hljjs.gov.cn/list_bidyw2.aspx?CategoryID=5&Sort=18104&page=1",
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{"type":"设备"}), f2],


    ["gcjs_zhongbiao_kcsj_gg",
     "http://ztb.hljjs.gov.cn/list_bidyw2.aspx?CategoryID=6&Sort=18101&page=1",
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{"type":"勘察设计"}), f2],
    ["gcjs_zhongbiao_sg_gg",
     "http://ztb.hljjs.gov.cn/list_bidyw2.aspx?CategoryID=6&Sort=18102&page=1",
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{"type":"施工"}), f2],
    ["gcjs_zhongbiao_jl_gg",
     "http://ztb.hljjs.gov.cn/list_bidyw2.aspx?CategoryID=6&Sort=18103&page=1",
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{"type":"监理"}), f2],
    ["gcjs_zhongbiao_sb_gg",
     "http://ztb.hljjs.gov.cn/list_bidyw2.aspx?CategoryID=6&Sort=18104&page=1",
     ["name", "ggstart_time", "href",  "info"], add_info(f1,{"type":"设备"}), f2],

]

def work(conp, **args):
    est_meta(conp, data=data, diqu="黑龙江省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "heilongjiang"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://ztb.hljjs.gov.cn/list_bidyw2.aspx?CategoryID=2&Sort=18101&page=1")
    # f1(driver,4)
    # f1(driver,10)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    #
    # print(f3(driver, 'http://ztb.hljjs.gov.cn/showbid_zbgg.aspx?FID=038010C1-1805-4A9C-B128-0A9FC2D2BA60&Sort=18101'))
    # driver.close()
