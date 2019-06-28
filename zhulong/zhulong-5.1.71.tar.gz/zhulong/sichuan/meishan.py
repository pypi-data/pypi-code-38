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


_name_="meishan"

flag = 0

def f1_data(driver, num):
    locator = (By.XPATH, '//*[@id="DZJJZU_List2_DataGrid1_ctl02_sp_ProjectName"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, '//*[@id="DZJJZU_List2_Pager"]/div[1]/font[3]/b')
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = int(st)
    if num != int(cnum):
        val = driver.find_element_by_xpath('//*[@id="DZJJZU_List2_DataGrid1_ctl02_sp_ProjectName"]/a').get_attribute('onclick')[-30:]
        driver.execute_script("javascript:__doPostBack('DZJJZU_List2$Pager','{}')".format(num))
        locator = (By.XPATH, "//*[@id='DZJJZU_List2_DataGrid1_ctl02_sp_ProjectName']/a[not(contains(@onclick, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table", id='DZJJZU_List2_DataGrid1')
    trs = table.find_all("tr")
    data = []
    for tr in trs[1:]:
        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        if flag == 1:
            tdd = tr.find_all('td', align="center")[-1]
            if tdd.find('a'):
                onclick = tdd.find('a')['href']
                link = re.findall(r'\("(.*)"\)', onclick)[0].split('/',maxsplit=1)[1]
                link = "http://www.msggzy.org.cn/front/" + link.strip()
            else:
                continue
        else:
            onclick = a['onclick'].strip()
            link = re.findall(r'\("(.*)"\)', onclick)[0].split('/',maxsplit=1)[1]
            link = "http://www.msggzy.org.cn/front/" + link.strip()
        td = '-'
        td_1 = tr.find('td', align="right").text.strip()
        td_2 = tr.find_all('td', align="center")[1].text.strip()
        aa = {"ysje": td_1, "cjje": td_2}
        info = json.dumps(aa, ensure_ascii=False)
        tmp = [title, td, link, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f1(driver, num):
    url = driver.current_url
    if 'http://www.msggzy.org.cn/front/ShowInfo/DZJJ_More.aspx' in url:
        if 'bian' in url:
            driver.get(url.rsplit('/', maxsplit=1)[0])
        df = f1_data(driver, num)
        return df
    locator = (By.XPATH, "//table[@cellspacing='3']/tbody/tr[1]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//td[@class='huifont']")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = re.findall(r'(\d+)/', st)[0]
    url = driver.current_url
    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@cellspacing='3']/tbody/tr[1]/td/a").get_attribute('href')[-35:]
        if "Paging" not in url:
            s = "?Paging=%d" % (num) if num > 1 else "?Paging=1"
            url = url + s
        elif num == 1:
            url = re.sub("Paging=[0-9]*", "Paging=1", url)
        else:
            s = "Paging=%d" % (num) if num > 1 else "Paging=1"
            url = re.sub("Paging=[0-9]*", s, url)
        driver.get(url)
        locator = (By.XPATH, "//table[@cellspacing='3']/tbody/tr[1]/td/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table", cellspacing="3")
    trs = table.find_all("tr")
    data = []
    for tr in trs:
        a = tr.find('a')
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        link = "http://www.msggzy.org.cn" + a['href'].strip()
        td = tr.find("td", align="right").text.strip()
        tmp = [title, td, link]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df



def f2(driver):
    url = driver.current_url
    if 'http://www.msggzy.org.cn/front/ShowInfo/DZJJ_More.aspx' in url:
        global flag
        flag = 0
        if 'bian' in url:
            flag = 1
            driver.get(url.rsplit('/', maxsplit=1)[0])
        locator = (By.XPATH, '//*[@id="DZJJZU_List2_DataGrid1_ctl02_sp_ProjectName"]')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, '//*[@id="DZJJZU_List2_Pager"]/div[1]/font[2]/b')
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = int(st)
        driver.quit()
        return int(num)
    else:
        locator = (By.XPATH, "//table[@cellspacing='3']/tbody/tr[1]/td/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, "//td[@class='huifont']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = re.findall(r'/(\d+)', str)[0]
        driver.quit()
        return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//table[@id='tblInfo'][string-length()>15]")
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
    div = soup.find('table', id="tblInfo")
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.msggzy.org.cn/front/jsgc/001002/",
     ["name", "ggstart_time", "href", "info"],f1,f2],
    #
    ["gcjs_biangeng_gg",
     "http://www.msggzy.org.cn/front/jsgc/001010/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zsjg_gg",
     "http://www.msggzy.org.cn/front/jsgc/001016/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.msggzy.org.cn/front/jsgc/001013/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_gqita_zhonghxbiangeng_gg",
     "http://www.msggzy.org.cn/front/jsgc/001011/",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'gglx':'中标候选人公示变更'}), f2],

    ["gcjs_gqita_liu_zhongz_gg",
     "http://www.msggzy.org.cn/front/jsgc/001017/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://www.msggzy.org.cn/front/jsgc/001015/",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_kaibiao_gg",
     "http://www.msggzy.org.cn/front/jsgc/001018/",
     ["name", "ggstart_time", "href", "info"], f1, f2],
    # #
    ["zfcg_zhaobiao_gg",
     "http://www.msggzy.org.cn/front/zfcg/002001/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "http://www.msggzy.org.cn/front/zfcg/002002/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_zhong_liu_gg",
     "http://www.msggzy.org.cn/front/zfcg/002003/",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_wsjj_gg",
     "http://www.msggzy.org.cn/front/ShowInfo/DZJJ_More.aspx",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'网上竞价'}), f2],

    ["zfcg_biangeng_wsjj_gg",
     "http://www.msggzy.org.cn/front/ShowInfo/DZJJ_More.aspx/bian",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '网上竞价'}), f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="四川省眉山市",**args)
    est_html(conp,f=f3,**args)

# 修改时间：2019/6/27
if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","sichuan","meishan"])





