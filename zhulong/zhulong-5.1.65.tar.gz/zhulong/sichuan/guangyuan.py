import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write,db_command,db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import json
from zhulong.util.etl import add_info,est_meta,est_html,est_tbs


_name_="guangyuan"





def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='wb-data-item']/li[1]/div/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//li[@class='ewb-page-li current']")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(st)
    except:
        cnum = 1
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='wb-data-item']/li[1]/div/a").get_attribute('href')[-30:]
        if "about.html" in url:
            s = "%d.html" % (num) if num > 1 else "1.html"
            url = re.sub(r"about\.html", s, url)
        elif num == 1:
            url = re.sub("[0-9]*\.html", "1.html", url)
        else:
            s = "%d.html" % (num) if num > 1 else "1.html"
            url = re.sub("[0-9]*\.html", s, url)
        driver.get(url)
        try:
            locator = (By.XPATH, "//ul[@class='wb-data-item']/li[1]/div/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            driver.refresh()
            locator = (By.XPATH, "//ul[@class='wb-data-item']/li[1]/div/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 3).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("ul", class_="wb-data-item")
    trs = table.find_all("li", class_="wb-data-list")
    data = []
    for tr in trs:
        a = tr.find("a")
        link = "http://www.gyggzyjy.cn" + a['href'].strip()
        td = tr.find("span", class_='wb-data-date').text.strip()
        zblx = a.find('font', color="#FF6600")
        info = {}
        if zblx != None:
            zblx = a.find('font', color="#FF6600").extract().text.strip()
            if '[' in zblx:zblx = re.findall(r'\[(.*)\]', zblx)[0]
            info['zblx'] = zblx
        title = a.text.strip()
        if re.findall(r'^\[(.*?)\]', title):
            lx = re.findall(r'^\[(.*?)\]', title)[0]
            info['lx'] = lx
        if re.findall(r'.+\[(.*?)\]$', title):
            title = title.rsplit('[', maxsplit=1)[0]
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:
            info = None
        tmp = [title, td, link, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df





def f2(driver):
    locator = (By.XPATH, "//ul[@class='wb-data-item']/li[1]/div/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "(//li[@class='ewb-page-li ']/a)[last()]")
        num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        num = 1
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    if '404' in driver.title:
        return 404
    locator = (By.XPATH, "//div[@class='ewb-main'][string-length()>30]")
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
    div = soup.find('div', class_="ewb-con")
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.gyggzyjy.cn/ggfwpt/012001/012001001/012001001001/about.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_bian_bu_gg",
     "http://www.gyggzyjy.cn/ggfwpt/012001/012001001/012001001002/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.gyggzyjy.cn/ggfwpt/012001/012001001/012001001003/about.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiao_gg",
     "http://www.gyggzyjy.cn/ggfwpt/012001/012001001/012001001004/about.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zgysjg_gg",
     "http://www.gyggzyjy.cn/ggfwpt/012001/012001001/012001001006/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://www.gyggzyjy.cn/ggfwpt/012001/012001002/012001002002/about.html",
    ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_biangeng_gg",
     "http://www.gyggzyjy.cn/ggfwpt/012001/012001002/012001002003/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://www.gyggzyjy.cn/ggfwpt/012001/012001002/012001002004/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_liubiao_gg",
     "http://www.gyggzyjy.cn/ggfwpt/012001/012001002/012001002007/about.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_gqita_zhao_bian_gg",
     "http://www.gyggzyjy.cn/ggfwpt/012001/012001005/012001005001/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'jylx':'其他'}), f2],

    ["qsy_gqita_zhong_liu_gg",
     "http://www.gyggzyjy.cn/ggfwpt/012001/012001005/012001005002/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'jylx':'其他'}), f2],
]



def work(conp,**args):
    est_meta(conp,data=data,diqu="四川省广元市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","sichuan","guangyuan"])



