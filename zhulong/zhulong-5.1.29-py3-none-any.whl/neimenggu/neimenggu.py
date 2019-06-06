import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
import pandas as pd
from zhulong.util.etl import est_meta, est_html,est_meta_large

_name_ = "neimenggu"


def f1(driver, num):
    if "http://www.nmggcztb.cn" in driver.current_url: # 公共资源
        locator = (By.XPATH, '//*[@id="liebiao"]/li[1]/a')
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
        val = driver.find_element_by_xpath('//*[@id="liebiao"]/li[1]/a').text
        locator = (By.XPATH, "//div[@class='epages']")
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
        cnum = re.findall('(\d+)\/', driver.find_element_by_xpath("//div[@class='epages']").text)[0]
        # print(cnum,val)
        if int(cnum) != int(num):
            url = '='.join(driver.current_url.split("=")[:-1]) + "=" + str(num)
            driver.get(url)
            locator = (By.XPATH, "//*[@id='liebiao']/li[1]/a[not(contains(string(),'%s'))]" % val)
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
        data = []
        page = driver.page_source
        body = etree.HTML(page)
        content_list = body.xpath("//*[@id='liebiao']//li")
        for content in content_list:
            name = content.xpath("./a/text()")[0].strip()
            ggstart_time = content.xpath("./span/text()")[0].strip()[1:-1]
            url = "http://www.nmggcztb.cn" + content.xpath("./a/@href")[0].strip()
            temp = [name, ggstart_time, url]
            data.append(temp)
            # print(temp)
    else:
        locator = (By.XPATH, "//div[@class='content_right fr']")
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
        val = driver.find_element_by_xpath("//div[@class='content_right fr']//tr[2]/td/a").get_attribute("href")
        cnum = driver.find_element_by_xpath('//a[@class="one"]').text
        if int(cnum) != int(num):
            driver.execute_script("pagination(%s)" % num)
            locator = (By.XPATH, "//div[@class='content_right fr']//tr[2]/td/a[not(contains(@href,'%s'))]" % val)
            WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))

        data = []
        page = driver.page_source
        body = etree.HTML(page)
        content_list = body.xpath("//div[@class='content_right fr']//tr")[1:]
        for content in content_list:
            name = content.xpath("./td/a/text()")[0].strip()
            ggstart_time = content.xpath("./td[last()]/text()")[0].strip()
            url = "http://ggzyjy.nmg.gov.cn" + content.xpath("./td/a/@href")[0].strip()
            temp = [name, ggstart_time, url]
            data.append(temp)
            # print(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    if "http://www.nmggcztb.cn" in driver.current_url :# 公共资源
        locator = (By.XPATH, "//div[@class='epages']")
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
        total_page = re.findall('\/(\d+)', driver.find_element_by_xpath("//div[@class='epages']").text)[0]
    else:
        locator = (By.CLASS_NAME, "mmggxlh")
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
        total_page = driver.find_element_by_xpath("//div[@class='mmggxlh']/a[last()-1]").text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)

    if "http://www.nmggcztb.cn" in driver.current_url: # 公共资源
        locator = (By.XPATH, "//div[@id='left1']")
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
        div = soup.find('div', id='left1')
        # print(div)
    else:
        locator = (By.XPATH, "//div[@class='content']")
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
        div = soup.find('div', class_='content')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://ggzyjy.nmg.gov.cn/jyxx/jsgcZbgg",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_biangeng_gg",
     "http://ggzyjy.nmg.gov.cn/jyxx/jsgcGzsx",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg",
     "http://ggzyjy.nmg.gov.cn/jyxx/jsgcZbhxrgs",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg",
     "http://ggzyjy.nmg.gov.cn/jyxx/jsgcZbjggs",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://ggzyjy.nmg.gov.cn/jyxx/zfcg/cggg",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://ggzyjy.nmg.gov.cn/jyxx/zfcg/gzsx",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://ggzyjy.nmg.gov.cn/jyxx/zfcg/zbjggs",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **kwargs):
    est_meta_large(conp, data=data, diqu="内蒙古自治区", **kwargs)
    est_html(conp, f=f3, **kwargs)


if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "neimenggu", "neimenggu"])
