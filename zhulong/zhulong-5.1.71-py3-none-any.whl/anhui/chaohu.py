import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write, db_command, db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import sys
import time

import json

from zhulong.util.etl import est_tbs, est_meta, est_html, gg_existed

# driver=webdriver.Chrome()

# url="""http://jyzx.yiyang.gov.cn/jyxx/003001/003001001/2.html"""

# driver.get(url)

_name_ = 'chaohu'


def f1(driver, num):

    locator = (
        By.XPATH, '//table[@bgcolor="#e4e4e4"]/tbody/tr[2]/td[3]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    cnum=driver.find_element_by_xpath('//font[@color="#FF6600"][1]').text

    if int(cnum) != num:
        val = driver.find_element_by_xpath(
            '//table[@bgcolor="#e4e4e4"]/tbody/tr[2]/td[3]/a').get_attribute('href')[-20:]
        driver.execute_script('javascript:goPage(%d)'%num)

        locator = (By.XPATH,
                   '//table[@bgcolor="#e4e4e4"]/tbody/tr[2]/td[3]/a[not(contains(string(),"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    trs = soup.find('table', attrs={'bgcolor': '#e4e4e4'}).find('tbody').find_all('tr',recursive=False)[1:]

    for tr in trs:
        tds = tr.find_all('td',recursive=False)
        href = tds[2].a['href']
        index_num=tds[1].get_text().strip()
        ggstart_time = tds[3].get_text().strip()
        name=tds[4].find('td',style="word-break:break-all;",valign="top").get_text().strip()

        if 'http' in href:
            href = href
        else:
            href = 'http://zwgk.hefei.gov.cn' + href
        info={'index_num':index_num}
        info=json.dumps(info,ensure_ascii=False)

        tmp = [name, ggstart_time, href,info]

        data.append(tmp)
    df = pd.DataFrame(data=data)

    return df



def f2(driver):
    locator = (By.XPATH, '//table[@bgcolor="#e4e4e4"]/tbody/tr[2]/td[3]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    total =driver.find_element_by_xpath('//font[@color="#FF6600"][2]').text
    total = int(total)

    driver.quit()
    return total



def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//table[@class="bk"][string-length()>10]')

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

    div = soup.find('table', class_='bk')

    return div

data=[

    ["gcjs_zhaobiao_gg","http://zwgk.hefei.gov.cn/zwgk/public/spage.xp?doAction=sxxlist&cid=&type=1&mlid=0012001600130001&unitid=000400010013",[  'name', 'ggstart_time', 'href','info'],f1,f2],
    ["gcjs_zhongbiao_gg","http://zwgk.hefei.gov.cn/zwgk/public/spage.xp?doAction=sxxlist&cid=&type=1&mlid=0012001600130002&unitid=000400010013",[  'name', 'ggstart_time', 'href','info'],f1,f2],
    ["zfcg_zhaobiao_gg","http://zwgk.hefei.gov.cn/zwgk/public/spage.xp?doAction=sxxlist&cid=&type=1&mlid=0012001600070002&unitid=000400010013",[  'name', 'ggstart_time', 'href','info'],f1,f2],
    ["zfcg_zhongbiao_gg","http://zwgk.hefei.gov.cn/zwgk/public/spage.xp?doAction=sxxlist&cid=&type=1&mlid=0012001600070003&unitid=000400010013",[  'name', 'ggstart_time', 'href','info'],f1,f2],

]

def work(conp, **arg):
    est_meta(conp, data=data, diqu="安徽省巢湖市", **arg)

    est_html(conp, f=f3, **arg)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.4.175", "anhui", "chaohu"])

