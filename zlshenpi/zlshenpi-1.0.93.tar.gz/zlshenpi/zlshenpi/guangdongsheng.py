import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zlshenpi.util.etl import add_info, est_meta, est_html, est_tbs, add_info
import sys
import time
import json

_name_ = "guangdongsheng"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='per95']/table/tbody/tr[child::td][1]/td/div/a")
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-20:]
    locator = (By.XPATH, "//span[@class='current']")
    cnum = int(WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text)
    if num != int(cnum):
        driver.execute_script('javascript:jumpPage(%s)' % num)
        locator = (By.XPATH, "//div[@class='per95']/table/tbody/tr[child::td][1]/td/div/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    body = etree.HTML(page)
    contents = body.xpath("//div[@class='per95']/table/tbody/tr[child::td]")
    data = []
    for content in contents:
        name = content.xpath('./td/div/a/text()')[0].strip()
        href = 'http://www.gdtz.gov.cn'+content.xpath('./td/div/a/@href')[0].strip()
        xm_code = content.xpath("./td[1]/text()")[0].strip()
        process = content.xpath('./td[3]/div/text()')[0].strip()
        status = content.xpath('./td[4]/text()')[0].strip()
        ggstart_time = content.xpath('./td[last()]/div/text()')[0].strip()
        info = json.dumps({'xm_code': xm_code, "process": process, 'status': status}, ensure_ascii=False)
        tmp = [name,  ggstart_time,href , info]

        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='badoo']/a[last()]")
    txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')
    total_page = int(re.findall('\d+', txt)[0])
    return total_page


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='per95']")
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
    div = soup.find('div', class_="per95")
    return div


data = [
    ["xm_shenpi_gg",
     "http://www.gdtz.gov.cn/tybm/apply3!searchMore3.action",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres","since2015","192.168.3.171","zlshenpi","guangdong"],num=3)

    # url = "http://www.gdtz.gov.cn/tybm/apply3!searchMore3.action"
    # driver = webdriver.Chrome()
    # driver.get(url)
    # f1(driver,44)
