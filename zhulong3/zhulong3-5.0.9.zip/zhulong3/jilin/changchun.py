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

_name_ = 'jilin_changchun'


def f1(driver, num):
    locator = (By.XPATH, '//td[@class="huifont"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    page_temp = driver.find_element_by_xpath('//td[@class="huifont"]').text
    cnum = re.findall("(\d+)\/", page_temp)[0]

    locator = (By.XPATH, '//ul[@class="wb-data-item"]/li')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//ul[@class="wb-data-item"]/li[1]/div/a').get_attribute('href')[-30:]
    if int(cnum) != int(num):
        driver.execute_script("ShowNewPage('./?Paging=%s');" % num)
        locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[1]/div/a[not(contains(@href,"%s"))]' % val)
        for _ in range(5):

            try:
                try:
                    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
                    break
                except:
                    if str(num) in driver.current_url:break
            except:
                driver.refresh()
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//ul[@class="wb-data-item"]/li')
    for content in content_list:
        name = content.xpath("./div/a/text()")[0].strip()
        url = 'http://www.ccjspt.com.cn' + content.xpath("./div/a/@href")[0].strip()
        try:
            ggstart_time = content.xpath("./span/text()")[0].strip()
        except:
            ggstart_time = ''
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print('temp',temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//td[@class="huifont"]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    page_temp = driver.find_element_by_xpath('//td[@class="huifont"]').text
    total_page = re.findall("\/(\d+)", page_temp)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//table[@width="1014"]')
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
    div = soup.find('table', width='1014')
    return div


data = [
    ["gcjs_zhaobiao_jl_gg",
     "http://www.ccjspt.com.cn/TPFront/zbgg/078003/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"监理"}), f2],
    ["gcjs_zhaobiao_sg_gg",
     "http://www.ccjspt.com.cn/TPFront/zbgg/078006/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"施工"}), f2],
    ["gcjs_zhaobiao_kcsj_gg",
     "http://www.ccjspt.com.cn/TPFront/zbgg/078007/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"勘察设计"}), f2],
    ["gcjs_zhaobiao_sg_wh_gg",
     "http://www.ccjspt.com.cn/TPFront/zbgg/078005/078005001/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"施工","Tag":"外埠"}), f2],
    ["gcjs_zhaobiao_jl_wh_gg",
     "http://www.ccjspt.com.cn/TPFront/zbgg/078005/078005002/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"监理","Tag":"外埠"}), f2],
    ["gcjs_zhaobiao_kcsj_wh_gg",
     "http://www.ccjspt.com.cn/TPFront/zbgg/078005/078005003/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"勘察设计","Tag":"外埠"}), f2],
    ["gcjs_zhaobiao_qt_wh_gg",
     "http://www.ccjspt.com.cn/TPFront/zbgg/078005/078005004/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"其他"}), f2],

    ["gcjs_zhongbiaohx_jl_gg",
     "http://www.ccjspt.com.cn/TPFront/hxrgs/080004/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"监理"}), f2],
    ["gcjs_zhongbiaohx_sg_gg",
     "http://www.ccjspt.com.cn/TPFront/hxrgs/080003/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"施工"}), f2],
    ["gcjs_zhongbiaohx_sg_wh_gg",
     "http://www.ccjspt.com.cn/TPFront/hxrgs/080006/080006001/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"施工","Tag":"外埠"}), f2],
    ["gcjs_zhongbiaohx_jl_wh_gg",
     "http://www.ccjspt.com.cn/TPFront/hxrgs/080006/080006002/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"监理","Tag":"外埠"}), f2],
    ["gcjs_zhongbiaohx_kcsj_wh_gg",
     "http://www.ccjspt.com.cn/TPFront/hxrgs/080006/080006003/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"勘察设计","Tag":"外埠"}), f2],
    ["gcjs_zhongbiaohx_qt_wh_gg",
     "http://www.ccjspt.com.cn/TPFront/hxrgs/080006/080006004/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"其他","Tag":"外埠"}), f2],

    ["gcjs_zhongbiao_jl_gg",
     "http://www.ccjspt.com.cn/TPFront/zbjggg/084002/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"监理"}), f2],
    ["gcjs_zhongbiao_sg_gg",
     "http://www.ccjspt.com.cn/TPFront/zbjggg/084001/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"施工"}), f2],
    ["gcjs_zhongbiao_kcsj_gg",
     "http://www.ccjspt.com.cn/TPFront/zbjggg/084004/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"勘察设计"}), f2],
    ["gcjs_zhongbiao_sg_wh_gg",
     "http://www.ccjspt.com.cn/TPFront/zbjggg/084003/084003001/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"施工","Tag":"外埠"}), f2],
    ["gcjs_zhongbiao_jl_wh_gg",
     "http://www.ccjspt.com.cn/TPFront/zbjggg/084003/084003002/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"监理","Tag":"外埠"}), f2],
    ["gcjs_zhongbiao_kcsj_wh_gg",
     "http://www.ccjspt.com.cn/TPFront/zbjggg/084003/084003003/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"勘察设计","Tag":"外埠"}), f2],
    ["gcjs_zhongbiao_qt_wh_gg",
     "http://www.ccjspt.com.cn/TPFront/zbjggg/084003/084003004/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"其他","Tag":"外埠"}), f2],

    ["gcjs_biangeng_jl_gg",
     "http://www.ccjspt.com.cn/TPFront/bggg/079004/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"监理"}), f2],
    ["gcjs_biangeng_sg_gg",
     "http://www.ccjspt.com.cn/TPFront/bggg/079003/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"施工"}), f2],
    ["gcjs_biangeng_kcsj_gg",
     "http://www.ccjspt.com.cn/TPFront/bggg/079001/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"勘察设计"}), f2],
    ["gcjs_biangeng_qt_gg",
     "http://www.ccjspt.com.cn/TPFront/bggg/079006/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"其他"}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="吉林省长春市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "jilin_changchun"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://www.ccjspt.com.cn/TPFront/hxrgs/080003/")
    # for i in range(1,90):print(f1(driver,i))
