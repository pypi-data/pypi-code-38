import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import etree
import pandas as pd
from zhulong.util.etl import est_meta, est_html

_name_ = "manzhouli"


def f1(driver, num):

    locator = (By.XPATH, "//ul[@class='notice-list lf-list1']/li/a")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    val = driver.find_element_by_xpath("//ul[@class='notice-list lf-list1']/li[1]/a").get_attribute("href")

    locator = (By.XPATH, "//div[@class='pagination']")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    cnum = driver.find_element_by_xpath("//div[@class='pagination']/a[@class='current']").text.strip()

    # return
    if int(cnum) != int(num):
        url = re.sub(r"index[_\d]*",'index_'+str(num) if num != 1 else 'index',driver.current_url)
        # print(url)
        driver.get(url)
        locator = (By.XPATH, "//ul[@class='notice-list lf-list1']/li[1]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath("//ul[@class='notice-list lf-list1']/li")
    for content in content_list:
        name = content.xpath("./a")[0].xpath("string(.)").strip()
        ggstart_time = content.xpath("./span/text()")[0].strip()
        url = "http://www.mzlggzy.org.cn" + content.xpath("./a/@href")[0].strip()
        temp = [name, ggstart_time, url]
        data.append(temp)
        # print(temp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='pagination']/a[contains(string(),'尾页')]")
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    total_temp = driver.find_element_by_xpath("//div[@class='pagination']/a[contains(string(),'尾页')]").get_attribute('href')
    total_page = re.findall('(\d+)\.',total_temp)[0]
    driver.quit()
    return int(total_page)


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, "//div[@class='home-detail']")
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
    div = soup.find('div', class_='home-detail')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.mzlggzy.org.cn/engconstTender/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_biangeng_gg",
     "http://www.mzlggzy.org.cn/engconstChange/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_gqita_zhong_zhonghx_gg",
     "http://www.mzlggzy.org.cn/engconstWinbid/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["gcjs_liubiao_gg",
     "http://www.mzlggzy.org.cn/gcjsZbycgg/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://www.mzlggzy.org.cn/govprocChange/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_biangeng_gg",
     "http://www.mzlggzy.org.cn/govprocWinbid/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_zhongbiao_gg",
     "http://www.mzlggzy.org.cn/zb/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    ["zfcg_liubiao_gg",
     "http://www.mzlggzy.org.cn/zfcgCgycgg/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **kwargs):
    est_meta(conp, data=data, diqu="内蒙古自治区满洲里市", **kwargs)
    est_html(conp, f=f3, **kwargs)


if __name__ == "__main__":
    # url = "http://www.mzlggzy.org.cn/engconstTender/index.htm"
    # driver =webdriver.Chrome()
    # driver.get(url)
    # f1(driver,1)
    # f1(driver,5)
    # f1(driver,1)
    # print(f2(driver))

    work(conp=["postgres", "since2015", "192.168.3.171", "neimenggu", "manzhouli"])
