import math
import re

import requests
from bs4 import BeautifulSoup
from lmfscrap import web
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zhulong4.util.etl import est_html, est_meta, est_meta_large
import time

_name_ = 'ec_ccccltd_cn'


def f1(driver, num):
    locator = (By.XPATH, '//table[@style="table-layout:fixed;"]/tbody/tr')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    val = driver.find_element_by_xpath(
        '//table[@style="table-layout:fixed;"]/tbody/tr[child::td][1]/td[2]/a').get_attribute("href")[-100:-50]
    cnum = driver.find_element_by_xpath('//span[@class="page_text01"][1]').text
    if int(cnum) != int(num):
        driver.execute_script("""function checkPageNoKey(num1) {
                                form.VENUS_PAGE_NO_KEY.value = num1;
                                if(form.VENUS_PAGE_NO_KEY_INPUT.value <= 0) {
                                    form.VENUS_PAGE_NO_KEY.value = 1;
                                }}
                                function goAppointedPage(num2){  //直接跳到某页
                                checkPageNoKey(num2);
                                form.submit();
                                }
                                goAppointedPage(%s)""" % num)

        locator = (By.XPATH,
                   '//table[@style="table-layout:fixed;"]/tbody/tr[child::td][1]/td[2]/a[not(contains(@href,"%s"))]' % val)
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table[@style="table-layout:fixed;"]/tbody/tr[child::td]')
    for content in content_list:
        name = content.xpath("./td[2]/a/text()")[0].strip()
        url_temp = re.findall('\'([^\']+)\'', content.xpath("./td[2]/a/@href")[0])[0]
        url_temp = re.sub(r'\\r\\n', '', url_temp)
        url = 'http://ec.ccccltd.cn/PMS/moredetail.shtml?id=' + url_temp
        ggstart_time = content.xpath("./td[last()]/text()")[0].strip()

        temp = [name, ggstart_time, url]
        data.append(temp)
        # print('temp', temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//span[@class="page_text01"][2]')
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    total_page = driver.find_element_by_xpath('//span[@class="page_text01"][2]').text
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@id="right"]')
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
    div = soup.find('div', id='right')
    return div


data = [
    ["qy_gqita_zhao_bian_liu_kong_gg",
     "http://ec.ccccltd.cn/PMS/gysmore.shtml?id=sjN7r9ttBwLI2dpg4DQpQb68XreXjaqknBMygP8dAEQ57TILyRtTnCZX1hIiXHcc1Ra16D6TzZdblRFD/JXcCd5FP7Ek60ksxl9KkyODirY=",
     ['name', 'ggstart_time', 'href', "info"], f1, f2],

    ["qy_zhongbiaohx_gg",
     "http://ec.ccccltd.cn/PMS/gysmore.shtml?id=sjN7r9ttBwLI2dpg4DQpQb68XreXjaqknBMygP8dAEQ57TILyRtTnPr0y7nbc5lW1Ra16D6TzZdblRFD/JXcCd5FP7Ek60ksxl9KkyODirY=",
     ['name', 'ggstart_time', 'href', "info"], f1, f2],

]


def work(conp, **args):
    est_meta_large(conp, data=data, diqu="中国交通建设集团有限公司", **args)
    est_html(conp, f=f3, **args)

def main():
    conp = ["postgres", "since2015", "192.168.3.171", "anbang_qiye", "ec_ccccltd_cn"]
    work(conp, pageloadtimeout=40)
    # driver = webdriver.Chrome()
    # driver.get("http://ec.ccccltd.cn/PMS/gysmore.shtml?id=sjN7r9ttBwLI2dpg4DQpQb68XreXjaqknBMygP8dAEQ57TILyRtTnCZX1hIiXHcc1Ra16D6TzZdblRFD/JXcCd5FP7Ek60ksxl9KkyODirY=")
    # f1(driver, 2)
    # f1(driver, 3)
    # f1(driver, 10)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # driver.get("http://ec.ccccltd.cn/PMS/gysmore.shtml?id=sjN7r9ttBwLI2dpg4DQpQb68XreXjaqknBMygP8dAEQ57TILyRtTnPr0y7nbc5lW1Ra16D6TzZdblRFD/JXcCd5FP7Ek60ksxl9KkyODirY=")
    # f1(driver, 2)
    # f1(driver, 3)
    # f1(driver, 10)
    # print(f2(driver))
    # driver = webdriver.Chrome()
    # print(
    #     f3(driver, 'http://ec.ccccltd.cn/PMS/moredetail.shtml?id=rlfE3i5BGBB0+4B90Mn5NFqXO9o+RLfH6jsITwDEk951zLidmyWYgOWEs0LitWGfsNC1kSxrQ1yUDgiTmndKsSi8mYW9wH7asNC1kSxrQ1yUDgiTmndKsaxjvQ1EHVjxGlc9rVi95hBcyzQAtFicBeH9zf46XSSkGPvNdUTZd5ZWRFxeAJJDCVtXDy8n/F1o'))
    # driver.close()
if __name__ == "__main__":
    main()