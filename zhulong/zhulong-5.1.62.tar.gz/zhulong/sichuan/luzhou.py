import ast
import pandas as pd
import re
import requests
from zhulong.util.fake_useragent import UserAgent
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


_name_="luzhou"

def zbgg_click(f):
    def warp(*kwargs):
        driver = kwargs[0]
        try:
            val_1 = driver.find_element_by_xpath("//span[@id='noticeWrap1']/a").text.strip()
        except:
            val_1 = ''
        if val_1 != '招标公告':
            locator = (By.XPATH, "//div[@id='typeBulletin1']//a[contains(text(), '招标公告')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            locator = (By.XPATH, "//span[@id='noticeWrap1']/a[contains(text(), '招标公告')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*kwargs)
    return warp

def bygg_click(f):
    def warp(*kwargs):
        driver = kwargs[0]
        try:
            val_1 = driver.find_element_by_xpath("//span[@id='noticeWrap1']/a").text.strip()
        except:
            val_1 = ''
        if val_1 != '补遗/澄清':
            locator = (By.XPATH, "//div[@id='typeBulletin1']//a[contains(text(), '补遗/澄清')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            locator = (By.XPATH, "//span[@id='noticeWrap1']/a[contains(text(), '补遗/澄清')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*kwargs)
    return warp

def kbgg_click(f):
    def warp(*kwargs):
        driver = kwargs[0]
        try:
            val_1 = driver.find_element_by_xpath("//span[@id='noticeWrap1']/a").text.strip()
        except:
            val_1 = ''
        if val_1 != '开标记录':
            locator = (By.XPATH, "//div[@id='typeBulletin1']//a[contains(text(), '开标记录')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            locator = (By.XPATH, "//span[@id='noticeWrap1']/a[contains(text(), '开标记录')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*kwargs)
    return warp

def lbgg_click(f):
    def warp(*kwargs):
        driver = kwargs[0]
        try:
            val_1 = driver.find_element_by_xpath("//span[@id='noticeWrap1']/a").text.strip()
        except:
            val_1 = ''
        if val_1 != '流标或终止公告':
            locator = (By.XPATH, "//div[@id='typeBulletin1']//a[contains(text(), '流标或终止公告')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            locator = (By.XPATH, "//span[@id='noticeWrap1']/a[contains(text(), '流标或终止公告')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*kwargs)
    return warp

def pbgg_click(f):
    def warp(*kwargs):
        driver = kwargs[0]
        try:
            val_1 = driver.find_element_by_xpath("//span[@id='noticeWrap1']/a").text.strip()
        except:
            val_1 = ''
        if val_1 != '评标结果公示':
            locator = (By.XPATH, "//div[@id='typeBulletin1']//a[contains(text(), '评标结果公示')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            locator = (By.XPATH, "//span[@id='noticeWrap1']/a[contains(text(), '评标结果公示')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*kwargs)
    return warp

def zhbgg_click(f):
    def warp(*kwargs):
        driver = kwargs[0]
        try:
            val_1 = driver.find_element_by_xpath("//span[@id='noticeWrap1']/a").text.strip()
        except:
            val_1 = ''
        if val_1 != '中标结果公告':
            locator = (By.XPATH, "//div[@id='typeBulletin1']//a[contains(text(), '中标结果公告')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            locator = (By.XPATH, "//span[@id='noticeWrap1']/a[contains(text(), '中标结果公告')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*kwargs)
    return warp

def htgs_click(f):
    def warp(*kwargs):
        driver = kwargs[0]
        try:
            val_1 = driver.find_element_by_xpath("//span[@id='noticeWrap1']/a").text.strip()
        except:
            val_1 = ''
        if val_1 != '合同公示':
            locator = (By.XPATH, "//div[@id='typeBulletin1']//a[contains(text(), '合同公示')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            locator = (By.XPATH, "//span[@id='noticeWrap1']/a[contains(text(), '合同公示')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*kwargs)
    return warp

def zjlgg_click(f):
    def warp(*kwargs):
        driver = kwargs[0]
        try:
            val_1 = driver.find_element_by_xpath("//span[@id='noticeWrap1']/a").text.strip()
        except:
            val_1 = ''
        if val_1 != '增加工程量':
            locator = (By.XPATH, "//div[@id='typeBulletin1']//a[contains(text(), '增加工程量')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            locator = (By.XPATH, "//span[@id='noticeWrap1']/a[contains(text(), '增加工程量')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*kwargs)
    return warp

def cggg_click(f):
    def warp(*kwargs):
        driver = kwargs[0]
        try:
            val_1 = driver.find_element_by_xpath("//span[@id='noticeWrap1']/a").text.strip()
        except:
            val_1 = ''
        if val_1 != '采购公告':
            locator = (By.XPATH, "//div[@id='typeBulletin1']//a[contains(text(), '采购公告')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            locator = (By.XPATH, "//span[@id='noticeWrap1']/a[contains(text(), '采购公告')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*kwargs)
    return warp

def bggg_click(f):
    def warp(*kwargs):
        driver = kwargs[0]
        try:
            val_1 = driver.find_element_by_xpath("//span[@id='noticeWrap1']/a").text.strip()
        except:
            val_1 = ''
        if val_1 != '变更公告':
            locator = (By.XPATH, "//div[@id='typeBulletin1']//a[contains(text(), '变更公告')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            locator = (By.XPATH, "//span[@id='noticeWrap1']/a[contains(text(), '变更公告')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*kwargs)
    return warp

def jggg_click(f):
    def warp(*kwargs):
        driver = kwargs[0]
        try:
            val_1 = driver.find_element_by_xpath("//span[@id='noticeWrap1']/a").text.strip()
        except:
            val_1 = ''
        if val_1 != '结果公告':
            locator = (By.XPATH, "//div[@id='typeBulletin1']//a[contains(text(), '结果公告')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            locator = (By.XPATH, "//span[@id='noticeWrap1']/a[contains(text(), '结果公告')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*kwargs)
    return warp

def htgg_click(f):
    def warp(*kwargs):
        driver = kwargs[0]
        try:
            val_1 = driver.find_element_by_xpath("//span[@id='noticeWrap1']/a").text.strip()
        except:
            val_1 = ''
        if val_1 != '合同公告':
            locator = (By.XPATH, "//div[@id='typeBulletin1']//a[contains(text(), '合同公告')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            locator = (By.XPATH, "//span[@id='noticeWrap1']/a[contains(text(), '合同公告')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*kwargs)
    return warp

def ysygg_click(f):
    def warp(*kwargs):
        driver = kwargs[0]
        try:
            val_1 = driver.find_element_by_xpath("//span[@id='noticeWrap1']/a").text.strip()
        except:
            val_1 = ''
        if val_1 != '验收预公告':
            locator = (By.XPATH, "//div[@id='typeBulletin1']//a[contains(text(), '验收预公告')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            locator = (By.XPATH, "//span[@id='noticeWrap1']/a[contains(text(), '验收预公告')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*kwargs)
    return warp

def ysgg_click(f):
    def warp(*kwargs):
        driver = kwargs[0]
        try:
            val_1 = driver.find_element_by_xpath("//span[@id='noticeWrap1']/a").text.strip()
        except:
            val_1 = ''
        if val_1 != '验收记录公示':
            locator = (By.XPATH, "//div[@id='typeBulletin1']//a[contains(text(), '验收记录公示')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            locator = (By.XPATH, "//span[@id='noticeWrap1']/a[contains(text(), '验收记录公示')]")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        return f(*kwargs)
    return warp


def f1_data(driver, num):
    locator = (By.XPATH, "//ul[@class='ewb-notice-items']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//li[@class='active']/a")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        cnum = 1

    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='ewb-notice-items']/li[1]/a").get_attribute('href')[-30:]
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@id='page']//input"))).click()
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[@id='page']//input"))).send_keys('%s' % num,Keys.ENTER)
        locator = (By.XPATH, "//ul[@class='ewb-notice-items']/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    ul = soup.find("ul", id="jingtai")
    lis = ul.find_all("li")
    data = []
    for li in lis:
        a = li.find('a')
        href = 'http://ggzy.luzhou.gov.cn' + a['href'].strip()
        span = li.find('span', class_='r ewb-notice-time').text.strip()
        try:
            font = a.find_all('font')
            if int(len(font)) > 1:
                diqu = a.find_all('font')[0].extract().text.strip()
                diqu = re.findall(r'\[(.*)\]', diqu)[0]
                xmlx = a.find_all('font')[0].extract().text.strip()
                xmlx = re.findall(r'\[(.*)\]', xmlx)[0]
                info = {'diqu': diqu, 'xmlx': xmlx}
            else:
                diqu = a.find_all('font')[0].extract().text.strip()
                diqu = re.findall(r'\[(.*)\]', diqu)[0]
                info = {'diqu': diqu}
        except:
            info = {}
        try:
            title = a['title']
        except:
            title = a.text.strip()
        if re.findall(r'^\[(.*?)\]', title):
            gglx = re.findall(r'^\[(.*?)\]', title)[0]
            if '公告' in gglx:
                info['gglx'] = gglx
            else:
                info['lx'] = gglx
        elif re.findall(r'^\【(.*?)\】', title):
            gglx = re.findall(r'^\【(.*?)\】', title)[0]
            if '公告' in gglx:
                info['gglx'] = gglx
            else:
                info['lx'] = gglx
        info = json.dumps(info, ensure_ascii=False)
        tmp = [title, span, href, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df

def f1(driver, num):
    url = driver.current_url
    if ('/qtjy/016001/' in url) or ('/qtjy/016003/' in url) or ('/zfcg/005003/' in url):
        df = f1_data(driver, num)
        return df
    locator = (By.XPATH, "//ul[@id='showlist']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@id='pager']/ul/li[@class='active']/a")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        cnum = 1

    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@id='showlist']/li[1]/a").get_attribute('href')[-30:]
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH,"//div[@id='moreinfoAjax']//input"))).click()
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='moreinfoAjax']//input"))).send_keys('%s' % num, Keys.ENTER)
        locator = (By.XPATH, "//ul[@id='showlist']/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    ul = soup.find("ul", id="showlist")
    lis = ul.find_all("li")
    data = []
    for li in lis:
        a = li.find('a')
        href = 'http://ggzy.luzhou.gov.cn' + a['href'].strip()
        span = li.find('span', class_='r ewb-notice-time').text.strip()
        try:
            font = a.find_all('font')
            if int(len(font)) > 1:
                diqu = a.find_all('font')[0].extract().text.strip()
                diqu = re.findall(r'\[(.*)\]', diqu)[0]
                xmlx = a.find_all('font')[0].extract().text.strip()
                xmlx = re.findall(r'\[(.*)\]', xmlx)[0]
                if '招标' in xmlx:
                    info = {'diqu': diqu, 'zblx': xmlx}
                else:
                    info = {'diqu': diqu, 'xmlx': xmlx}
            else:
                diqu = a.find_all('font')[0].extract().text.strip()
                diqu = re.findall(r'\[(.*)\]', diqu)[0]
                info = {'diqu': diqu}
        except:
            info = {}
        try:
            title = a['title']
        except:
            title = a.text.strip()
        if re.findall(r'^\[(.*?)\]', title):
            gglx = re.findall(r'^\[(.*?)\]', title)[0]
            if '公告' in gglx:
                info['gglx'] = gglx
            elif '四川省' in gglx:
                info['diqu'] = gglx
            else:
                info['lx'] = gglx
        elif re.findall(r'^\【(.*?)\】', title):
            gglx = re.findall(r'^\【(.*?)\】', title)[0]
            if '公告' in gglx:
                info['gglx'] = gglx
            elif '四川省' in gglx:
                info['diqu'] = gglx
            else:
                info['lx'] = gglx
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:
            info = None
        tmp = [title, span, href, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df



def f2(driver):
    url = driver.current_url
    if ('/qtjy/016001/' in url) or ('/qtjy/016003/' in url) or ('/zfcg/005003/' in url):
        locator = (By.XPATH, "//ul[@class='ewb-notice-items']/li[1]/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, "//div[@id='page']/ul/li[last()]/a")
            num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        except:
            num = 1
        driver.quit()
        return int(num)

    locator = (By.XPATH, "//ul[@id='showlist']/li[1]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//div[@id='pager']/ul/li[last()]/a")
        num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        num = 1
    driver.quit()
    return int(num)



def f3(driver, url):
    driver.get(url)
    if '404' in driver.title:
        return 404
    locator = (By.XPATH, "//div[@class='ewb-results-info'][string-length()>30] | //div[@class='news-detail-wrap'][string-length()>30]")
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
    div = soup.find('div', class_="ewb-results-info")
    if div == None:
        div = soup.find('div', class_="news-detail-wrap")
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://ggzy.luzhou.gov.cn/gcjs/004001/projectBuild.html",
     ["name", "ggstart_time", "href", "info"], zbgg_click(f1),zbgg_click(f2)],

    ["gcjs_gqita_bian_bu_gg",
     "http://ggzy.luzhou.gov.cn/gcjs/004001/projectBuild.html",
     ["name", "ggstart_time", "href", "info"], bygg_click(f1), bygg_click(f2)],

    ["gcjs_zsjg_gg",
     "http://ggzy.luzhou.gov.cn/gcjs/004001/projectBuild.html",
     ["name", "ggstart_time", "href", "info"], kbgg_click(f1),kbgg_click(f2)],

    ["gcjs_gqita_liu_zhongz_gg",
     "http://ggzy.luzhou.gov.cn/gcjs/004001/projectBuild.html",
     ["name", "ggstart_time", "href", "info"], lbgg_click(f1),lbgg_click(f2)],

    ["gcjs_zhongbiaohx_gg",
     "http://ggzy.luzhou.gov.cn/gcjs/004001/projectBuild.html",
     ["name", "ggstart_time", "href", "info"], pbgg_click(f1), pbgg_click(f2)],

    ["gcjs_zhongbiao_gg",
     "http://ggzy.luzhou.gov.cn/gcjs/004001/projectBuild.html",
     ["name", "ggstart_time", "href", "info"], zhbgg_click(f1), zhbgg_click(f2)],

    ["gcjs_gqita_hetong_gg",
     "http://ggzy.luzhou.gov.cn/gcjs/004001/projectBuild.html",
     ["name", "ggstart_time", "href", "info"], htgs_click(f1), htgs_click(f2)],

    ["gcjs_gqita_zjgcl_gg",
     "http://ggzy.luzhou.gov.cn/gcjs/004001/projectBuild.html",
     ["name", "ggstart_time", "href", "info"], zjlgg_click(add_info(f1,{'gglx2':'增加工程量'})), zjlgg_click(f2)],

    ["zfcg_zhaobiao_gg",
     "http://ggzy.luzhou.gov.cn/zfcg/005001/projectBuild_zfcg.html",
    ["name", "ggstart_time", "href", "info"], cggg_click(f1),cggg_click(f2)],

    ["zfcg_biangeng_gg",
     "http://ggzy.luzhou.gov.cn/zfcg/005001/projectBuild_zfcg.html",
     ["name", "ggstart_time", "href", "info"], bggg_click(f1), bggg_click(f2)],

    ["zfcg_zhongbiao_gg",
     "http://ggzy.luzhou.gov.cn/zfcg/005001/projectBuild_zfcg.html",
     ["name", "ggstart_time", "href", "info"], jggg_click(f1), jggg_click(f2)],

    ["zfcg_gqita_hetong_gg",
     "http://ggzy.luzhou.gov.cn/zfcg/005001/projectBuild_zfcg.html",
     ["name", "ggstart_time", "href", "info"], htgg_click(f1), htgg_click(f2)],

    ["zfcg_gqita_yuyanshou_gg",
     "http://ggzy.luzhou.gov.cn/zfcg/005001/projectBuild_zfcg.html",
     ["name", "ggstart_time", "href", "info"], ysygg_click(add_info(f1,{'gglx2':'验收预公告'})), ysygg_click(f2)],

    ["zfcg_gqita_yanshou_gg",
     "http://ggzy.luzhou.gov.cn/zfcg/005001/projectBuild_zfcg.html",
     ["name", "ggstart_time", "href", "info"], ysgg_click(f1), ysgg_click(f2)],

    ["zfcg_zhaobiao_wsjj_gg",
     "http://ggzy.luzhou.gov.cn/zfcg/005002/projectBuild_zfcg2.html",
     ["name", "ggstart_time", "href", "info"], cggg_click(add_info(f1, {'zbfs':"网上竞价"})), cggg_click(f2)],

    ["zfcg_zhongbiao_wsjj_gg",
     "http://ggzy.luzhou.gov.cn/zfcg/005002/projectBuild_zfcg2.html",
     ["name", "ggstart_time", "href", "info"], jggg_click(add_info(f1, {'zbfs':"网上竞价"})), jggg_click(f2)],

    ["zfcg_gqita_hetong_wsjj_gg",
     "http://ggzy.luzhou.gov.cn/zfcg/005002/projectBuild_zfcg2.html",
     ["name", "ggstart_time", "href", "info"], htgg_click(add_info(f1, {'zbfs':"网上竞价"})), htgg_click(f2)],

    ["zfcg_gqita_yuyanshou_wsjj_gg",
     "http://ggzy.luzhou.gov.cn/zfcg/005002/projectBuild_zfcg2.html",
     ["name", "ggstart_time", "href", "info"], ysygg_click(add_info(f1, {'zbfs':"网上竞价",'gglx2':'验收预公告'})), ysygg_click(f2)],

    ["zfcg_gqita_yanshou_wsjj_gg",
     "http://ggzy.luzhou.gov.cn/zfcg/005002/projectBuild_zfcg2.html",
     ["name", "ggstart_time", "href", "info"], ysgg_click(add_info(f1, {'zbfs':"网上竞价"})), ysgg_click(f2)],

    ["zfcg_zhaobiao_shangchang_gg",
     "http://ggzy.luzhou.gov.cn/zfcg/005003/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gglx2':'商场直购'}), f2],

    ["qsy_zhaobiao_gg",
     "http://ggzy.luzhou.gov.cn/qtjy/016001/list.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'jylx':'其他交易','gglx2':'国企采购'}), f2],

    ["qsy_gqita_gg",
     "http://ggzy.luzhou.gov.cn/qtjy/016003/list.html",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'其他交易','gglx2':'其他交易'}), f2],

]



def work(conp,**args):
    est_meta(conp,data=data,diqu="四川省泸州市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.4.175","sichuan","luzhou"])



