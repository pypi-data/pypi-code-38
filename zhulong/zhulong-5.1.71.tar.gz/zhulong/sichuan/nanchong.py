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


_name_="nanchong"



def f1(driver, num):
    locator = (By.XPATH, "(//ul[@class='list-ul']/li[1]/a)[last()]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//td[@class='huifont']")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = re.findall(r'(\d+)/', st)[0]
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("(//ul[@class='list-ul']/li[1]/a)[last()]").get_attribute('href')[-35:]
        if "moreinfo.aspx?Paging" not in url:
            s = "moreinfo.aspx?Paging=%d" % (num) if num > 1 else "moreinfo.aspx?Paging=1"
            url = url + s
        elif num == 1:
            url = re.sub("Paging=[0-9]*", "Paging=1", url)
        else:
            s = "Paging=%d" % (num) if num > 1 else "Paging=1"
            url = re.sub("Paging=[0-9]*", s, url)
        driver.get(url)
        locator = (By.XPATH, "(//ul[@class='list-ul']/li[1]/a)[last()][not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("ul", class_="list-ul")
    trs = table.find_all("li", class_="list-li")
    data = []
    for tr in trs:
        try:
            a = tr.find_all("a")[-1]
        except:
            a = tr.find("a", class_="list-a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        link = "http://www.scncggzy.com.cn" + a['href'].strip()
        td = tr.find("span", class_='time').text.strip()
        tmp = [title, td, link]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df





def f2(driver):
    locator = (By.XPATH, "(//ul[@class='list-ul']/li[1]/a)[last()]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//td[@class='huifont']")
    str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'/(\d+)', str)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    html_page = driver.page_source
    if ("抱歉，系统发生了错误" in html_page) or ("出错啦！页面无法显示！" in html_page):
        return 404
    locator = (By.XPATH, "//table[@style=' border:#d1d1d1 1px solid;'][string-length()>30] | //table[@id='InfoDetail1_tblInfo'][string-length()>30]")
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
    div = soup.find('table', id='InfoDetail1_tblInfo')
    if div == None:
        div = soup.find('table', style=" border:#d1d1d1 1px solid;")
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.scncggzy.com.cn/TPFront/front_gcjs/072001/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_bian_bu_gg",
     "http://www.scncggzy.com.cn/TPFront/front_gcjs/072002/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.scncggzy.com.cn/TPFront/front_gcjs/072003/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiao_gg",
     "http://www.scncggzy.com.cn/TPFront/front_gcjs/072004/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_hetong_gg",
     "http://www.scncggzy.com.cn/TPFront/front_gcjs/072005/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhaobiao_quxian_gg",
     "http://www.scncggzy.com.cn/TPFront/front_gcjs/072006/072006001/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu': '区县'}), f2],

    ["gcjs_biangeng_quxian_gg",
     "http://www.scncggzy.com.cn/TPFront/front_gcjs/072006/072006002/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu': '区县'}), f2],

    ["gcjs_zhongbiao_quxian_gg",
     "http://www.scncggzy.com.cn/TPFront/front_gcjs/072006/072006004/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu': '区县'}), f2],

    ["gcjs_zgysjg_gg",
     "http://www.scncggzy.com.cn/TPFront/front_gcjs/072010/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_liu_zhongz_gg",
     "http://www.scncggzy.com.cn/TPFront/front_gcjs/072011/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://www.scncggzy.com.cn/TPFront/front_zfcg/071002/",
    ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_biangeng_gg",
     "http://www.scncggzy.com.cn/TPFront/front_zfcg/071003/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_zhong_liu_gg",
     "http://www.scncggzy.com.cn/TPFront/front_zfcg/071005/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_hetong_gg",
     "http://www.scncggzy.com.cn/TPFront/front_zfcg/071007/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_quxian_gg",
     "http://www.scncggzy.com.cn/TPFront/front_zfcg/071008/071008001/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu': '区县'}), f2],

    ["zfcg_biangeng_quxian_gg",
     "http://www.scncggzy.com.cn/TPFront/front_zfcg/071008/071008002/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu': '区县'}), f2],

    ["zfcg_zhongbiao_quxian_gg",
     "http://www.scncggzy.com.cn/TPFront/front_zfcg/071008/071008003/",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu': '区县'}), f2],

]



def work(conp,**args):
    est_meta(conp,data=data,diqu="四川省南充市",**args)
    est_html(conp,f=f3,**args)

# 修改时间：2019/6/27
if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","sichuan","nanchong"])


