import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write,db_command,db_query
from selenium.webdriver import DesiredCapabilities
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


_name_="shifang"



def f1(driver, num):
    url = driver.current_url
    locator = (By.XPATH, "//ul[@class='list_ul_xzf']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@class='paging']/a[last()]")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = re.findall(r'(\d+)/', st)[0]
    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='list_ul_xzf']/li[1]/a").get_attribute('href')[-10:]
        driver.execute_script("page_to({})".format(num))
        locator = (By.XPATH, "//ul[@class='list_ul_xzf']/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("ul", class_='list_ul_xzf')
    trs = table.find_all("li")
    data = []
    for tr in trs:
        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        href = a['href'].strip()
        if "http" in href:
            link = href
        else:
            link = "http://www.shifang.gov.cn" + href
        span = tr.find_all('span')[-1].text.strip()
        tmp = [title, span, link]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df





def f2(driver):
    locator = (By.XPATH, "//ul[@class='list_ul_xzf']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@class='paging']/a[last()]")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'/(\d+)', st)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    iframe = soup.find('iframe', id="ifr1")
    div1 = ''
    if iframe:
        divs = soup.find_all('div', class_='docInfo')
        for d in divs:
            div1 += str(d)
        driver.switch_to.frame('ifr1')
        locator = (By.XPATH, "//span[@id='numPages'][not(contains(text(), '0'))]")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        tnum = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//span[@id='numPages']"))).text.strip()
        tnum = int(re.findall(r'(\d+)', tnum)[0])
        if tnum != 1:
            for _ in range(tnum-1):
                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//button[@id='next']"))).click()
                try:
                    locator = (By.XPATH, "//div[@class='page'][last()][string-length()>40][string-length()>40]")
                    WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located(locator))
                except:
                    locator = (By.XPATH, "//div[@class='page'][last()-1][string-length()>40][string-length()>40]")
                    WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located(locator))
    locator = (By.XPATH, "//div[@id='viewerContainer'][string-length()>40] | //table[@style='width:100%;']")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
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
    div2 = soup.find('div', id="viewerContainer")
    if div2 == None:
        div2 = soup.find('table', style='width:100%;')
    div = str(div2) + div1
    return div


data = [

    ["zfcg_gqita_zhao_bian_gg",
     "http://www.shifang.gov.cn/gov/search_file?cateValue=0&cateType=11",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_zhong_liu_gg",
     "http://www.shifang.gov.cn/gov/search_file?cateValue=1&cateType=11",
     ["name", "ggstart_time", "href", "info"],f1,f2],
]



def work(conp,**args):
    est_meta(conp,data=data,diqu="四川省什邡市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","sichuan","shifang"])
