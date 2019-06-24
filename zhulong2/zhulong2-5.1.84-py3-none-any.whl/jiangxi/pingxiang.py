import time

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from zhulong2.util.etl import est_tbs, est_meta, est_html, est_gg, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hengyang.gov.cn/jyxx/jsgc/zbgg_64796/index.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)

_name_ = 'jiangxi_pingxiang'

def f1(driver, num):
    locator = (By.XPATH, '(//td[@bgcolor="#FFFFFF"])[1]/a')
    WebDriverWait(driver, 5).until(EC.presence_of_element_located(locator))

    url = driver.current_url
    cnum = int(re.findall("PageNo=(\d+?)&", url)[0])

    if num != cnum:
        s = "PageNo=%d&" % (num)
        url = re.sub("PageNo=(\d+?)&", s, url)
        val = driver.find_element_by_xpath('(//td[@bgcolor="#FFFFFF"])[1]/a').get_attribute('href')[-10:]
        driver.get(url)
        locator = (By.XPATH, '(//td[@bgcolor="#FFFFFF"])[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    ht = driver.page_source
    soup = BeautifulSoup(ht, 'html.parser')
    uls = soup.find_all('td', bgcolor="#FFFFFF")

    data = []
    for li in uls:
        name = li.a.get_text()
        href = li.a['href']
        href = 'http://bmwz.pingxiang.gov.cn/cgw/more/' + href
        ggstart_time='k'
        tmp = [name, href,ggstart_time]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None

    return df


def f2(driver):
    locator = (By.XPATH, '(//td[@bgcolor="#FFFFFF"])[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total = driver.find_element_by_xpath('//font[@color="#ff3333"][1]').text
    total=int(total)
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//td[@bgcolor="#FFFFFF"][string-length()>10]')

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
    div = soup.find('td', bgcolor="#FFFFFF")
    return div


data = [
    ###包含变更,招标
    ["zfcg_zhaobiao_diqu1_gg", "http://bmwz.pingxiang.gov.cn/cgw/more/more.asp?PageNo=1&id=&n=%D5%D0%B1%EA%D0%C5%CF%A2",["name", "href", 'ggstart_time','info'], add_info(f1,{'diqu':'市本级'}), f2],
    ["zfcg_zhaobiao_diqu2_gg", "http://bmwz.pingxiang.gov.cn/cgw/more/more.asp?PageNo=1&id=&n=%CF%D8%C7%F8%D5%D0%B1%EA%D0%C5%CF%A2",["name",  "href",'ggstart_time', 'info'], add_info(f1,{'diqu':'区县'}), f2],
    ##包含中标,流标
    ["zfcg_zhongbiao_gg", "http://bmwz.pingxiang.gov.cn/cgw/more/more1.asp?PageNo=1&id=&n=%D6%D0%B1%EA",["name", "href", 'ggstart_time', 'info'], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="江西省萍乡市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    conp = ["postgres", "since2015", "192.168.3.171", "lch", "jiangxi_pingxiang"]

    work(conp=conp,haadless=False,num=1)