import random
import pandas as pd
import re
import requests
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time

from zhulong2.util.etl import est_html, est_meta, add_info, est_meta_large

_name_ = "beijing_beijing"


def f1_data(driver, num):
    locator = (By.XPATH, "//div[@class='datagrid-mask-msg']")
    WebDriverWait(driver, 20).until_not(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//input[@class='pagination-num']")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='pagination-info']")
        cnnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(re.findall(r'(\d+)', cnnum)[0])
        if cnum / 20 == int(cnum / 20):
            cnum = cnum / 20
        else:
            cnum = int(cnum / 20) + 1
    except:
        cnum = 1
    if num != int(cnum):
        driver.find_element_by_xpath('//input[@class="pagination-num"]').clear()
        driver.find_element_by_xpath('//input[@class="pagination-num"]').send_keys(num, Keys.ENTER)
        locator = (By.XPATH, "//div[@class='datagrid-mask-msg']")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, "//div[@class='datagrid-mask-msg']")
        WebDriverWait(driver, 10).until_not(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_='datagrid-view2')
    div = div.find('div', class_='datagrid-body')
    tbody = div.find("table", class_='datagrid-btable').tbody
    trs = tbody.find_all("tr")
    data = []
    for tr in trs:
        try:
            title = tr.find('td', attrs={'field': 'purchaseItem'}).div.text.strip()
        except:
            title = '-'
        link = '-'
        try:
            span = tr.find('td', attrs={'field': 'htSgnDate'}).div.text.strip()
        except:
            span = '-'
        try:
            info = {'info_html': '{}'.format(tr)}
            info = json.dumps(info, ensure_ascii=False)
        except:
            info = None
        tmp = [title, span, link, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2_data(driver, num):
    locator = (By.XPATH, "//ul[@class='fei_ul']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='a_div']/span")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        cnum = 1
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='fei_ul']/li[1]/a").get_attribute('href')[-16:]
        if '_' not in url:
            s = "index_%d" % (num - 1) if num > 1 else "index"
            url = re.sub("index", s, url)
        elif num == 1:
            url = re.sub("index_[0-9]*", "index", url)
        else:
            s = "index_%d" % (num - 1) if num > 1 else "index"
            url = re.sub("index_[0-9]*", s, url)
        driver.get(url)
        locator = (By.XPATH, "//ul[@class='fei_ul']/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    tbody = soup.find("ul", class_='fei_ul')
    trs = tbody.find_all("li")
    data = []
    for tr in trs:
        a = tr.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        href = a['href'].strip()
        if 'http' in href:
            link = href
        else:
            url_http = url.rsplit('/', maxsplit=1)[0]
            link = url_http + '/' + href.split('/', maxsplit=1)[1]
        span = tr.find('span', class_='datetime').text.strip()
        info = {}
        if re.findall(r'^\[(\w+)\]', title):
            zbfs = re.findall(r'^\[(\w+)\]', title)[0]
            info['zbfs'] = zbfs
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:
            info = None
        tmp = [title, span, link, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f1(driver, num):
    url = driver.current_url
    if 'http://43.254.24.51:7012/GS6' in url:
        df = f1_data(driver, num)
        return df
    elif 'http://www.ccgp-beijing.gov.cn/fzfcgggq' in url:
        df = f2_data(driver, num)
        return df
    else:
        locator = (By.XPATH, "//ul[@class='xinxi_ul']/li[1]/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, "//div[@class='a_div']/span")
            cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        except:
            cnum = 1
        url = driver.current_url
        if num != int(cnum):
            val = driver.find_element_by_xpath("//ul[@class='xinxi_ul']/li[1]/a").get_attribute('href')[-16:]
            if '_' not in url:
                s = "index_%d" % (num - 1) if num > 1 else "index"
                url = re.sub("index", s, url)
            elif num == 1:
                url = re.sub("index_[0-9]*", "index", url)
            else:
                s = "index_%d" % (num - 1) if num > 1 else "index"
                url = re.sub("index_[0-9]*", s, url)
            driver.get(url)
            locator = (By.XPATH, "//ul[@class='xinxi_ul']/li[1]/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        tbody = soup.find("ul", class_='xinxi_ul')
        trs = tbody.find_all("li")
        data = []
        for tr in trs:
            a = tr.find("a")
            try:
                title = a['title'].strip()
            except:
                title = a.text.strip()
            href = a['href'].strip()
            if 'http' in href:
                link = href
            else:
                url_http = url.rsplit('/', maxsplit=1)[0]
                link = url_http + '/' + href.split('/', maxsplit=1)[1]
            span = tr.find('span', class_='datetime').text.strip()
            info = {}
            if 'sjzfcggg' in url:
                if re.findall(r'^\[(\w+)\]', title):
                    zbfs = re.findall(r'^\[(\w+)\]', title)[0]
                    info['zbfs'] = zbfs
            else:
                if re.findall(r'^\[(\w+)\]', title):
                    zbfs = re.findall(r'^\[(\w+)\]', title)[0]
                    info['diqu'] = zbfs
            if info:
                info = json.dumps(info, ensure_ascii=False)
            else:
                info = None
            tmp = [title, span, link, info]
            data.append(tmp)
        df = pd.DataFrame(data)
        return df


def f2(driver):
    url = driver.current_url
    if 'http://43.254.24.51:7012/GS6' in url:
        locator = (By.XPATH, "//div[@class='datagrid-mask-msg']")
        WebDriverWait(driver, 20).until_not(EC.presence_of_element_located(locator))
        locator = (By.XPATH, "//span[@style='padding-right:6px;']")
        tnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = re.findall(r'(\d+)', tnum)[0]
        driver.quit()
        return int(num)
    elif 'http://www.ccgp-beijing.gov.cn/fzfcgggq' in url:
        locator = (By.XPATH, "//ul[@class='fei_ul']/li[1]/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        while True:
            locator = (By.XPATH, "//ul[@class='fei_ul']/li[1]/a")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            try:
                locator = (By.XPATH, "//a[@id='pagenav_nextgroup']")
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            except:
                num = driver.find_element_by_xpath("//div[@class='a_div']/span").text.strip()
                break
        driver.quit()
        return int(num)
    else:
        locator = (By.XPATH, "//ul[@class='xinxi_ul']/li[1]/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        while True:
            locator = (By.XPATH, "//ul[@class='xinxi_ul']/li[1]/a")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            try:
                locator = (By.XPATH, "//a[@id='pagenav_nextgroup']")
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            except:
                num = driver.find_element_by_xpath("//div[@class='a_div']/span").text.strip()
                break
        driver.quit()
        return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@style='width: 1105px;margin:0 auto'][string-length()>10]")
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
    div = soup.find('div', style='width: 1105px;margin:0 auto')
    return div


data = [
    ["zfcg_zhaobiao_shiji_gg",
     "http://www.ccgp-beijing.gov.cn/xxgg/sjzfcggg/sjzbgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],
    #
    ["zfcg_zhongbiao_shiji_gg",
     "http://www.ccgp-beijing.gov.cn/xxgg/sjzfcggg/sjzbjggg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],
    #
    ["zfcg_biangeng_shiji_gg",
     "http://www.ccgp-beijing.gov.cn/xxgg/sjzfcggg/sjgzgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],

    ["zfcg_liubiao_shiji_gg",
     "http://www.ccgp-beijing.gov.cn/xxgg/sjzfcggg/sjfbgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],

    ["zfcg_yucai_dyly_shiji_gg",
     "http://www.ccgp-beijing.gov.cn/xxgg/sjzfcggg/sjdygg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级', 'zbfs': '单一来源'}), f2],

    ["zfcg_gqita_shiji_gg",
     "http://www.ccgp-beijing.gov.cn/xxgg/sjzfcggg/sjqtgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级'}), f2],

    ["zfcg_gqita_jicaichengjiao_shiji_gg",
     "http://43.254.24.51:7012/GS6/bidapi/showJcContract",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '市级', 'zbfs': '定点采购', 'gglx': '集采成交'}), f2],
    ###
    ["zfcg_zhaobiao_quxian_gg",
     "http://www.ccgp-beijing.gov.cn/xxgg/qjzfcggg/qjzbgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '区县'}), f2],

    ["zfcg_zhongbiao_quxian_gg",
     "http://www.ccgp-beijing.gov.cn/xxgg/qjzfcggg/qjzbjggg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '区县'}), f2],
    #
    ["zfcg_biangeng_quxian_gg",
     "http://www.ccgp-beijing.gov.cn/xxgg/qjzfcggg/qjgzgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '区县'}), f2],

    ["zfcg_liubiao_quxian_gg",
     "http://www.ccgp-beijing.gov.cn/xxgg/qjzfcggg/qjfbgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '区县'}), f2],

    ["zfcg_yucai_dyly_quxian_gg",
     "http://www.ccgp-beijing.gov.cn/xxgg/qjzfcggg/qjdygg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '区县', 'zbfs': '单一来源'}), f2],

    ["zfcg_gqita_quxian_gg",
     "http://www.ccgp-beijing.gov.cn/xxgg/qjzfcggg/qjqtgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '区县'}), f2],

    ["zfcg_gqita_jicaichengjiao_quxian_gg",
     "http://43.254.24.51:7012/GS6/bidapi/showJcContractQx",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '区县', 'zbfs': '定点采购', 'gglx': '集采成交'}), f2],
    ###
    ["zfcg_zhaobiao_fzfcg_gg",
     "http://www.ccgp-beijing.gov.cn/fzfcgggq/fzfzbgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx': '非政府采购'}), f2],

    ["zfcg_zhongbiao_fzfcg_gg",
     "http://www.ccgp-beijing.gov.cn/fzfcgggq/fzfzbjggg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx': '非政府采购'}), f2],
    #
    ["zfcg_biangeng_fzfcg_gg",
     "http://www.ccgp-beijing.gov.cn/fzfcgggq/fzfgzgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx': '非政府采购'}), f2],

    ["zfcg_liubiao_fzfcg_gg",
     "http://www.ccgp-beijing.gov.cn/fzfcgggq/fzffbgg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx': '非政府采购'}), f2],

    ["zfcg_gqita_fzfcg_gg",
     "http://www.ccgp-beijing.gov.cn/fzfcgggq/fzfdygg/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx': '非政府采购'}), f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="北京市", **args)
    est_html(conp, f=f3, **args)


# 页数太多，数据获取不完全
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "beijing"],pageloadtimeout=120,pageLoadStrategy="none",)

    # driver=webdriver.Chrome()
    # url = "http://43.254.24.51:7012/GS6/bidapi/showJcContract"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    # driver=webdriver.Chrome()
    # url = "http://43.254.24.51:7012/GS6/bidapi/showJcContract"
    # driver.get(url)
    # for i in range(1113, 1115):
    #     df=f1(driver, i)
    #     print(df.values)
        # for i in df[2].values:
        #     f = f3(driver, i)
        #     print(f)
