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
from zhulong.util.etl import est_html, est_meta, add_info
import requests
import time

_name_='kunshan'
def f3(driver, url):
    driver.get(url)
    locator = (By.CLASS_NAME, "ewb-colu-bd")
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
    div = soup.find('div', class_='ewb-colu-bd')
    return div


def f1(driver, num):
    locator = (By.XPATH, '//ul[@class="wb-data-item"]')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    val = driver.find_element_by_xpath('//ul[@class="wb-data-item"]/li[1]/div/a').get_attribute("href")[-50:]
    locator = (By.CLASS_NAME, 'huifont')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    cnum = int(driver.find_element_by_class_name('huifont').text.split('/')[0])
    if int(cnum) != int(num):
        url = '='.join(driver.current_url.split('=')[:-1]) + "=" + str(num)
        driver.get(url)
        locator = (By.XPATH, "//ul[@class='wb-data-item']/li[1]/div/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
    locator =(By.XPATH,'//ul[@class="wb-data-item"]/li')
    WebDriverWait(driver,30).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//ul[@class="wb-data-item"]/li')
    for content in content_list:
        if content.xpath("./div/a/text()")==[]:
            name = "None"
        else:
            name = content.xpath("./div/a/text()")[0].strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        url = "http://www.ksggzy.com" + content.xpath("./div/a/@href")[0]
        temp = [name, ggstart_time, url]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.CLASS_NAME, 'huifont')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    total_page = int(driver.find_element_by_class_name('huifont').text.split('/')[1])
    driver.quit()
    return total_page


data = [

    ["gcjs_zhaobiao_gg", "http://www.ksggzy.com/TPFront/gcjs/005003/005003001/005003001001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://www.ksggzy.com/TPFront/gcjs/005003/005003001/005003001004/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zhongbiao_gg", "http://www.ksggzy.com/TPFront/gcjs/005003/005003001/005003001005/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_zgysjg_gg", "http://www.ksggzy.com/TPFront/gcjs/005003/005003001/005003001006/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_biangeng_gg", "http://www.ksggzy.com/TPFront/gcjs/005003/005003001/005003001007/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_kongzhijia_gg", "http://www.ksggzy.com/TPFront/gcjs/005003/005003001/005003001002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],



    ["zfcg_zhaobiao_hw_gg", "http://www.ksggzy.com/TPFront/zfcg/004003/004003002/004003002001/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"货物"}), f2],
    ["zfcg_gqita_zhong_liu_hw_1_gg", "http://www.ksggzy.com/TPFront/zfcg/004003/004003002/004003002002/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"货物"}), f2],
    ["zfcg_gqita_zhong_liu_hw_2_gg", "http://www.ksggzy.com/TPFront/zfcg/004003/004003002/004003002003/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"货物"}), f2],
    ["zfcg_biangeng_hw_gg", "http://www.ksggzy.com/TPFront/zfcg/004003/004003002/004003002004/?Paging=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"type":"货物"}), f2],

    ["qycg_zhaobiao_gg", "http://www.ksggzy.com/TPFront/gycq/006008/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qycg_zhongbiao_gg", "http://www.ksggzy.com/TPFront/gycq/006009/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["qycg_biangeng_gg", "http://www.ksggzy.com/TPFront/gycq/006010/?Paging=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp,**kwargs):
    est_meta(conp, data=data, diqu="江苏省昆山市",**kwargs)
    est_html(conp, f=f3,**kwargs)


if __name__ == "__main__":
    conp=["postgres", "since2015", "192.168.3.171", "jiangsu", "kunshan"]
    work(conp)