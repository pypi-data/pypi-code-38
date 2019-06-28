import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write,db_command,db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, NoAlertPresentException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import json
from zhulong.util.etl import add_info,est_meta,est_html,est_tbs


_name_="mianyang1"


def f1_1(driver, num):
    locator = (By.XPATH, "//table[@id='ctl00_ContentPlaceHolder1_myGV']/tbody/tr[2]/td/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//tr[@class='myGVPagerCss']/td/span[1]")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(str)
    except:
        cnum = 1
    url = driver.current_url
    if num != int(cnum):
        if num > int(cnum):
            t = num - int(cnum)
            for i in range(t):
                locator = (By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_myGV_ctl02_HLinkGcmc"]')
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
                driver.find_element_by_link_text('下一页').click()
            locator = (By.XPATH, '//tr[@class="myGVPagerCss"]/td/span[1]')
            cnum_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            if num != int(cnum_1):
                raise TimeoutError
        if num < int(cnum):
            t = int(cnum) - num
            for i in range(t):
                locator = (By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_myGV_ctl02_HLinkGcmc"]')
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
                driver.find_element_by_link_text('上一页').click()
            locator = (By.XPATH, '//tr[@class="myGVPagerCss"]/td/span[1]')
            cnum_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            if num != int(cnum_1):
                raise TimeoutError
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table", id='ctl00_ContentPlaceHolder1_myGV')
    trs = table.find_all("tr")
    data = []
    for tr in trs[1:-1]:
        a = tr.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        if 'http://ztb.my.gov.cn/ceinwz/WebInfo_List.aspx?' in url:
            link = "http://ztb.my.gov.cn/ceinwz/" + a['href'].strip()
        else:
            link = "http://caigou.my.gov.cn/ceinwz/" + a['href'].strip()
        try:
            td = tr.find("td", class_="fFbDate")
            span = td.find_all('span')[0].text.strip()
        except:
            span = '-'
        try:
            title = re.sub(r'^\[(.*)\]', '', title).strip()
            if '※' in title:
                title = re.sub(r'※', '', title).strip()
        except:
            title = title
            if '※' in title:
                title = re.sub(r'※', '', title).strip()
        tmp = [title, span, link]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f1_2(driver, num):
    locator = (By.XPATH, "//table[@id='ctl00_ContentPlaceHolder1_Tabs_tabpnlEnsure_myGVEnsure']/tbody/tr[2]/td/span")
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    try:
        locator = (By.XPATH, "//tr[@class='myGVPagerCss']/td[@colspan='3']/table/tbody/tr/td/span")
        total = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(total)
    except:
        cnum = 1
    url = driver.current_url
    if num != int(cnum):
        driver.execute_script("javascript:__doPostBack('ctl00$ContentPlaceHolder1$Tabs$tabpnlEnsure$myGVEnsure','Page${}')".format(num))
        try:
            locator = (By.XPATH,"//table[@id='ctl00_ContentPlaceHolder1_Tabs_tabpnlEnsure_myGVEnsure']/tbody/tr[2]/td/span[not(contains(string(), '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        except:
            driver.back()
            while True:
                driver.find_element_by_xpath("(//tr[@class='myGVPagerCss']//a)[last()-1]").click()
                locator = (By.XPATH, "(//tr[@class='myGVPagerCss']//a)[last()-1]")
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
                time.sleep(3)
                page = driver.page_source
                soup = BeautifulSoup(page, 'html.parser')
                trs = soup.find_all('tr', class_='myGVPagerCss')
                ss = 0
                for tr in trs:
                    ts = tr.find_all('a')
                    for t in ts:
                        t_num = t.text.strip()
                        if str(num) == str(t_num):
                            ss = 1
                            break
                if ss == 1:
                    break
            driver.execute_script("javascript:__doPostBack('ctl00$ContentPlaceHolder1$Tabs$tabpnlEnsure$myGVEnsure','Page${}')".format(num))
            locator = (By.XPATH,"//table[@id='ctl00_ContentPlaceHolder1_Tabs_tabpnlEnsure_myGVEnsure']/tbody/tr[2]/td/span[not(contains(string(), '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table", id='ctl00_ContentPlaceHolder1_Tabs_tabpnlEnsure_myGVEnsure')
    trs = table.find_all("tr")
    data = []
    for tr in trs[1:-2]:
        a = tr.find("span")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        link = "-"
        try:
            span = tr.find_all('td')[1].text.strip()
        except:
            span = '-'
        try:
            td = tr.find_all('td')[2].text.strip()
            tds = re.findall(r'\((.*)\)', td)
            td = tds[0] if tds else td
        except:
            td = None
        yy = {"yuanyin": td}
        info = json.dumps(yy, ensure_ascii=False)
        tmp = [title, span, link, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f1_3(driver, num):
    locator = (By.XPATH, "//table[@id='ctl00_ContentPlaceHolder1_BestNewsListALL_myGV']/tbody/tr[1]/td/a")
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    try:
        locator = (By.XPATH, "//span[@id='ctl00_ContentPlaceHolder1_BestNewsListALL_myGV_ctl13_lblPage']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = re.findall(r'第(\d+)页', str)[0]
        d = -1
    except:
        cnum = 1
        d = 0
    url = driver.current_url
    if num != int(cnum):
        locator = (By.XPATH, "//input[@id='ctl00_ContentPlaceHolder1_BestNewsListALL_myGV_ctl13_inPageNum']")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).clear()
        locator = (By.XPATH, "//input[@id='ctl00_ContentPlaceHolder1_BestNewsListALL_myGV_ctl13_inPageNum']")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).send_keys(num)
        locator = (By.XPATH, "//input[@id='ctl00_ContentPlaceHolder1_BestNewsListALL_myGV_ctl13_Button1']")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()

        locator = (By.XPATH, "//table[@id='ctl00_ContentPlaceHolder1_BestNewsListALL_myGV']/tbody/tr[1]/td/a[not(contains(string(), '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table", id='ctl00_ContentPlaceHolder1_BestNewsListALL_myGV')
    trs = table.find_all("tr")
    data = []
    for tr in trs[:d]:
        a = tr.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        if "http://ztb.my.gov.cn/ceinwz/xwmore.aspx?" in url:
            link = "http://ztb.my.gov.cn/ceinwz/" + a['href'].strip()
        else:
            link = "http://zfcg.my.gov.cn/ceinwz/" + a['href'].strip()
        try:
            span = re.findall(r'\((\d+-\d+-\d+)\)', title)[0]
        except:
            span = '-'
        tmp = [title, span, link]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def f1_4(driver, num):
    locator = (By.XPATH, "//table[@id='cgfsTable']/tbody/tr[1]/td/a")
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    try:
        locator = (By.XPATH, "//li[@class='active disabled']")
        st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        cnum = int(st)
    except:
        cnum = 1
    if num != int(cnum):
        driver.execute_script('SetPageIndex({})'.format(num))
        locator = (By.XPATH, "//table[@id='cgfsTable']/tbody/tr[1]/td/a[not(contains(string(), '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find("table", id='cgfsTable')
    tbody = table.find('tbody')
    trs = tbody.find_all("tr")
    data = []
    for tr in trs:
        a = tr.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()

        handle = driver.current_window_handle
        # 获取a标签的onclick属性文本
        onclick = a['onclick'].strip()
        # 执行js跳转详情页
        driver.execute_script(onclick)
        handles = driver.window_handles
        for newhandle in handles:
            if newhandle != handle:
                # 切换到新打开的窗口Blink
                driver.switch_to_window(newhandle)
                time.sleep(1)
                link = driver.current_url
                driver.close()
                driver.switch_to_window(handle)
        span = tr.find_all('td')[-1].text.strip()
        zbfs = tr.find_all('td')[0].text.strip()
        diqu = tr.find_all('td')[1].text.strip()
        if '[' in zbfs:
            zbfs = re.findall(r'\[(.*)\]', zbfs)[0]
        info = json.dumps({'zbfs':zbfs,'diqu':diqu}, ensure_ascii=False)
        tmp = [title, span, link, info]
        data.append(tmp)
    df = pd.DataFrame(data)
    return df


def f1(driver, num):
    url = driver.current_url
    if ('http://ztb.my.gov.cn/ceinwz/WebInfo_List.aspx?' in url) or ('http://caigou.my.gov.cn/ceinwz/WebInfo_List.aspx?' in url):
        df = f1_1(driver, num)
        return df
    elif 'http://ztb.my.gov.cn/ceinwz/cxzbxm.aspx?' in url:
        df = f1_2(driver, num)
        return df

    elif ('http://ztb.my.gov.cn/ceinwz/xwmore.aspx?' in url) or ('http://zfcg.my.gov.cn/ceinwz/xwmore.aspx?' in url):
        df = f1_3(driver, num)
        return df

    elif '/MianYang_New/NoticeList.aspx' in url:
        df = f1_4(driver, num)
        return df


def f2(driver):
    url = driver.current_url
    if ('http://ztb.my.gov.cn/ceinwz/WebInfo_List.aspx?' in url) or ('http://caigou.my.gov.cn/ceinwz/WebInfo_List.aspx?' in url):
        locator = (By.XPATH, "//table[@id='ctl00_ContentPlaceHolder1_myGV']/tbody/tr[2]/td/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, "//span[@id='ctl00_ContentPlaceHolder1_myGV_ctl23_LabelPageCount']")
            num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        except:
            num = 1
    elif 'http://ztb.my.gov.cn/ceinwz/cxzbxm.aspx?' in url:
        locator = (By.XPATH, "//table[@id='ctl00_ContentPlaceHolder1_Tabs_tabpnlEnsure_myGVEnsure']/tbody/tr[2]/td/span")
        val_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        try:
            driver.find_element_by_link_text('>>').click()
            locator = (By.XPATH,
                       "//table[@id='ctl00_ContentPlaceHolder1_Tabs_tabpnlEnsure_myGVEnsure']/tbody/tr[2]/td/span[not(contains(string(), '%s'))]" % val_1)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

            locator = (By.XPATH, "//tr[@class='myGVPagerCss']/td/table/tbody/tr/td[last()]/span")
            num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        except:
            num = 1
    elif ('http://ztb.my.gov.cn/ceinwz/xwmore.aspx?' in url) or ('http://zfcg.my.gov.cn/ceinwz/xwmore.aspx?' in url):
        locator = (By.XPATH, "//table[@id='ctl00_ContentPlaceHolder1_BestNewsListALL_myGV']/tbody/tr[1]/td/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, "//span[@id='ctl00_ContentPlaceHolder1_BestNewsListALL_myGV_ctl13_lblPage']")
            str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
            num = re.findall(r'共(\d+)页', str)[0]
        except:
            num = 1
    elif 'MianYang_New/NoticeList.aspx' in url:
        t = 0
        try:
            for _ in range(200):
                t += 1
                driver.execute_script('SetPageIndex({})'.format(t))
                locator = (By.XPATH, "//table[@id='cgfsTable']/tbody/tr[1]/td/a")
                val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
                if val is None:
                    break
        except:
            num = t-1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    try:
        alart = driver.switch_to.alert
        alart.accept()
    except:
        pass

    if 'http://myzc.my.gov.cn' in url:
        locator = (By.XPATH, "//div[@class='box-container'][string-length()>30]")
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
        div = soup.find('div', class_="box-container")
        return div
    if '/ceinwz/admin_show.aspx' in url:
        locator = (By.XPATH, "//div[@class='newsImage']")
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
        div = soup.find('div', class_="newsImage")
        return div
    else:
        time.sleep(2)
        if '<iframe id="frmBestwordHtml' in str(driver.page_source):
            driver.switch_to_frame('frmBestwordHtml')
            flag = 1
            if '找不到文件或目录' in str(driver.page_source):
                return 404
            locator = (By.XPATH, "//div[contains(@class, 'Section')][string-length()>30] | //embed[@id='plugin']")
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        else:
            flag = 2
            locator = (By.XPATH, "//table[@width='75%'][string-length()>30] | //div[@class='wrap'][string-length()>30] | //form[contains(@name, 'form1')][string-length()>30]")
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
            div = soup.find('div', class_=re.compile('.*?Section.*?'))
            if div == None:
                div = soup.find('embed', id='plugin')
        else:
            div = soup.find('form', id="form1")
            if div == None:
                div = soup.find('table', width="75%")
                if div == None:
                    div = soup.find('div', class_='wrap')
        return div


def zfcg_caigou(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, "//table[@id='cgfsTable']/tbody/tr[1]/td/a")
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        s1 = Select(driver.find_element_by_id('selGGType'))
        data = s1.first_selected_option.text.strip()
        if data != '采购公告':
            s1.select_by_visible_text("采购公告")
            time.sleep(1)
            locator = (By.XPATH, "//button[@class='btn btn-info']")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            try:
                locator = (By.XPATH,"//table[@id='cgfsTable']/tbody/tr[1]/td/a[not(contains(string(), '%s'))]" % val)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            except:
                time.sleep(1)

        return f(*krg)
    return wrap

def zfcg_jieguo(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, "//table[@id='cgfsTable']/tbody/tr[1]/td/a")
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        s1 = Select(driver.find_element_by_id('selGGType'))
        data = s1.first_selected_option.text.strip()
        if data != '结果公告':
            s1.select_by_visible_text("结果公告")
            time.sleep(1)
            locator = (By.XPATH, "//button[@class='btn btn-info']")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            try:
                locator = (By.XPATH,"//table[@id='cgfsTable']/tbody/tr[1]/td/a[not(contains(string(), '%s'))]" % val)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            except:
                time.sleep(1)

        return f(*krg)
    return wrap

def zfcg_biangen(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, "//table[@id='cgfsTable']/tbody/tr[1]/td/a")
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        s1 = Select(driver.find_element_by_id('selGGType'))
        data = s1.first_selected_option.text.strip()
        if data != '变更公告':
            s1.select_by_visible_text("变更公告")
            time.sleep(1)
            locator = (By.XPATH, "//button[@class='btn btn-info']")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            try:
                locator = (By.XPATH,"//table[@id='cgfsTable']/tbody/tr[1]/td/a[not(contains(string(), '%s'))]" % val)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            except:
                time.sleep(1)

        return f(*krg)
    return wrap


def zfcg_yanshouyugg(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, "//table[@id='cgfsTable']/tbody/tr[1]/td/a")
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        s1 = Select(driver.find_element_by_id('selGGType'))
        data = s1.first_selected_option.text.strip()
        if data != '竞价验收预公告':
            s1.select_by_visible_text("竞价验收预公告")
            time.sleep(1)
            locator = (By.XPATH, "//button[@class='btn btn-info']")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            try:
                locator = (By.XPATH,"//table[@id='cgfsTable']/tbody/tr[1]/td/a[not(contains(string(), '%s'))]" % val)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            except:
                time.sleep(1)

        return f(*krg)
    return wrap


def zfcg_yanshou(f):
    def wrap(*krg):
        driver = krg[0]
        locator = (By.XPATH, "//table[@id='cgfsTable']/tbody/tr[1]/td/a")
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        s1 = Select(driver.find_element_by_id('selGGType'))
        data = s1.first_selected_option.text.strip()
        if data != '竞价验收公告':
            s1.select_by_visible_text("竞价验收公告")
            time.sleep(1)
            locator = (By.XPATH, "//button[@class='btn btn-info']")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()
            try:
                locator = (By.XPATH,"//table[@id='cgfsTable']/tbody/tr[1]/td/a[not(contains(string(), '%s'))]" % val)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
            except:
                time.sleep(1)

        return f(*krg)
    return wrap


data = [
    ["gcjs_zhaobiao_gg",
     "http://ztb.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=100,106,112,118,124,130,136,142,148,154&jsgc=0100000&zfcg=&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=1&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=jsgcsgjl",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_liubiao_gg",
     "http://ztb.my.gov.cn/ceinwz/cxzbxm.aspx?xmlx=10&FromUrl=jsgcsgjl",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://ztb.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=103,109,115,121,127,133,139,145,151,157&jsgc=0000010&zfcg=&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=1&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=jsgcsgjl",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_bian_bu_gg",
     "http://ztb.my.gov.cn/ceinwz/WebInfo_List.aspx?jsgc=0011000&newsid=101,107,113,119,125,131,137,,143,149,155&qxid=1&FromUrl=jsgcsgjl",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_biangeng_gg",
     "http://ztb.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=104,110,116,122,128,134,140,146,152,158&jsgc=0000000&zfcg=&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=1&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=jsgcsgjl",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhaobiao_cailiao_gg",
     "http://ztb.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=200,206,212,218,224,230,236,242,248,254&jsgc=0000000&zfcg=&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=1&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=1&ShowOverDate=0&showdate=1&FromUrl=sbcllzb11",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'设备材料类'}), f2],

    ["gcjs_gqita_bian_bu_cailiao_gg",
     "http://ztb.my.gov.cn/ceinwz/xwmore.aspx?id=201,207,213,219,225,131,237,243,249,255&qxid=1&FromUrl=sbcllzb",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'设备材料类'}), f2],

    ["gcjs_zhongbiaohx_cailiao_gg",
     "http://ztb.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=203,209,215,221,227,233,239,245,251,257&jsgc=0000000&zfcg=&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=1&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=1&ShowOverDate=0&showdate=1&FromUrl=sbcllzb",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'设备材料类'}), f2],

    ["zfcg_zhaobiao_gg",
     "http://myzc.my.gov.cn/Style/MianYang_New/NoticeList.aspx",
    ["name", "ggstart_time", "href", "info"],zfcg_caigou(f1),zfcg_caigou(f2)],

    ["zfcg_gqita_zhong_liu_gg",
     "http://myzc.my.gov.cn/Style/MianYang_New/NoticeList.aspx",
     ["name", "ggstart_time", "href", "info"], zfcg_jieguo(f1), zfcg_jieguo(f2)],

    ["zfcg_biangeng_gg",
     "http://myzc.my.gov.cn/Style/MianYang_New/NoticeList.aspx",
     ["name", "ggstart_time", "href", "info"], zfcg_biangen(f1), zfcg_biangen(f2)],

    ["zfcg_gqita_yuyanshou_gg",
     "http://myzc.my.gov.cn/Style/MianYang_New/NoticeList.aspx",
     ["name", "ggstart_time", "href", "info"], zfcg_yanshouyugg(add_info(f1,{'gglx':'竞价验收预公告'})), zfcg_yanshouyugg(f2)],

    ["zfcg_gqita_yanshou_gg",
     "http://myzc.my.gov.cn/Style/MianYang_New/NoticeList.aspx",
     ["name", "ggstart_time", "href", "info"], zfcg_yanshou(add_info(f1,{'gglx':'竞价验收公告'})), zfcg_yanshou(f2)],

    ["zfcg_zhaobiao_danyilaiyuan_gg",
     "http://zfcg.my.gov.cn/ceinwz/xwmore.aspx?id=400&showdate=1&FromUrl=nourl",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs':'单一来源采购'}), f2],

    ["zfcg_yucai_gg",
     "http://zfcg.my.gov.cn/ceinwz/xwmore.aspx?id=401&showdate=1&FromUrl=nourl",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_shiji_gg",
     "http://caigou.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=601&jsgc=&zfcg=0100000&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=1&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=nourl",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu':'市级'}), f2],

    ["zfcg_biangeng_shiji_gg",
     "http://caigou.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=602&jsgc=&zfcg=0010000&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=0&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=nourl",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu':'市级'}), f2],

    ["zfcg_gqita_zhong_liu_shiji_gg",
     "http://caigou.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=604&jsgc=&zfcg=0000010&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=1&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=nourl",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu':'市级'}), f2],

    ["zfcg_zhaobiao_quxian_gg",
     "http://caigou.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=2000&jsgc=&zfcg=0000000&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=1&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=nourl",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu':'区县'}), f2],

    ["zfcg_biangeng_quxian_gg",
     "http://caigou.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=3000&jsgc=&zfcg=0000000&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=1&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=nourl",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu':'区县'}), f2],

    ["zfcg_gqita_zhong_liu_quxian_gg",
     "http://caigou.my.gov.cn/ceinwz/WebInfo_List.aspx?newsid=5000&jsgc=&zfcg=0000000&tdjy=&cqjy=&qtjy=&PubDateSort=0&ShowPre=1&CbsZgys=0&zbfs=&qxxx=0&showqxname=0&NewsShowPre=1&wsjj=0&showCgr=0&ShowOverDate=0&showdate=1&FromUrl=nourl",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu':'区县'}), f2],

]



def work(conp,**args):
    est_meta(conp,data=data,diqu="四川省绵阳市",**args)
    est_html(conp,f=f3,**args)

# 修改时间：2019/6/27
if __name__=='__main__':
    work(conp=["postgres","zhulong.com.cn","192.168.169.47","sichuan","mianyang1"],pageloadtimeout=120,pageloadstrategy="none",num=1,headless=False)
