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
from zhulong.util.etl import est_html, est_meta,add_info

_name_ = "lianzhou"


def f1(driver, num):
    locator = (By.XPATH, "//table[@class='newtable']/tbody/tr[1]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//span[@class='current']")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
        cnum = int(cnum)
    except:
        cnum = 1
    if num != cnum:
        val = driver.find_element_by_xpath("//table[@class='newtable']/tbody/tr[1]/td/a").get_attribute('href')[-30:]
        driver.execute_script('javascript:goPage({})'.format(num))
        locator = (By.XPATH, "//table[@class='newtable']/tbody/tr[1]/td/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("table", class_="newtable")
    trs = div.find_all("tr")
    data = []
    for tr in trs[:-2]:
        a = tr.find('a')
        title = a.text.strip()
        title = title.split('、', maxsplit=1)[1].strip()
        td = tr.find('td', width="80").text.strip()
        href = a['href'].strip()
        tmp = [title, td, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df["info"] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//table[@class='newtable']/tbody/tr[1]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@class='scott']/a[last()]")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')
        total = re.findall(r'goPage\((\d+)\)', str)[0]
        total = int(total)
    except:
        total = 1
    driver.quit()
    return total


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='maincont'][string-length()>30] | //div[@class='zw_c_cont'][string-length()>30]")
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
    div = soup.find('table', class_='lefttable')
    if div == None:
        div = soup.find('table', class_='zw_c_cont')
    return div


data = [
    ["gcjs_zhaobiao_gg", "https://www.qyggzy.cn/webIndex/newsLeftBoard//010201/01020102",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["gcjs_zhongbiaohx_gg", "https://www.qyggzy.cn/webIndex/newsLeftBoard//010202/01020202",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhaobiao_gg", "https://www.qyggzy.cn/webIndex/newsLeftBoard//010304/01030402",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_gqita_bian_cheng_gg", "https://www.qyggzy.cn/webIndex/newsLeftBoard//010305/01030502",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_gqita_zhong_liu_gg", "https://www.qyggzy.cn/webIndex/newsLeftBoard//010306/01030602",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省连州市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guangdong", "lianzhou"])

    # driver=webdriver.Chrome()
    # url = "https://www.qyggzy.cn/webIndex/newsLeftBoard//010306/01030602"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    # driver=webdriver.Chrome()
    # url = "https://www.qyggzy.cn/webIndex/newsLeftBoard//010306/01030602"
    # driver.get(url)
    # for i in range(2, 3):
    #     df=f1(driver, i)
    #     print(df.values)
    #     for m in df[2].values:
    #         f = f3(driver, m)
    #         print(f)