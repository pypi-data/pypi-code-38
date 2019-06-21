import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from zhulong4.util.etl import est_html, est_meta, add_info

_name_ = "www_gmgitc_com"


def f1(driver, num):
    locator = (By.XPATH, "//table[@class='FontBlue']/tbody/tr[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        locator = (By.XPATH, "//span[@id='ctl00_PageContent_lblCurrentIndex']")
        total = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = re.findall(r'(\d+)', total)[0]
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@class='FontBlue']/tbody/tr[1]//a").get_attribute('href')[-20:]
        s = True
        n = num
        for _ in range(n):
            html_data = driver.page_source
            html_soup = BeautifulSoup(html_data, "html.parser")
            div = html_soup.find("table", id='ctl00_PageContent_DataGrid1').tbody
            tr = div.find('tr', attrs={'align': 'right','class':'FontBlue'})
            als = tr.find_all('a')
            k=0
            for al in als:
                anum = al.text.strip()
                if anum == '...':
                    continue
                elif int(anum) == num:
                    k = 1
                    break
                elif int(anum) > num:
                    k = 2
                elif int(anum) < num:
                    k = 3
            if k==1:
                break
            elif k==2:
                driver.find_element_by_xpath("//table[@class='FontBlue']/tbody/tr[last()]//a[1]").click()
            elif k==3:
                driver.find_element_by_xpath("//table[@class='FontBlue']/tbody/tr[last()]//a[last()]").click()
            locator = (By.XPATH, "//span[@id='ctl00_PageContent_lblCurrentIndex']")
            total2 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            cnum2 = re.findall(r'(\d+)', total2)[0]
            if int(cnum2) == num:
                s = False
                break
        if s:
            driver.find_element_by_link_text("{}".format(num)).click()
        locator = (By.XPATH, "//table[@class='FontBlue']/tbody/tr[1]//a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("table", id='ctl00_PageContent_DataGrid1').tbody
    lis = div.find_all('tr', attrs={'align':''})
    data = []
    for li in lis:
        a = li.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        link = a["href"]
        if 'http' in link:
            href = link
        else:
            urls = url.rsplit('/', maxsplit=1)[0]
            href = urls + '/' + link
        if "Notice/Clarify/" in url:
            span = li.find_all("td")[0].text.strip()
            endtime = li.find_all("td")[-1].text.strip()
            info = json.dumps({'endtime':endtime}, ensure_ascii=False)
        else:
            span = li.find_all("td")[-1].text.strip()
            info = None
        tmp = [title, span, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    locator = (By.XPATH, "//table[@class='FontBlue']/tbody/tr[1]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//span[@id='ctl00_PageContent_lblPageCount']")
        total = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = re.findall(r'(\d+)', total)[0]
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@width='90%'][1] | //table[@width='744']")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    try:
        driver.find_element_by_xpath('//iframe[@marginwidth="0"]')
        locator = (By.XPATH, '//iframe[@marginwidth="0"]')
        dt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        driver.switch_to_frame(dt)
        locator = (By.XPATH, '//body[@marginwidth="0"]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        flag = 1
    except:
        flag = 0
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
    if flag != 1:
        div = soup.find('table', width='90%')
        if div == None:
            div = soup.find('table', width='744')
    else:
        div1 = soup.find('body', attrs={'marginwidth':'0'})
        driver.switch_to.parent_frame()
        soup2 = BeautifulSoup(driver.page_source, 'html.parser')
        div2 = soup2.find('td', width='744')
        if div2:
            div = str(div2) + str(div1)
        else:
            div = div1

    return div


data = [
    ["qy_zhaobiao_gg",
     "http://www.gmgitc.com/Notice/BidInfo/List.aspx",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qy_zhongbiao_gg",
     "http://www.gmgitc.com/Notice/BidResult/List.aspx",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qy_biangeng_gg",
     "http://www.gmgitc.com/Notice/Clarify/List.aspx",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="国义招标", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang3", "www_gmgitc_com"],pageloadtimeout=60,pageLoadStrategy="none")

    # driver = webdriver.Chrome()
    # url = "http://www.gmgitc.com/Notice/BidInfo/List.aspx"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    #
    # driver=webdriver.Chrome()
    # url = "http://www.gmgitc.com/Notice/BidInfo/List.aspx"
    # driver.get(url)
    # for i in range(31, 33):
    #     df=f1(driver, i)
    #     print(df.values)
