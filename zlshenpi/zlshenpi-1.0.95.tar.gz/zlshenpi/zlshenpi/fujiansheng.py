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

_name_ = "fujiansheng"


def f1(driver, num):
    locator = (By.XPATH, "//table[@id='tb']/tbody/tr[1]")
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute("onclick")[-20:]
    locator = (By.XPATH, "//a[@style='pointer-events:none; cursor:default; ']/span")
    cnum = int(WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator)).text)
    if num != int(cnum):
        driver.execute_script('gotopage(%s)' % num)
        locator = (By.XPATH, """//table[@id='tb']/tbody/tr[1][not(contains(@onclick, "%s"))]""" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    body = etree.HTML(page)
    contents = body.xpath("//table[@id='tb']/tbody/tr[contains(@class,'project')]")
    data = []
    for content in contents:
        # if 'publicPromotion' in driver.current_url:

        name = content.xpath('./td[1]/text()')[0].strip()
        txt_tmp = content.xpath('./@onclick')[0].strip()
        projectcode, biaoji = re.findall("\'([^']+?)\'", txt_tmp)
        href = "https://fj.tzxm.gov.cn:443/eap/credit.publicShow?projectcode=" + projectcode + "&biaoji=" + biaoji
        xm_code = content.xpath("./td[2]/text()")[0].strip()
        area = content.xpath('./td[4]/text()')[0].strip()
        xmtype = content.xpath('./td[5]/text()')[0].strip()

        ggstart_time = content.xpath('./td[3]/text()')[0].strip()
        info = json.dumps({"area": area, 'xmtype': xmtype, "xm_code": xm_code}, ensure_ascii=False)
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)

        print(tmp)

    df = pd.DataFrame(data)
    return df


def f2(driver):
    locator = (By.XPATH, '//a[contains(@onclick,"goto")][last()-1]/span')
    total_page = int(WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text)
    return total_page


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='block_content']")
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
    div = soup.find('div', class_="block_content")
    return div


data = [
    ["xm_jieguo_gg",
     "https://fj.tzxm.gov.cn/eap/credit.searchMsg",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["xm_tuijie_gg",
     "https://fj.tzxm.gov.cn/eap/credit.publicPromotionList",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    # work(conp=["postgres", "since2015", "192.168.3.171", "zlshenpi", "guangdong"], num=50)
    driver = webdriver.Chrome()
    for d in data:
        driver.get(d[1])
        print(d[1])
        f1(driver,1)
    print(f2(driver))