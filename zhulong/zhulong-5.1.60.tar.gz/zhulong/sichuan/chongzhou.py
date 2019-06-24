import json
import time
import pandas as pd
import re
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from zhulong.util.etl import add_info,est_meta,est_html,est_tbs


_name_="chongzhou"



str_gl = None
num_gl = None

#
def click_link_1(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, '//div[@data-id="displaytype"]/div[2]/div[@class="option choosed"]')
        val_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if f == f2:
            global str_gl,num_gl
            str_gl = None
            locator = (By.XPATH, '//div[@id="contentlist"]//div[1]/div/a')
            str_gl = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            num_gl = None
            locator = (By.XPATH, '//span[@id="LabelPage"]')
            str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            num_gl = re.findall(r'/(\d+)', str)[0]
        # 获取需要点击的链接的文本
        locator = (By.XPATH, '//*[@id="condition"]/div[1]/div[2]/div[2]')
        val_2 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if val_1 not in val_2:
            # 点击
            locator = (By.XPATH, '//*[@id="condition"]/div[1]/div[2]/div[2]')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            try:
                locator = (By.XPATH, '//div[@id="contentlist"]//div[1]/div/a[not(contains(string(), "%s"))]' % str_gl)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            except:
                time.sleep(1)
            locator = (By.XPATH, '//span[@id="LabelPage"][not(contains(string(), "%s"))]' % num_gl)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*krg)
    return wrap

def click_link_2(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, '//div[@data-id="displaytype"]/div[2]/div[@class="option choosed"]')
        val_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if f == f2:
            global str_gl, num_gl
            str_gl = None
            locator = (By.XPATH, '//div[@id="contentlist"]//div[1]/div/a')
            str_gl = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            num_gl = None
            locator = (By.XPATH, '//span[@id="LabelPage"]')
            str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            num_gl = re.findall(r'/(\d+)', str)[0]
        # 获取需要点击的链接的文本
        locator = (By.XPATH, '//*[@id="condition"]/div[1]/div[2]/div[3]')
        val_2 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if val_1 not in val_2:
            # 点击
            locator = (By.XPATH, '//*[@id="condition"]/div[1]/div[2]/div[3]')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            try:
                locator = (By.XPATH, '//div[@id="contentlist"]//div[1]/div/a[not(contains(string(), "%s"))]' % str_gl)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            except:
                time.sleep(1)
            locator = (By.XPATH, '//span[@id="LabelPage"][not(contains(string(), "%s"))]' % num_gl)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*krg)
    return wrap

def click_link_3(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, '//div[@data-id="displaytype"]/div[2]/div[@class="option choosed"]')
        val_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if f == f2:
            global str_gl, num_gl
            str_gl = None
            locator = (By.XPATH, '//div[@id="contentlist"]//div[1]/div/a')
            str_gl = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            num_gl = None
            locator = (By.XPATH, '//span[@id="LabelPage"]')
            str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            num_gl = re.findall(r'/(\d+)', str)[0]
        # 获取需要点击的链接的文本
        locator = (By.XPATH, '//*[@id="condition"]/div[1]/div[2]/div[4]')
        val_2 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if val_1 not in val_2:
            # 点击
            locator = (By.XPATH, '//*[@id="condition"]/div[1]/div[2]/div[4]')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            try:
                locator = (By.XPATH, '//div[@id="contentlist"]//div[1]/div/a[not(contains(string(), "%s"))]' % str_gl)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            except:
                time.sleep(1)
            locator = (By.XPATH, '//span[@id="LabelPage"][not(contains(string(), "%s"))]' % num_gl)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*krg)
    return wrap

def click_link_4(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, '//div[@data-id="displaytype"]/div[2]/div[@class="option choosed"]')
        val_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if f == f2:
            global str_gl, num_gl
            str_gl = None
            locator = (By.XPATH, '//div[@id="contentlist"]//div[1]/div/a')
            str_gl = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            num_gl = None
            locator = (By.XPATH, '//span[@id="LabelPage"]')
            str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            num_gl = re.findall(r'/(\d+)', str)[0]
        # 获取需要点击的链接的文本
        locator = (By.XPATH, '//*[@id="condition"]/div[1]/div[2]/div[5]')
        val_2 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if val_1 not in val_2:
            # 点击
            locator = (By.XPATH, '//*[@id="condition"]/div[1]/div[2]/div[5]')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            try:
                locator = (By.XPATH, '//div[@id="contentlist"]//div[1]/div/a[not(contains(string(), "%s"))]' % str_gl)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            except:
                time.sleep(1)
            locator = (By.XPATH, '//span[@id="LabelPage"][not(contains(string(), "%s"))]' % num_gl)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*krg)
    return wrap

def click_link_5(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, '//div[@data-id="displaytype"]/div[2]/div[@class="option choosed"]')
        val_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if f == f2:
            global str_gl, num_gl
            str_gl = None
            locator = (By.XPATH, '//div[@id="contentlist"]//div[1]/div/a')
            str_gl = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            num_gl = None
            locator = (By.XPATH, '//span[@id="LabelPage"]')
            str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            num_gl = re.findall(r'/(\d+)', str)[0]
        # 获取需要点击的链接的文本
        locator = (By.XPATH, '//*[@id="condition"]/div[1]/div[2]/div[6]')
        val_2 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if val_1 not in val_2:
            # 点击
            locator = (By.XPATH, '//*[@id="condition"]/div[1]/div[2]/div[6]')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            try:
                locator = (By.XPATH, '//div[@id="contentlist"]//div[1]/div/a[not(contains(string(), "%s"))]' % str_gl)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            except:
                time.sleep(1)
            locator = (By.XPATH, '//span[@id="LabelPage"][not(contains(string(), "%s"))]' % num_gl)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*krg)
    return wrap

def click_link_6(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, '//div[@data-id="displaytype"]/div[2]/div[@class="option choosed"]')
        val_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if f == f2:
            global str_gl, num_gl
            str_gl = None
            locator = (By.XPATH, '//div[@id="contentlist"]//div[1]/div/a')
            str_gl = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            num_gl = None
            locator = (By.XPATH, '//span[@id="LabelPage"]')
            str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            num_gl = re.findall(r'/(\d+)', str)[0]
        # 获取需要点击的链接的文本
        locator = (By.XPATH, '//*[@id="condition"]/div[1]/div[2]/div[7]')
        val_2 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if val_1 not in val_2:
            # 点击
            locator = (By.XPATH, '//*[@id="condition"]/div[1]/div[2]/div[7]')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            try:
                locator = (By.XPATH, '//div[@id="contentlist"]//div[1]/div/a[not(contains(string(), "%s"))]' % str_gl)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            except:
                time.sleep(1)
            locator = (By.XPATH, '//span[@id="LabelPage"][not(contains(string(), "%s"))]' % num_gl)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*krg)
    return wrap

#
def click_gglx_1(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, '//*[@id="statechoose"]/div[2]/div[@class="option choosed"]')
        val_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if f == f2:
            global str_gl, num_gl
            str_gl = None
            locator = (By.XPATH, '//div[@id="contentlist"]//div[1]/div/a')
            str_gl = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            num_gl = None
            locator = (By.XPATH, '//span[@id="LabelPage"]')
            str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            num_gl = re.findall(r'/(\d+)', str)[0]
        # 获取需要点击的链接的文本
        locator = (By.XPATH, '//*[@id="statechoose"]/div[2]/div[2]')
        val_2 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if val_1 not in val_2:
            # 点击
            locator = (By.XPATH, '//*[@id="statechoose"]/div[2]/div[2]')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            try:
                locator = (By.XPATH, '//div[@id="contentlist"]//div[1]/div/a[not(contains(string(), "%s"))]' % str_gl)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            except:
                time.sleep(1)
            try:
                locator = (By.XPATH, '//span[@id="LabelPage"][not(contains(string(), "%s"))]' % num_gl)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            except:
                time.sleep(1)
        return f(*krg)
    return wrap

def click_gglx_2(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, '//*[@id="statechoose"]/div[2]/div[@class="option choosed"]')
        val_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if f == f2:
            global str_gl, num_gl
            str_gl = None
            locator = (By.XPATH, '//div[@id="contentlist"]//div[1]/div/a')
            str_gl = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            num_gl = None
            locator = (By.XPATH, '//span[@id="LabelPage"]')
            str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            num_gl = re.findall(r'/(\d+)', str)[0]
        # 获取需要点击的链接的文本
        locator = (By.XPATH, '//*[@id="statechoose"]/div[2]/div[3]')
        val_2 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        if val_1 not in val_2:
            # 点击
            locator = (By.XPATH, '//*[@id="statechoose"]/div[2]/div[3]')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            try:
                locator = (By.XPATH, '//div[@id="contentlist"]//div[1]/div/a[not(contains(string(), "%s"))]' % str_gl)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            except:
                time.sleep(1)
            try:
                locator = (By.XPATH, '//span[@id="LabelPage"][not(contains(string(), "%s"))]' % num_gl)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            except:
                time.sleep(1)
        return f(*krg)
    return wrap




def f1(driver, num):
    locator = (By.XPATH, '//div[@id="contentlist"]//div[1]/div/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//span[@class='active']")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
        cnum = st.strip()
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath('//div[@id="contentlist"]//div[1]/div/a').get_attribute('href')[-30:]
        driver.execute_script("javascript:__doPostBack('ctl00$ContentPlaceHolder1$Pager','{}')".format(num))
        locator = (By.XPATH, '//div[@id="contentlist"]//div[1]/div/a[not(contains(@href, "%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    tbody = soup.find("div", id="contentlist")
    trs = tbody.find_all("div", class_="row contentitem")
    data = []
    for tr in trs:
        a = tr.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        href = a['href'].strip()
        if "http" in href:
            link = href
        else:
            if href.startswith(('./', '/')):
                href = href.split('/', maxsplit=1)[1]
            u = url.rsplit('/', maxsplit=1)[0]
            link = u + '/' + href
        td = tr.find("div", class_='publishtime').text.strip()
        try:
            dq = tr.find('div', class_='col-xs-1').text.strip()
            if '【' in dq:
                dq = re.findall(r'【(.*)】', dq)[0]
        except:
            dq = ''
        info = json.dumps({'diqu': dq}, ensure_ascii=False)
        tmp = [title, td, link, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f2(driver):
    locator = (By.XPATH, '//*[@id="LabelPage"]')
    str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    num = re.findall(r'/(\d+)', str)[0]
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    if '<iframe id="ifrList"' in driver.page_source:
        driver.switch_to_frame('ifrList')
    try:
        flag = 1
        locator = (By.XPATH, "//div[@id='noticecontent'][string-length()>40] | //div[@class='middle clear'][string-length()>40] | //div[@class='bg'][string-length()>40]")
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    except:
        flag = 2
        locator = (By.XPATH, "//tr[@style='padding-left: 20px;'][string-length()>40]")
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
    if flag == 1:
        div = soup.find('div', id="noticecontent")
        if div == None:
            div = soup.find('div', class_="middle clear")
            if div == None:
                div = soup.find('div', class_="bg")
    elif flag == 2:
        div = soup.find('tr', style='padding-left: 20px;')
    return div


data = [
    ["gcjs_zhaobiao_gg", "https://www.cdggzy.com/chongzhou/site/JSGC/List.aspx",
     ["name", "ggstart_time", "href", "info"], click_link_1(f1), click_link_1(f2)],

    ["gcjs_zhongbiaohx_lx1_gg", "https://www.cdggzy.com/chongzhou/site/JSGC/List.aspx",
     ["name", "ggstart_time", "href", "info"], click_link_2(add_info(f1, {'gglx':'结果公布'})), click_link_2(f2)],

    ["gcjs_biangeng_gg", "https://www.cdggzy.com/chongzhou/site/JSGC/List.aspx",
     ["name", "ggstart_time", "href", "info"], click_link_3(f1), click_link_3(f2)],

    ["gcjs_zhongbiaohx_lx2_gg", "https://www.cdggzy.com/chongzhou/site/JSGC/List.aspx",
     ["name", "ggstart_time", "href", "info"], click_link_4(add_info(f1, {'gglx':'评标结果公示'})), click_link_4(f2)],

    ["gcjs_hetong_gg", "https://www.cdggzy.com/chongzhou/site/JSGC/List.aspx",
     ["name", "ggstart_time", "href", "info"], click_link_5(f1), click_link_5(f2)],

    ["gcjs_gqita_liu_zhongz_gg", "https://www.cdggzy.com/chongzhou/site/JSGC/List.aspx",
     ["name", "ggstart_time", "href", "info"], click_link_6(f1), click_link_6(f2)],

    ["zfcg_zhaobiao_gg", "https://www.cdggzy.com/chongzhou/site/Notice/ZFCG/NoticeList.aspx",
     ["name", "ggstart_time", "href", "info"], click_link_1(f1), click_link_1(f2)],

    ["zfcg_biangeng_gg", "https://www.cdggzy.com/chongzhou/site/Notice/ZFCG/NoticeList.aspx",
     ["name", "ggstart_time", "href", "info"], click_link_2(f1), click_link_2(f2)],

    ["zfcg_gqita_zhong_liu_gg", "https://www.cdggzy.com/chongzhou/site/Notice/ZFCG/NoticeList.aspx",
     ["name", "ggstart_time", "href", "info"], click_link_3(f1), click_link_3(f2)],

    ["zfcg_zhaobiao_wsjj_gg", "https://www.cdggzy.com/chongzhou/site/Notice/WSJJ/NoticeList.aspx",
     ["name", "ggstart_time", "href", "info"], click_link_1(add_info(f1, {'zbfs':'网上竞价'})), click_link_1(f2)],

    ["zfcg_zhongbiao_wsjj_gg", "https://www.cdggzy.com/chongzhou/site/Notice/WSJJ/NoticeList.aspx",
     ["name", "ggstart_time", "href", "info"], click_link_2(add_info(f1, {'zbfs':'网上竞价'})), click_link_2(f2)],

    ["zfcg_liubiao_wsjj_gg", "https://www.cdggzy.com/chongzhou/site/Notice/WSJJ/NoticeList.aspx",
     ["name", "ggstart_time", "href", "info"], click_link_3(add_info(f1, {'zbfs':'网上竞价'})), click_link_3(f2)],

    ["zfcg_gqita_jieguobiangeng_wsjj_gg", "https://www.cdggzy.com/chongzhou/site/Notice/WSJJ/NoticeList.aspx",
     ["name", "ggstart_time", "href", "info"], click_link_4(add_info(f1, {'zbfs':'网上竞价','gglx':'结果变更公告'})), click_link_4(f2)],
    #
    ["zfcg_zhaobiao_ddcg_gg", "https://www.cdggzy.com/chongzhou/site/Notice/DDCG/NoticeList.aspx",
     ["name", "ggstart_time", "href", "info"], click_link_1(add_info(f1, {'zbfs':'定点采购'})), click_link_1(f2)],

    ["zfcg_zhongbiao_ddcg_gg", "https://www.cdggzy.com/chongzhou/site/Notice/DDCG/NoticeList.aspx",
     ["name", "ggstart_time", "href", "info"], click_link_2(add_info(f1, {'zbfs':'定点采购'})), click_link_2(f2)],

    ["zfcg_liubiao_ddcg_gg", "https://www.cdggzy.com/chongzhou/site/Notice/DDCG/NoticeList.aspx",
     ["name", "ggstart_time", "href", "info"], click_link_3(add_info(f1, {'zbfs':'定点采购'})), click_link_3(f2)],
]



def work(conp,**args):
    est_meta(conp,data=data,diqu="四川省崇州市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","sichuan","chongzhou"])


