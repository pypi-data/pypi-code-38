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

from zhulong2.util.etl import est_tbs, est_meta, est_html, gg_existed, est_gg, add_info

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://www.dzzfcg.gov.cn/n33754981/n33755353/index.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)


_name_ = 'shandong_dezhou'


def f1(driver, num):
    locator = (By.XPATH, '(//li[@class="fs_14"])[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = driver.find_element_by_xpath('//td[@id="pag_33792302"]/font[@color="red"]').text

    mark1 = re.findall('www.dzzfcg.gov.cn/(.+?)/', url)[0]
    mark2 = re.findall('www.dzzfcg.gov.cn/.+?/(.+?)/', url)[0]

    if num != int(cnum):
        num = total - num + 1
        val = driver.find_element_by_xpath('(//li[@class="fs_14"])[1]/a').get_attribute('href')[-30:]

        driver.execute_script(
            "javascript:pageName={num};goPub('../../{mark1}/{mark2}/index_33792302_{num}.html')".format(num=num,
                                                                                                        mark1=mark1,
                                                                                                        mark2=mark2))
        locator = (By.XPATH, '(//li[@class="fs_14"])[1]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    ht = driver.page_source
    soup = BeautifulSoup(ht, 'html.parser')
    uls = soup.find_all('li', class_="fs_14")

    data = []
    for li in uls:
        name = li.a.get_text()
        href = li.a['href'].strip('../../')
        href = 'http://www.dzzfcg.gov.cn/' + href
        ggstart_time = li.span.get_text()
        tmp = [name, ggstart_time, href]
        data.append(tmp)

    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    global total
    locator = (By.XPATH, '(//li[@class="fs_14"])[1]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        total = driver.find_element_by_xpath('//td[@id="pag_33792302"]').text
        total = re.findall('总页数:(\d+)', total)[0].strip()
        total = int(total)
    except:
        total=1

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="cont_t"][string-length()>10]')

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
    div = soup.find('div', class_="cont_t").parent

    return div


data = [
    ["zfcg_zhaobiao_diqu1_gg", "http://www.dzzfcg.gov.cn/n33754981/n33755148/index.html",
     ['name', 'ggstart_time', 'href', 'info'], add_info(f1, {"diqu": "市级"}), f2],
    ["zfcg_zhaobiao_diqu2_gg", "http://www.dzzfcg.gov.cn/n33754981/n33755153/index.html",
     ['name', 'ggstart_time', 'href', 'info'], add_info(f1, {"diqu": "县级"}), f2],
    ["zfcg_zhongbiao_diqu1_gg", "http://www.dzzfcg.gov.cn/n33754981/n33755353/index.html",
     ['name', 'ggstart_time', 'href', 'info'], add_info(f1, {"diqu": "市级"}), f2],
    ["zfcg_zhongbiao_diqu2_gg", "http://www.dzzfcg.gov.cn/n33754981/n33755403/index.html",
     ['name', 'ggstart_time', 'href', 'info'], add_info(f1, {"diqu": "县级"}), f2],
    ["zfcg_biangeng_diqu1_gg", "http://www.dzzfcg.gov.cn/n33754981/n33755358/index.html",
     ['name', 'ggstart_time', 'href', 'info'], add_info(f1, {"diqu": "市级"}), f2],
    ["zfcg_biangeng_diqu2_gg", "http://www.dzzfcg.gov.cn/n33754981/n33755410/index.html",
     ['name', 'ggstart_time', 'href', 'info'], add_info(f1, {"diqu": "县级"}), f2],

    ["zfcg_yucai_diqu1_gg", "http://www.dzzfcg.gov.cn/n34067983/n34067928/index.html",
     ['name', 'ggstart_time', 'href', 'info'], add_info(f1, {"diqu": "市级"}), f2],
    ["zfcg_yucai_diqu2_gg", "http://www.dzzfcg.gov.cn/n34067983/n34067993/index.html",
     ['name', 'ggstart_time', 'href', 'info'], add_info(f1, {"diqu": "县级"}), f2],
    ["zfcg_yanshou_diqu1_gg", "http://www.dzzfcg.gov.cn/n34067983/n34067933/index.html",
     ['name', 'ggstart_time', 'href', 'info'], add_info(f1, {"diqu": "市级"}), f2],
    ["zfcg_yanshou_diqu2_gg", "http://www.dzzfcg.gov.cn/n34067983/n34067998/index.html",
     ['name', 'ggstart_time', 'href', 'info'], add_info(f1, {"diqu": "县级"}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="山东省德州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    conp = ["postgres", "since2015", "192.168.3.171", "lch", "shandong_dezhou"]

    work(conp=conp)
