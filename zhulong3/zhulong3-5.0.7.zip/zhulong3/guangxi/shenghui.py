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

import json

import time

from zhulong3.util.etl import est_html, est_meta, add_info,est_meta_large

_name_ = "guangxi_shenghui"


def f1(driver, num):
    locator = (By.XPATH, '//table[@cellpadding="4"]/tbody/tr[2]/td/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    # url = driver.current_url
    try:
        locator = (By.XPATH, '//div[@id="AspNetPager1"]/table/tbody/tr/td[1]/font[3]/b')
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath('//table[@cellpadding="4"]/tbody/tr[2]/td/a').get_attribute('href')[-15:]

        driver.execute_script("javascript:__doPostBack('AspNetPager1','{}')".format(num))

        locator = (By.XPATH, "//table[@cellpadding='4']/tbody/tr[2]/td/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("table", attrs={'cellpadding':'4', 'cellspacing':'1'}).tbody
    lis = div.find_all("tr")
    data = []
    for li in lis[1:]:
        a = li.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        span = li.find_all("td")[-1].text.strip()
        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = 'http://www.gxcic.net/ztb/' + link

        tds = li.find_all("td")[-2].text.strip()
        td = {'zblx':tds}
        info = json.dumps(td, ensure_ascii=False)
        tmp = [title, span, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, '//table[@cellpadding="4"]/tbody/tr[2]/td/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//div[@id="AspNetPager1"]/table/tbody/tr/td[1]/font[2]/b')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    li = driver.find_element_by_xpath('//div[@id="AspNetPager1"]/table/tbody/tr/td[1]/font[2]/b').text
    total = int(li)
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@style='padding:10px;'] | //div[@class='page-right-box']")
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
    div = soup.find('div', class_='mainbg')
    div = div.find('div', style='padding:10px;')
    if div == None:
        div = soup.find('div', class_='page-right-box')
    # div=div.find_all('div',class_='ewb-article')[0]
    return div


data = [
    ["gcjs_gqita_zhao_zhong_shigong_gg", "http://www.gxcic.net/ztb/ztblist.aspx?ZGZbfl=%CA%A9%B9%A4%D5%D0%B1%EA",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'施工'}), f2],

    ["gcjs_gqita_zhao_zhong_kancha_gg", "http://www.gxcic.net/ztb/ztblist.aspx?ZGZbfl=%BF%B1%B2%EC%D5%D0%B1%EA",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gclx':'勘察'}), f2],

    ["gcjs_gqita_zhao_zhong_sheji_gg", "http://www.gxcic.net/ztb/ztblist.aspx?ZGZbfl=%C9%E8%BC%C6%D5%D0%B1%EA",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'设计'}), f2],

    ["gcjs_gqita_zhao_zhong_guihua_gg", "http://www.gxcic.net/ztb/ztblist.aspx?ZGZbfl=%B3%C7%CF%E7%B9%E6%BB%AE",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'城乡规划'}), f2],

    ["gcjs_gqita_zhao_zhong_jianli_gg", "http://www.gxcic.net/ztb/ztblist.aspx?ZGZbfl=%BC%E0%C0%ED%D5%D0%B1%EA",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'监理'}), f2],

    ["gcjs_gqita_zhao_zhong_cailiao_gg", "http://www.gxcic.net/ztb/ztblist.aspx?ZGZbfl=%B2%C4%C1%CF%C9%E8%B1%B8%D5%D0%B1%EA",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'材料设备'}), f2],

    ["gcjs_gqita_zhao_zhong_qita_gg", "http://www.gxcic.net/ztb/ztblist.aspx?ZGZbfl=%C6%E4%CB%FC%D5%D0%B1%EA",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gclx':'其他'}), f2],
    #
    ["gcjs_zhongbiao_gg", "http://www.gxcic.net/ztb/zblist.aspx",
     ["name", "ggstart_time", "href", "info"], f1, f2],


]



def work(conp,**args):
    est_meta_large(conp, data=data, diqu="广西省省会", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang2", "guangxi_shenghui"])

    # driver = webdriver.Chrome()
    # url = "http://www.gxcic.net/ztb/ztblist.aspx"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    #
    # driver=webdriver.Chrome()
    # url = "http://www.gxcic.net/ztb/ztblist.aspx"
    # driver.get(url)
    # for i in range(1, 6):
    #     df=f1(driver, i)
    #     print(df.values)
