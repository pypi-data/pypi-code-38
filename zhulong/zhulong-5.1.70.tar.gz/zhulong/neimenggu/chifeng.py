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

_name_ = "chifeng"


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="right-position-content"]/div/table/tbody/tr[1]/td[2]/a')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    val = driver.find_element_by_xpath('//div[@class="right-position-content"]/div/table/tbody/tr[1]/td[2]/a').get_attribute("href")[-50:]
    cnum = re.findall("(\d+)\/", driver.find_element_by_xpath("//td[@class='huifont']").text)[0]
    if int(cnum) != int(num):
        url = driver.current_url.split("=")[0] + "=" + str(num)
        # print(url)
        driver.get(url)
        for _ in range(3):
            try:
                locator = (By.XPATH, '//div[@class="right-position-content"]/div/table/tbody/tr[1]/td[2]/a[not(contains(@href,"%s"))]' % val)
                WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
                break
            except:
                driver.refresh()
    data = []
    soup = BeautifulSoup(driver.page_source, "lxml")
    div = soup.find("div", align="left")
    content_list = div.find_all("tr", height="30")
    for content in content_list:
        a = content.find("a")
        name_temp = a.text.strip()
        if "..." in name_temp:
            try:
                name = name_temp.split('...')[1]
                if name == "":
                    raise Exception
            except:
                name = name_temp.split('...')[0]
        else:
            name = a.text.strip()
        ggstart_time = content.find_all("td")[2].text.strip().strip('[').strip(']')
        url = "http://ggzy.chifeng.gov.cn" + a["href"]
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//td[@class='huifont']")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    total_page = re.findall(r"\/(\d+)", driver.find_element_by_xpath("//td[@class='huifont']").text)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//td[@valign="top"]/table[@width="998" and @border="0" and @cellspacing="0"]')
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

    td = soup.findAll("td", valign="top")
    for t in td:
        if t.find("table", attrs={'width': "998", 'border': "0", "cellspacing": "0"}):
            table = t.find("table", attrs={'width': "998", 'border': "0", "cellspacing": "0"})
            break
        else:
            continue
    return table


data = [
    ["gcjs_zhaobiao_kc_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003001/003001001/003001001001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "勘察"}), f2],
    ["gcjs_zhaobiao_sj_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003001/003001001/003001001002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "设计"}), f2],
    ["gcjs_zhaobiao_jl_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003001/003001001/003001001003/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "监理"}), f2],
    ["gcjs_zhaobiao_sg_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003001/003001001/003001001004/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "施工"}), f2],
    ["gcjs_zhaobiao_hw_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003001/003001001/003001001005/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "货物"}), f2],
    ["gcjs_zhaobiao_qita_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003001/003001001/003001001006/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_kc_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003001/003001003/003001003001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "勘察"}), f2],
    ["gcjs_zhongbiaohx_sj_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003001/003001003/003001003002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "设计"}), f2],
    ["gcjs_zhongbiaohx_jl_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003001/003001003/003001003003/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "监理"}), f2],
    ["gcjs_zhongbiaohx_sg_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003001/003001003/003001003004/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "施工"}), f2],
    ["gcjs_zhongbiaohx_hw_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003001/003001003/003001003005/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "货物"}), f2],
    ["gcjs_zhongbiaohx_qita_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003001/003001003/003001003006/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "其他"}), f2],

    ["gcjs_zhongbiao_kc_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003001/003001005/003001005001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "勘察"}), f2],
    ["gcjs_zhongbiao_sj_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003001/003001005/003001005002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "设计"}), f2],
    ["gcjs_zhongbiao_jl_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003001/003001005/003001005003/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "监理"}), f2],
    ["gcjs_zhongbiao_sg_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003001/003001005/003001005004/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "施工"}), f2],
    ["gcjs_zhongbiao_hw_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003001/003001005/003001005005/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "货物"}), f2],
    ["gcjs_zhongbiao_qita_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003001/003001005/003001005006/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "其他"}), f2],

    ["gcjs_biangeng_kc_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003001/003001004/003001004001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "勘察"}), f2],
    ["gcjs_biangeng_sj_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003001/003001004/003001004002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "设计"}), f2],
    ["gcjs_biangeng_jl_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003001/003001004/003001004003/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "监理"}), f2],
    ["gcjs_biangeng_sg_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003001/003001004/003001004004/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "施工"}), f2],
    ["gcjs_biangeng_hw_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003001/003001004/003001004005/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "货物"}), f2],
    ["gcjs_biangeng_qita_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003001/003001004/003001004006/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "其他"}), f2],

    ["zfcg_zhaobiao_gc_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003002/003002001/003002001001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "工程"}), f2],
    ["zfcg_zhaobiao_hw_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003002/003002001/003002001002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "货物"}), f2],
    ["zfcg_zhaobiao_fw_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003002/003002001/003002001003/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "服务"}), f2],

    ["zfcg_zhongbiao_gc_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003002/003002002/003002002001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "工程"}), f2],
    ["zfcg_zhongbiao_hw_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003002/003002002/003002002002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "货物"}), f2],
    ["zfcg_zhongbiao_fw_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003002/003002002/003002002003/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "服务"}), f2],

    ["zfcg_biangeng_gc_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003002/003002003/003002003001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "工程"}), f2],
    ["zfcg_biangeng_hw_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003002/003002003/003002003002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "货物"}), f2],
    ["zfcg_biangeng_fw_gg",
     "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003002/003002003/003002003003/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"type": "服务"}), f2],

]


def work(conp, **kwargs):
    est_meta(conp, data=data, diqu="内蒙古自治区赤峰市", **kwargs)
    est_html(conp, f=f3, **kwargs)


if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "neimenggu", "chifeng"])
    # url = "http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003001/003001001/003001001003/?Paging=1"
    # d= webdriver.Chrome()
    # d.get(url)
    # print(f3(d, 'http://ggzy.chifeng.gov.cn/EpointWeb_CF/InfoDetail/?InfoID=04b24449-486f-4155-a6ad-cf5de9548f3c&CategoryNum=003002003003'))
    # f1(d,1)
    # d.quit()
    # driver =webdriver.Chrome()
    # driver.get("http://ggzy.chifeng.gov.cn/EpointWeb_CF/jyxx_cf/003001/003001001/003001001001/?Paging=1")
    # for i in range(1,17):
    #     f1(driver,i)
    # driver.quit()
