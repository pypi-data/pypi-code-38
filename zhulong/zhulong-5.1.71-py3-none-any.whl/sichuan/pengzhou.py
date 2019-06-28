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


_name_="pengzhou"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='main_con']/table/tbody/tr[1]/td/a")
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-30:]
    locator = (By.XPATH, "//td[@class='page_bar']")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = re.findall(r'(\d+)/', st)[0]
    url = driver.current_url
    if num != int(cnum):
        driver.find_element_by_xpath('//input[@id="txtAjax_PageIndex"]').clear()
        driver.find_element_by_xpath('//input[@id="txtAjax_PageIndex"]').send_keys(num, Keys.ENTER)
        locator = (By.XPATH, "//div[@class='main_con']/table/tbody/tr[1]/td/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("div", class_="main_con")
    trs = table.find_all("tr", class_='ListTableOddRow')
    data = []
    for tr in trs:
        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        try:
            href = a['href'].strip()
            if "http" in href:
                link = href
            else:
                link = "http://fwpt.pzggzy.com" + href
        except:
            link = '-'
        try:
            span = tr.find("td", style="width: 12%; text-align: center;").text.strip()
        except:
            span = '-'
        try:
            td = tr.find('td', style="width: 20%; color: #4a4847").text.strip()
            a={"yuanyin":td}
            a=json.dumps(a,ensure_ascii=False)
            info=a
        except:
            info = None
        tmp = [title, span, link, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='main_con']/table/tbody/tr[1]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, "//td[@class='page_bar']")
    str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'/(\d+)', str)[0]
    driver.quit()
    return int(num)



def f3(driver, url):

    driver.get(url)
    html = driver.page_source
    if ("您请求的文件不存在" in html) or ("找不到文件" in html) or ("Not Found" in html):
        return 404
    locator = (By.XPATH, "//div[@class='big_wrap'][string-length()>30] | //div[@class='cont-info'][string-length()>40] | //div[@id='myPrintArea'][string-length()>40]")
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
    div = soup.find('div', class_='big_wrap')
    if div == None:
        div = soup.find('div', class_='cont-info')
        if div == None:
            div = soup.find('div', id="myPrintArea")
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://fwpt.pzggzy.com/JyWeb/XXGK/JYXTXXFBList?SubType=1&SubType2=1010&Type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiaohx_gg",
     "http://fwpt.pzggzy.com/JyWeb/XXGK/JYXTXXFBList?SubType=1&SubType2=1025&Type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://fwpt.pzggzy.com/JyWeb/XXGK/JYXTXXFBList?SubType=1&SubType2=1030&Type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_liubiao_gg",
     "http://fwpt.pzggzy.com/JyWeb/XXGK/JYXTCXZBXMList?SubType=1&SubType2=1050&Type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhaobiao_gg",
     "http://fwpt.pzggzy.com/JyWeb/XXGK/JYXYZFCGXXFBList?SubType=2&SubType2=2020&Type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiaohx_gg",
     "http://fwpt.pzggzy.com/JyWeb/XXGK/JYXYZFCGXXFBList?SubType=2&SubType2=2025&Type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://fwpt.pzggzy.com/JyWeb/XXGK/JYXYZFCGXXFBList?SubType=2&SubType2=2030&Type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_hetong_gg",
     "http://fwpt.pzggzy.com/JyWeb/XXGK/JYXYZFCGXXFBList?SubType=2&SubType2=2040&Type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "http://fwpt.pzggzy.com/JyWeb/XXGK/JYXYZFCGXXFBList?SubType=2&SubType2=2050&Type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_liubiao_gg",
     "http://fwpt.pzggzy.com/JyWeb/XXGK/JYXTCXZBXMList?SubType=2&SubType2=2080&Type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qsy_zhaobiao_gg",
     "http://fwpt.pzggzy.com/JyWeb/XXGK/JYXTXXFBList?SubType=5&SubType2=5010&Type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'jylx':'其它交易'}), f2],

    ["qsy_gqita_bian_bu_gg",
     "http://fwpt.pzggzy.com/JyWeb/XXGK/JYXTXXFBList?SubType=5&SubType2=5020&Type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'其它交易'}), f2],

    ["qsy_gqita_zhong_liu_gg",
     "http://fwpt.pzggzy.com/JyWeb/XXGK/JYXTXXFBList?SubType=5&SubType2=5030&Type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'jylx':'其它交易'}), f2],

]



def work(conp,**args):
    est_meta(conp,data=data,diqu="四川省彭州市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","sichuan","pengzhou"])


