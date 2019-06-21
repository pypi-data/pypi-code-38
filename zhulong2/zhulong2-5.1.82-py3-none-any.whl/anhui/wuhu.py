import pandas as pd
import re
from lxml import etree
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from zhulong2.util.etl import est_meta, est_html, add_info

_name_ = 'anhui_wuhu'


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, "//div[@class='contentbox']")
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
    div = soup.find('div', class_='contentbox')
    return div


def f1(driver, num):


    locator = (By.XPATH, "//div[@class='listnews']/ul/li[1]/span/a")
    val = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).get_attribute("href")[-30:]

    locator = (By.XPATH, "//span[@class='current']")
    cnum = WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text
    # print('val', val, 'cnum', cnum)
    if int(cnum) != int(num):
        url = driver.current_url
        new_url = re.sub(r"page=\d+", 'page=' + str(num), url)
        driver.get(new_url)
        locator = (By.XPATH, '//div[@class="listnews"]/ul/li[1]/span/a[not(contains(@href,"%s"))] ' % ( val))
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//div[@class='listnews']/ul/li[not(contains(@class,'line'))]")

    for content in content_list:
        ggstart_time = content.xpath('./span/font/text()')[0].strip()
        name = content.xpath("./span/a/@title")[0].strip()
        href = content.xpath("./span/a/@href")[0].strip()
        temp = [name, ggstart_time, href]

        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//a[contains(text(),'尾页')]")
    txt = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).get_attribute('href')
    total_page = re.findall('page=(\d+)', txt)[0]
    driver.quit()
    return int(total_page)


data = [

    ["zfcg_zhongbiao_1_gg",
     "http://weda.wuhu.gov.cn/Tmp/Nav_lanmu.shtml?tm=34753%2E36&SS_ID=773&page=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"tag":"预中标"}), f2],

    ["zfcg_zhaobiao_gg",
     "http://weda.wuhu.gov.cn/Tmp/Nav_lanmu.shtml?tm=34753%2E19&SS_ID=769&page=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_2_gg",
     "http://weda.wuhu.gov.cn/Tmp/Nav_lanmu.shtml?tm=39888%2E25&SS_ID=776&page=2",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **arg):
    est_meta(conp, data=data, diqu="安徽省芜湖市", **arg)
    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "anbang", "anhui_wuhu"],num=2)
    # driver = webdriver.Chrome()
    # driver.get("http://weda.wuhu.gov.cn/Tmp/Nav_lanmu.shtml?SS_ID=769&tm=34753%2E19&page=9")
    # f1(driver,3)
