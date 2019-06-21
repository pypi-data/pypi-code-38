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

_name_ = 'hebei_shenghui'


def f1(driver, num):
    locator = (By.XPATH, "//div[@id='fl_lt_pager_bottom']")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    page_temp = driver.find_element_by_xpath("//div[@id='fl_lt_pager_bottom']").text
    cnum = re.findall("第(\d+?)\/", page_temp)[0]

    locator = (By.XPATH, "//div[@id='fl_lt_div']//tr")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//div[@id='fl_lt_div']//tr[1]/td/a").get_attribute("href")[-20:]
    # print("cnum",cnum,"val",val)
    if int(cnum) != int(num):
        url = re.sub("p=\d+","p="+str(num),driver.current_url)
        # print(url)
        driver.get(url)
        locator = (By.XPATH, '//div[@id="fl_lt_div"]//tr[1]/td/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@id='fl_lt_div']//tr")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@id='fl_lt_div']//tr")
    for content in content_list:
        name = content.xpath("./td/a/span/text()")[0].strip()
        ggstart_time = content.xpath("./td[2]/text()")[0].strip()
        url = 'http://zbb.hebjs.gov.cn/hebgc2009/index.php'+content.xpath("./td/a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)

    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@id='fl_lt_pager_bottom']")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    page_temp = driver.find_element_by_xpath("//div[@id='fl_lt_pager_bottom']").text
    total_page = re.findall("\/(\d+?)页", page_temp)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.ID, "second_body_right")
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
    div = soup.find('div', id='second_body_right')
    return div


data = [
    ["gcjs_zhaobiao_shengji_gg",
     "http://zbb.hebjs.gov.cn/hebgc2009/index.php?a=eng-anc-list&cat_bid1=&title=&region=130000&p=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'省会'}), f2],

    ["gcjs_zhaobiao_sjzs_gg",
     "http://zbb.hebjs.gov.cn/hebgc2009/index.php?a=eng-anc-list&cat_bid1=&title=&region=130100&p=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'石家庄'}), f2],

    ["gcjs_zhaobiao_tss_gg",
     "http://zbb.hebjs.gov.cn/hebgc2009/index.php?a=eng-anc-list&cat_bid1=&title=&region=130200&p=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'唐山市'}), f2],

    ["gcjs_zhaobiao_qhds_gg",
     "http://zbb.hebjs.gov.cn/hebgc2009/index.php?a=eng-anc-list&cat_bid1=&title=&region=130300&p=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'秦皇岛市'}), f2],

    ["gcjs_zhaobiao_hds_gg",
     "http://zbb.hebjs.gov.cn/hebgc2009/index.php?a=eng-anc-list&cat_bid1=&title=&region=130400&p=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'邯郸市'}), f2],

    ["gcjs_zhaobiao_xts_gg",
     "http://zbb.hebjs.gov.cn/hebgc2009/index.php?a=eng-anc-list&cat_bid1=&title=&region=130500&p=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'邢台市'}), f2],

    ["gcjs_zhaobiao_bds_gg",
     "http://zbb.hebjs.gov.cn/hebgc2009/index.php?a=eng-anc-list&cat_bid1=&title=&region=130600&p=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'保定市'}), f2],

    ["gcjs_zhaobiao_zjks_gg",
     "http://zbb.hebjs.gov.cn/hebgc2009/index.php?a=eng-anc-list&cat_bid1=&title=&region=130700&p=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'张家口市'}), f2],

    ["gcjs_zhaobiao_cds_gg",
     "http://zbb.hebjs.gov.cn/hebgc2009/index.php?a=eng-anc-list&cat_bid1=&title=&region=130800&p=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'承德市'}), f2],

    ["gcjs_zhaobiao_czs_gg",
     "http://zbb.hebjs.gov.cn/hebgc2009/index.php?a=eng-anc-list&cat_bid1=&title=&region=130900&p=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'沧州市'}), f2],

    ["gcjs_zhaobiao_lfs_gg",
     "http://zbb.hebjs.gov.cn/hebgc2009/index.php?a=eng-anc-list&cat_bid1=&title=&region=131000&p=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'廊坊市'}), f2],

    ["gcjs_zhaobiao_hss_gg",
     "http://zbb.hebjs.gov.cn/hebgc2009/index.php?a=eng-anc-list&cat_bid1=&title=&region=131100&p=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'area':'衡水市'}), f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="河北省", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "anbang2", "hebei"]
    work(conp)
    # driver = webdriver.Chrome()
    # driver.get("http://zbb.hebjs.gov.cn/hebgc2009/index.php?a=eng-anc-list&region=&title=&p=1")
    # f1(driver,1422)
    # f1(driver,1423)
    # f1(driver,1424)
    # f1(driver,1425)
    # f1(driver,1426)
    # f1(driver,1427)

