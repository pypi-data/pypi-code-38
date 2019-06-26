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


_name_="ziyang"



def f1(driver, num):
    url = driver.current_url
    locator = (By.XPATH, "//div[@class='contentSe']/table/tbody/tr[last()]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@class='mmggxlh']/a[@class='cur']")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()

    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@class='contentSe']/table/tbody/tr[last()]/td/a").get_attribute('href')[-50:]
        driver.execute_script("pagination({})".format(num))
        locator = (By.XPATH, "//div[@class='contentSe']/table/tbody/tr[last()]/td/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("div", class_='contentSe').table.tbody
    trs = table.find_all("tr")
    data = []
    for tr in trs[1:]:
        a = tr.find('a')
        try:
            name = a['title'].strip()
        except:
            name = a.text.strip()
        href = a['href'].strip()
        if "http" in href:
            link = href
        else:
            link = "http://ggzyjyzx.ziyang.gov.cn" + href
        ggstart_time = tr.find_all('td')[-1].text.strip()
        info={}
        if tr.find('td', align="center"):
            xm_code = tr.find('td', align="center").text.strip()
            if xm_code:info['xm_code']=xm_code
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:info=None
        tmp = [name, ggstart_time, link, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df





def f2(driver):
    locator = (By.XPATH, "//div[@class='contentSe']/table/tbody/tr[last()]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//div[@class='mmggxlh']/a[last()-1]")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    driver.quit()
    return int(st)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='content'][string-length()>40]")
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
    div = soup.find('div', class_="content")
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://ggzyjyzx.ziyang.gov.cn/jyxx/jsgcZbgg?city=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_bian_bu_gg",
     "http://ggzyjyzx.ziyang.gov.cn/jyxx/jsgcBgtz?city=",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_liubiao_gg",
     "http://ggzyjyzx.ziyang.gov.cn/jyxx/jsgcZbyc?city=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://ggzyjyzx.ziyang.gov.cn/jyxx/zfcg/cggg?city=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "http://ggzyjyzx.ziyang.gov.cn/jyxx/zfcg/gzsx?city=",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_wsjj_gg",
     "http://ggzyjyzx.ziyang.gov.cn/jyxx/zfcg/jjcg?city=",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'网上竞价'}), f2],

    ["zfcg_zhongbiao_wsjj_gg",
     "http://ggzyjyzx.ziyang.gov.cn/jyxx/zfcg/jjjg?city=",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '网上竞价'}), f2],
]



def work(conp,**args):
    est_meta(conp,data=data,diqu="四川省资阳市",**args)
    est_html(conp,f=f3,**args)


# 网站新增：http://ggzyjyzx.ziyang.gov.cn/?city=
# 修改时间：2019/6/20
if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","sichuan","ziyang"])


    # driver = webdriver.Chrome()
    # for d in data:
    #     driver.get(d[1])
    #     print(d[1])
    #     df = f2(driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     df = f1(driver,1)
    #     print(df.values)
    #     for j in df[2].values:
    #         df = f3(driver, j)
    #         print(df)
