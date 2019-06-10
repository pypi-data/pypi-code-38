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
from zhulong3.util.etl import est_html, est_meta, add_info

_name_ = "shanxi_yulin"


def f1(driver, num):
    locator = (By.XPATH, "//td[@height='115']/div/table/tbody/tr[1]//a[last()]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        locator = (By.XPATH, '//select[@id="id1"]/option[@selected]')
        total = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = re.findall(r'第(\d+)页', total)[0]
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath('//td[@height="115"]/div/table/tbody/tr[1]//a[last()]').get_attribute('href')[-15:]
        s = Select(driver.find_element_by_id('id1'))
        s.select_by_visible_text('第{}页'.format(num))

        locator = (By.XPATH, "//td[@height='115']/div/table/tbody/tr[1]//a[last()][not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("td", height='115').div.table.tbody
    lis = div.find_all('tr')
    data = []
    for li in lis:
        a = li.find_all("a")[-1]
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()

        span = li.find_all("td")[-1].text.strip()
        span = re.findall(r'\((.*)\)', span)[0]
        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = 'http://ylgcjyzx.com/' + link
        tmp = [title, span, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//td[@height='115']/div/table/tbody/tr[1]//a[last()]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//select[@id='id1']/option[last()]")
        total = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = re.findall(r'第(\d+)页', total)[0]
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//td[@class='p1']")
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
    div = soup.find('td', class_='p1')
    # div=div.find_all('div',class_='ewb-article')[0]
    return div


data = [
    ["gcjs_zhongbiao_gg",
     "http://ylgcjyzx.com/news_more3.asp?lm2=83",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp, **args):
    est_meta(conp, data=data, diqu="陕西省榆林市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang2", "shanxi_yulin"])

    # driver = webdriver.Chrome()
    # url = "http://ylgcjyzx.com/news_more3.asp?lm2=83"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    #
    # driver=webdriver.Chrome()
    # url = "http://ylgcjyzx.com/news_more3.asp?lm2=83"
    # driver.get(url)
    # for i in range(3, 5):
    #     df=f1(driver, i)
    #     print(df.values)
