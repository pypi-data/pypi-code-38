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
import requests
import time
from zhulong.util.etl import est_html, est_meta,add_info
from zhulong.util.fake_useragent import UserAgent

_name_ = "yingde"


def f1(driver, num):
    locator = (By.XPATH, "//table[@class='newtable']/tbody/tr[1]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//span[@class='current']")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    cnum = int(cnum)
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
    locator = (By.XPATH, "//div[@class='scott']/a[last()]")
    str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')
    total = re.findall(r'goPage\((\d+)\)', str)[0]
    total = int(total)
    driver.quit()
    return total


def f3(driver, url):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    except:
        proxies={}

    ua = UserAgent()

    headers = {
        "User-Agent": ua.chrome,
    }

    req=requests.get(url,proxies=proxies,headers=headers,timeout=20)
    if req.status_code != 200:
        raise ValueError('status code is %s'%req.status_code)
    page=req.text

    # driver.get(url)
    #
    # locator = (By.XPATH, "//table[@class='lefttable'][string-length()>30]")
    # WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    #
    # before = len(driver.page_source)
    # time.sleep(0.1)
    # after = len(driver.page_source)
    # i = 0
    # while before != after:
    #     before = len(driver.page_source)
    #     time.sleep(0.1)
    #     after = len(driver.page_source)
    #     i += 1
    #     if i > 5: break
    # page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('table', class_='lefttable')

    return div


data = [
    ["gcjs_zhaobiao_gg", "https://www.ydjyzx.cn/webIndex/newsLeftBoard//0102/010201",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_bian_bu_gg", "https://www.ydjyzx.cn/webIndex/newsLeftBoard//0102/010205",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_zhong_liu_gg", "https://www.ydjyzx.cn/webIndex/newsLeftBoard//0102/010202",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    #
    ["zfcg_zhaobiao_gg", "https://www.ydjyzx.cn/webIndex/newsLeftBoard//0103/010304",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_bian_zhongz_gg", "https://www.ydjyzx.cn/webIndex/newsLeftBoard/0103/010305",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_zhong_liu_gg", "https://www.ydjyzx.cn/webIndex/newsLeftBoard//0103/010306",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省英德市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "zhulong.com.cn", "192.168.169.47", "guangdong", "yingde"],num=1)

# url="https://www.ydjyzx.cn/webIndex/detailAllNews/C4319E2CB8F44DCE96E802EFDBF6727C"
# driver=webdriver.Chrome()

# driver.get(url)