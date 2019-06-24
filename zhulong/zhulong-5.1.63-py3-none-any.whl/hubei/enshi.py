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

from zhulong.util.etl import est_tbs, est_meta, est_html, gg_existed, est_gg

# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://ggzy.hefei.gov.cn/jyxx/002001/002001002/moreinfo_jyxx.html"
# driver=webdriver.Chrome()
# driver.minimize_window()
# driver.get(url)


_name_ = 'enshi'


def f1(driver, num):
    locator = (By.XPATH, '//div[@class="morelist"]/table//tr[1]/td[2]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum = driver.find_element_by_xpath('//td[@class="huifont"]').text.strip()

    cnum = re.findall('(\d+?)/', cnum)[0]

    if int(cnum) != num:
        val = driver.find_element_by_xpath('//div[@class="morelist"]/table//tr[1]/td[2]/a').get_attribute('href')[-30:]

        driver.execute_script("window.location.href='./?Paging={}'".format(num))

        locator = (By.XPATH, '//div[@class="morelist"]/table//tr[1]/td[2]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    div = soup.find('div', class_='morelist').find('table')
    lis = div.find_all('tr')
    for li in lis:
        href = li.find('td', align='left').a['href']
        name = li.find('td', align='left').a['title']
        ggstart_time = li.find('td', align='right').span.get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://es.eszggzy.cn' + href
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, '//div[@class="morelist"]/table//tr[1]/td[2]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.find_element_by_xpath('//td[@class="huifont"]').text

    total = re.findall('/(\d+)', page)[0]
    total = int(total)

    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//td[@class="infodetail"]')

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

    div = soup.find('td', class_='infodetail')

    return div


data = [
    #
    ["gcjs_zhaobiao_gg", "http://es.eszggzy.cn/esweb/jyxx/070001/070001001/", ['name', 'ggstart_time', 'href', 'info'], f1, f2],
    ["gcjs_biangeng_gg", "http://es.eszggzy.cn/esweb/jyxx/070001/070001002/", ['name', 'ggstart_time', 'href', 'info'], f1, f2],
    ["gcjs_zhongbiaohx_gg", "http://es.eszggzy.cn/esweb/jyxx/070001/070001003/", ['name', 'ggstart_time', 'href', 'info'], f1, f2],
    ["gcjs_liubiao_gg", "http://es.eszggzy.cn/esweb/jyxx/070001/070001004/", ['name', 'ggstart_time', 'href', 'info'], f1, f2],

    ["zfcg_zhaobiao_gg", "http://es.eszggzy.cn/esweb/jyxx/070002/070002001/", ['name', 'ggstart_time', 'href', 'info'], f1, f2],
    ["zfcg_biangeng_gg", "http://es.eszggzy.cn/esweb/jyxx/070002/070002002/", ['name', 'ggstart_time', 'href', 'info'], f1, f2],
    ["zfcg_zhongbiao_gg", "http://es.eszggzy.cn/esweb/jyxx/070002/070002003/", ['name', 'ggstart_time', 'href', 'info'], f1, f2],
    ["zfcg_liubiao_gg", "http://es.eszggzy.cn/esweb/jyxx/070002/070002004/", ['name', 'ggstart_time', 'href', 'info'], f1, f2],

    ["qsy_zhaobiao_gg", "http://es.eszggzy.cn/esweb/jyxx/070005/070005001/", ['name', 'ggstart_time', 'href', 'info'], f1, f2],
    ["qsy_biangeng_gg", "http://es.eszggzy.cn/esweb/jyxx/070005/070005002/", ['name', 'ggstart_time', 'href', 'info'], f1, f2],
    ["qsy_zhongbiao_gg", "http://es.eszggzy.cn/esweb/jyxx/070005/070005003/", ['name', 'ggstart_time', 'href', 'info'], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖北省恩施市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    conp = ["postgres", "since2015", "192.168.3.171", "hubei", "enshi"]

    work(conp=conp)
