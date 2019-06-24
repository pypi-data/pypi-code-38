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


_name_="zigong"




def f1(driver, num):
    url = driver.current_url

    locator = (By.XPATH, "//div[@id='main']/ul/li[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//ul[@class='m-pagination-page']/li[@class='active']/a")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(str)
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@id='main']/ul/li[last()]//a").get_attribute('href')[-35:]
        if 'about' in url:
            s = "%d.html" % num if num > 1 else "about2.html"
            url = re.sub("about2\.html", s, url)
        elif num == 1:
            url = re.sub("[0-9]*\.html", "about2.html", url)
        else:
            s = "%d.html" % num if num > 1 else "about2.html"
            url = re.sub("[0-9]*\.html", s, url)
        driver.get(url)
        locator = (By.XPATH, "//div[@id='main']/ul/li[last()]//a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("div", id="main").ul
    trs = table.find_all("li")
    data = []
    for tr in trs:
        info = {}

        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        href = a['href'].strip()
        if 'http' in href:
            link = href
        else:
            link = "http://www.zgggzy.cn" + href
        td = tr.find("span", class_="wb-data-date").text.strip()
        if tr.find("font", attrs={'color':re.compile(r'.*F$'),'class':False }):
            diqu = tr.find("font", attrs={'color':re.compile('.*F$'),'class':False }).text.strip()
            diqu = re.findall(r'\[(.*)\]', diqu)[0]
            info['diqu'] = diqu
        if tr.find("font", attrs={'color': re.compile(r'.*0$'),'class':False }):
            lx = tr.find("font", attrs={'color': re.compile('.*0$'),'class':False }).text.strip()
            lx = re.findall(r'\[(.*)\]', lx)[0]
            info['lx'] = lx
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:info=None
        tmp = [title, td, link, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@id='main']/ul/li[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        ul = soup.find('ul', class_='m-pagination-page')
        num = ul.find_all('li')[-1].a.text.strip()
    except:
        num = 1

    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    time.sleep(0.5)
    html = driver.page_source
    if ("您请求的文件不存在" in html) or ("找不到文件" in html):
        return 404
    locator = (By.XPATH, "//div[@id='content'][string-length()>30] | //div[@class='ewb-info-main ewb-mt10 clearfix'][string-length()>30]")
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
    div = soup.find('div', id="content")
    if div == None:
        div = soup.find('div', class_='ewb-info-main ewb-mt10 clearfix')
    return div







data = [
    ["zfcg_zhaobiao_gg",
     "http://www.zgggzy.cn/jyfwdt/003002/003002001/about2.html",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_biangeng_gg",
     "http://www.zgggzy.cn/jyfwdt/003002/003002002/about2.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://www.zgggzy.cn/jyfwdt/003002/003002003/about2.html",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_wsjj_gg",
     "http://www.zgggzy.cn/jyfwdt/003002/003002005/003002005001/about2.html",
     ["name", "ggstart_time", "href", "info"],add_info(f1, info={'zbfs':'网上竞价'}),f2],

    ["zfcg_zhongbiao_wsjj_gg",
     "http://www.zgggzy.cn/jyfwdt/003002/003002005/003002005002/about2.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, info={'zbfs':'网上竞价'}), f2],

    ["zfcg_zhaobiao_zhigou_gg",
     "http://www.zgggzy.cn/jyfwdt/003002/003002006/about2.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, info={'zbfs':'直购'}), f2],

    ["jqita_gqita_zhao_zhong_gg",
     "http://www.zgggzy.cn/jyfwdt/003005/about2.html",
     ["name", "ggstart_time", "href", "info"],f1, f2],

]



def work(conp,**args):
    est_meta(conp,data=data,diqu="四川省自贡市",**args)
    est_html(conp,f=f3,**args)



# 网站新增：http://www.zgggzy.cn/?valus=zhxw
# 修改时间：2019/6/24
if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","sichuan","zigong"])

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
