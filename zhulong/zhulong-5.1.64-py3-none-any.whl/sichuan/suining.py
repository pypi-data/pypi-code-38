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


_name_="suining"


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='right_new1']/ul/li[1]/a")
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-40:]
    gg_num = None
    if not val:
        gg_num = 1
        locator = (By.XPATH, "//div[@class='right_new1']/ul/li[1]/a")
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('title')
    try:
        locator = (By.XPATH, "//a[@class='one']")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(st)
    except:
        cnum = 1
    url = driver.current_url
    if num != int(cnum):
        locator = (By.XPATH, '//*[@id="txt_GoToPageIndex"]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).clear()
        locator = (By.XPATH, '//*[@id="txt_GoToPageIndex"]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).send_keys(num)
        locator = (By.XPATH, '//*[@id="mmgganue"]/a')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
        if gg_num != 1:
            locator = (By.XPATH, "//div[@class='right_new1']/ul/li[1]/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        else:
            locator = (By.XPATH, "//div[@class='right_new1']/ul/li[1]/a[not(contains(@title, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("div", class_="right_new1")
    trs = table.find_all("li")
    data = []
    for tr in trs:
        a = tr.find('a')
        try:
            title_1 = a['title'].strip()
        except:
            title_1 = a.text.strip()

        info = {}
        if re.findall(r'^\[(.*?)\]', title_1):
            diqu = re.findall(r'^\[(.*?)\]', title_1)[0]
            info['diqu'] = diqu
            title_1 = title_1.split(']', maxsplit=1)[1]
            if re.findall(r'^\[(.*?)\]', title_1):
                zblx = re.findall(r'^\[(.*?)\]', title_1)[0]
                info['zblx'] = zblx
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:
            info = None
        link = "http://jyzx.suining.gov.cn" + a['href'].strip()
        td = tr.find_all("span")[-1].text.strip()
        title = re.sub(r'\[(.*?)\]', '', title_1)
        tmp = [title, td, link, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='right_new1']/ul/li[1]/a/span[1]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "(//span[@class='dian'])[1]")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = re.findall(r'共 (\d+) 页', str)[0]
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='gsdt1'][string-length()>40]")
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
    div = soup.find('div', class_="gsdt1")
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://jyzx.suining.gov.cn/JyWeb/JYXX/Index?type=%u4EA4%u6613%u4FE1%u606F&subtype=210&subtype2=210010",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_bian_bu_gg",
     "http://jyzx.suining.gov.cn/JyWeb/JYXX/Index?type=%u4EA4%u6613%u4FE1%u606F&subtype=210&subtype2=210020",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zgysjg_gg",
     "http://jyzx.suining.gov.cn/JyWeb/JYXX/Index?type=%u4EA4%u6613%u4FE1%u606F&subtype=210&subtype2=210023",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://jyzx.suining.gov.cn/JyWeb/JYXX/Index?type=%u4EA4%u6613%u4FE1%u606F&subtype=210&subtype2=210025",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiao_gg",
     "http://jyzx.suining.gov.cn/JyWeb/JYXX/Index?type=%u4EA4%u6613%u4FE1%u606F&subtype=210&subtype2=210030",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_hetong_gg",
     "http://jyzx.suining.gov.cn/JyWeb/JYXX/Index?type=%u4EA4%u6613%u4FE1%u606F&subtype=210&subtype2=210040",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_liubiao_gg",
     "http://jyzx.suining.gov.cn/JyWeb/JYXX/Index?type=%u4EA4%u6613%u4FE1%u606F&subtype=210&subtype2=210050",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gg",
     "http://jyzx.suining.gov.cn/JyWeb/JYXX/Index?type=%u4EA4%u6613%u4FE1%u606F&subtype=220&subtype2=220010",
    ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_biangeng_gg",
     "http://jyzx.suining.gov.cn/JyWeb/JYXX/Index?type=%u4EA4%u6613%u4FE1%u606F&subtype=220&subtype2=220020",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_zhong_liu_gg",
     "http://jyzx.suining.gov.cn/JyWeb/JYXX/Index?type=%u4EA4%u6613%u4FE1%u606F&subtype=220&subtype2=220030",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_wsjj_gg",
     "http://jyzx.suining.gov.cn/JyWeb/wsjj/Index?type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&subtype=230&subtype2=230010",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'网上竞价'}), f2],

    ["zfcg_biangeng_wsjj_gg",
     "http://jyzx.suining.gov.cn/JyWeb/wsjj/Index?type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&subtype=230&subtype2=230020",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'网上竞价'}), f2],

    ["zfcg_zhongbiao_wsjj_gg",
     "http://jyzx.suining.gov.cn/JyWeb/wsjj/Index?type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&subtype=230&subtype2=230030",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'网上竞价'}), f2],

    ["zfcg_liubiao_wsjj_gg",
     "http://jyzx.suining.gov.cn/JyWeb/wsjj/Index?type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&subtype=230&subtype2=230040",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'网上竞价'}), f2],

    ["zfcg_gqita_jieguobuchong_wsjj_gg",
     "http://jyzx.suining.gov.cn/JyWeb/wsjj/Index?type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&subtype=230&subtype2=230050",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'网上竞价','gglx':'结果补充公告'}), f2],

    ["qsy_gqita_zhao_zhong_gg",
     "http://jyzx.suining.gov.cn/JyWeb/JYXX/Index?type=%u4EA4%u6613%u4FE1%u606F&subtype=255&subtype2=255010",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'其他交易'}), f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="四川省遂宁市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","sichuan","suining"])


