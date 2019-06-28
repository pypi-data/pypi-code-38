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
from zhulong.util.etl import gg_meta, gg_html, est_meta, est_html, add_info
import requests
import time

_name_="yizheng"
def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "/html/body/table/tbody/tr/td[2]/table")
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
    div = soup.findAll('table',class_='')[8]
    return div


def f1(driver, num):
    locator = (By.XPATH, '//table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div[1]/a')
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located(locator))
    val = driver.find_element_by_xpath('//table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div[1]/a').text
    locator = (By.XPATH, '//table/tbody/tr/td[2]/table/tbody/tr[2]/td/div')
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    cnum = int(re.findall('第(.*?)页',driver.find_element_by_xpath('//table/tbody/tr/td[2]/table/tbody/tr[2]/td/div').text)[0])
    if int(cnum) != int(num):
        class_name = re.findall('newsClass=(.*?)&',driver.current_url)[0]
        url = "http://zfcg.yizheng.gov.cn/more.php?page="+str(num)+"&newsClass="+str(class_name)+"&userId=70&num=&pageSize=30&browseURL=/detail.php&departmentId=&officeId="
        driver.get(url)
        locator = (By.XPATH, '//table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div[1]/a[not(contains(string(),"%s"))]' % val)
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located(locator))
    locator =(By.XPATH,'//table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div')
    WebDriverWait(driver,30).until(EC.visibility_of_all_elements_located(locator))
    data = []
    page = driver.page_source
    body = etree.HTML(page)
    content_list = body.xpath('//table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr[1]/td/div')
    for content in content_list:
        name = content.xpath("./a/text()")[0].strip()
        ggstart_time = '0000-00-00'
        url = "http://zfcg.yizheng.gov.cn" + content.xpath("./a/@href")[0]
        temp = [name, ggstart_time, url]
        data.append(temp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='pagination_index_last']")
    WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located(locator))
    total_page = int(re.findall('共 (\d+) 页',driver.find_element_by_xpath("//div[@class='pagination_index_last']").text)[0])
    driver.quit()
    return total_page


data = [

    ["zfcg_zhaobiao_gg", "http://www.yizheng.gov.cn/yzggzyjy/cggg/jyxx_list.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg", "http://www.yizheng.gov.cn/yzggzyjy/cgjggg/jyxx_list.shtml",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp,**kwargs):
    est_meta(conp, data=data, diqu="江苏省仪征市",**kwargs)
    est_html(conp, f=f3,**kwargs)


if __name__ == "__main__":
    conp=["postgres", "since2015", "192.168.3.171", "jiangsu", "yizheng"]
    work(conp)