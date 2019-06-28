import pandas as pd
import re

import requests
from zhulong.util.fake_useragent import UserAgent
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write,db_command,db_query
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import json
from zhulong.util.etl import add_info,est_meta,est_html,est_tbs


_name_="ningbo"


def f1(driver, num):
    url = driver.current_url
    if "http://www.bidding.gov.cn/" not in url:
        tmp = get_data(driver, num)
        df = pd.DataFrame(data=tmp)
        df['info'] = None
        return df
    locator = (By.XPATH, "//div[@class='c1-body']/li[1]/a")
    val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-12:]

    locator = (By.XPATH, "//div[@class='pg-3']/div")
    st = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
    cnum = re.findall(r'(\d+)/', st)[0]
    if num != int(cnum):
        if 'index.htm' in url:
            s = "index_%d" % (num) if num > 1 else "index_1"
            url = re.sub('index', s, url)
        if num == 1:
            url = re.sub("index_[0-9]*", "index_1", url)
        else:
            s = "index_%d" % (num) if num > 1 else "index_1"
            url = re.sub("index_[0-9]*", s, url)
        driver.get(url)
        locator = (By.XPATH, "//div[@class='c1-body']/li[1]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div= soup.find("div", class_='c1-body')
    trs = div.find_all("li")
    data = []
    for tr in trs:
        a = tr.find("a")
        try:
            link = a["href"]
        except:
            continue
        span = tr.find("span").text
        tmp = [a["title"].strip(), span.strip(), "http://www.bidding.gov.cn"+link.strip()]
        data.append(tmp)
    df = pd.DataFrame(data)
    df['info'] = None
    return df


def get_data(driver, num):
    url = driver.current_url
    if "http://www.nbuci.com/Newsinfo/list.aspx?" in url:
        locator = (By.XPATH, "//*[@id='ctl00_ContentPlaceHolder1_rpLists_ctl00_hyLink']")
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-30:]

        locator = (By.XPATH, "//*[@id='ctl00_ContentPlaceHolder1_bottomfy_CurPage']")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
        if num != int(cnum):
            driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_bottomfy_TextBoxGoto"]').clear()
            time.sleep(0.5)
            driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_bottomfy_TextBoxGoto"]').send_keys(num, Keys.ENTER)
            locator = (By.XPATH, "//*[@id='ctl00_ContentPlaceHolder1_rpLists_ctl00_hyLink'][not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        div = soup.find("table", id='ctl00_ContentPlaceHolder1_TablerpLists')
        trs = div.find_all("table")
        data = []
        for tr in trs:
            a = tr.find('a')
            title = a['title']
            links = a['href']
            link = re.sub(r'\.\./', 'http://www.nbuci.com/', links)
            date = tr.find('td', width="20%")
            tmp = [title.strip(), date.text.strip(), link]
            data.append(tmp)
        return data

    elif 'http://www.nbjttz.com/ztzl/cggs/' in url:
        locator = (By.XPATH, "(//a[@class='style_blue12'])[1]")
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-12:]
        locator = (By.XPATH, "//table[@width='97%']//td[@align='center']/div")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
        cnum = re.findall(r'(\d+)/', cnum)[0]
        if num != int(cnum):
            if "index.jhtml" in url:
                s = "index_%d.jhtml" % (num) if num > 1 else "index_1.jhtml"
                url = re.sub("index\.jhtml", s, url)
            elif num == 1:
                url = re.sub("index_[0-9]*", "index_1", url)
            else:
                s = "index_%d" % (num) if num > 1 else "index_1"
                url = re.sub("index_[0-9]*", s, url)
            driver.get(url)
            locator = (By.XPATH, "(//a[@class='style_blue12'])[1][not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        div = soup.find("table", class_='con_list')
        trs = div.find_all("tr")
        data = []
        for tr in trs:
            a = tr.find('a')
            title = a['title']
            link = a['href']
            dates = tr.find('td', width="12%").text.strip()
            date = re.findall(r'\[(.*)\]', dates)[0]
            tmp = [title.strip(), date, "http://www.nbjttz.com"+link]
            data.append(tmp)
        return data

    elif 'http://www.ndig.com.cn/cat/' in url:
        locator = (By.XPATH, "//*[@id='newslist']/li[1]/a")
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-12:]
        locator = (By.XPATH, "//td[@id='pagelist']")
        cnmm = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
        cnum = re.findall(r'(\d+) /', cnmm)[0]
        if num != int(cnum):
            driver.execute_script('javascript:showNews({})'.format(12*(num-1)))
            locator = (By.XPATH, "//*[@id='newslist']/li[1]/a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        div = soup.find("ul", id='newslist')
        trs = div.find_all("li")
        data = []
        for tr in trs:
            a = tr.find('a')
            title = a.text
            link = a['href']
            date = tr.find('span', class_="time").text.strip()
            tmp = [title.strip(), date, "http://www.ndig.com.cn"+link]
            data.append(tmp)
        return data

    elif 'http://www.nbmetro.com/index.php?' in url:
        locator = (By.XPATH, "(//p[@class='fl']/a)[1]")
        val = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).get_attribute('href')[-10:]
        try:
            locator = (By.XPATH, "//a[@class='active']")
            cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        except:
            cnum = 1
        if num != int(cnum):
            url = url.rsplit('/', maxsplit=1)[0] + '/{}'.format(num)
            driver.get(url)
            locator = (By.XPATH, "(//p[@class='fl']/a)[1][not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        div = soup.find("ul", class_='about-list f-cb')
        trs = div.find_all("li")
        data = []
        for tr in trs:
            a = tr.find('a')
            title = a.text
            link = a['href']
            date = tr.find('p', class_="fr").text.strip()
            tmp = [title.strip(), date, "http://www.nbmetro.com/"+link]
            data.append(tmp)
        return data

    elif 'http://www.nbgz.gov.cn/col' in url:
        columnid = re.findall(r'col/col(\d+)/', url)[0]
        unitid = re.findall(r'uid=(\d+)', url)[0]
        user_agents = UserAgent()
        user_agent = user_agents.chrome
        start_url = "http://www.nbgz.gov.cn/module/web/jpage/dataproxy.jsp?startrecord={}&endrecord={}&perpage=15".format(((num-1)*3*15+1), (num*3*15))
        headers = {
            'User-Agent': user_agent,
        }
        data = {
            "col": "1",
            "webid": "38",
            "path": "/",
            "columnid": columnid,
            "sourceContentType": "1",
            "unitid": unitid,
            "webname": "宁波市国资委",
            "permissiontype": "0",
        }
        res = requests.post(url=start_url, headers=headers, data=data)
        if res.status_code == 200:
            page = res.text
            if page:
                page = re.findall(r'<recordset>(.*)</recordset>', page)[0]
                soup = BeautifulSoup(page, 'html.parser')
                divs = soup.find_all('record')
                data_list = []
                for div in divs:
                    lis = re.findall(r'CDATA\[(.*)\]\]></record>', str(div))[0]
                    soup = BeautifulSoup(lis, 'html.parser')
                    lis = soup.find_all('li')
                    for li in lis:
                        a = li.find('a')
                        title = a.text.strip()
                        link = 'http://www.nbgz.gov.cn' + a['href'].strip()
                        span = li.find('p').text.strip()
                        tmp = [title, span, link]
                        data_list.append(tmp)
                df = pd.DataFrame(data_list)
                df['info'] =None
                return df


def f2(driver):
    url = driver.current_url
    if "http://www.nbuci.com/Newsinfo/list.aspx?" in url:
        locator = (By.XPATH, "//*[@id='ctl00_ContentPlaceHolder1_rpLists_ctl00_hyLink']")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, "//*[@id='ctl00_ContentPlaceHolder1_bottomfy_SumPage']")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
        num = int(str)

    elif 'http://www.nbjttz.com/ztzl/cggs/' in url:
        locator = (By.XPATH, "(//a[@class='style_blue12'])[1]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, "//table[@width='97%']//td[@align='center']/div")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
        num = re.findall(r'/(\d+)', cnum)[0]

    elif 'http://www.ndig.com.cn/' in url:
        locator = (By.XPATH, "//*[@id='newslist']/li[1]/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, "//td[@id='pagelist']")
        cnmm = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
        num = re.findall(r'/ (\d+)', cnmm)[0]

    elif 'http://www.nbmetro.com/index.php?' in url:
        locator = (By.XPATH, "(//p[@class='fl'])[1]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, "//div[@class='page']/a[11]")
            cnmm = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
            num = re.findall(r'(\d+)', cnmm)[0]
        except:
            num = 1

    elif 'http://www.nbgz.gov.cn/col' in url:
        locator = (By.XPATH, "//ul[@class='list-content']/li[1]")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, "//span[@class='default_pgTotalPage']")
        cnmm = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = int(cnmm)
        if int(num)/3 == int(int(num)/3):
            num = int(int(num) / 3)
        else:
            num = int(int(num) / 3) + 1

    else:
        locator = (By.XPATH, "//div[@class='c1-body']/li[1]/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        locator = (By.XPATH, "//div[@class='pg-3']/div")
        str = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text
        num = re.findall(r'/(\d+)', str)[0]
    driver.quit()
    return int(num)

def f3_1(driver, url):
    driver.get(url)
    locator = (By.CLASS_NAME, "largefont")
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
    table = soup.find('table', attrs={'width':'84%', 'height':'357'})
    div = table.find('tbody')
    return div

def f3_2(driver, url):
    driver.get(url)
    if "详见链接" in driver.page_source:
        locator = (By.XPATH, "//*[@id='content']")
        source = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        link = re.findall(r'(http.*)', source)[0].strip()
        driver.get(link)
        locator = (By.CLASS_NAME, "siteToolbar")
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
        div = soup.find('div', class_='frameNews')
        return div

    locator = (By.XPATH, "//div[@id='content']")
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
    div = soup.find('div', id='content')
    return div

def f3_3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='wordsbox']")
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
    div = soup.find('div', class_='wordsbox')
    return div

def f3_4(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='news-content-text-wrap']")
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
    div = soup.find('div', class_='news-content-text-wrap')
    return div

def f3_5(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='zoom']")
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
    div = soup.find('div', id='zoom')
    return div


def f3(driver, url):
    if "http://www.nbuci.com/" in url:
        df = f3_1(driver, url)
        return df
    elif "http://www.nbjttz.com/" in url:
        df = f3_2(driver, url)
        return df
    elif "http://www.ndig.com.cn/" in url:
        df = f3_3(driver, url)
        return df
    elif "http://www.nbmetro.com/" in url:
        df = f3_4(driver, url)
        return df
    elif "http://www.nbgz.gov.cn/" in url:
        df = f3_5(driver, url)
        return df
    else:
        driver.get(url)
        locator = (By.XPATH, "//div[@class='frameNews']")
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
        div = soup.find('div', class_='frameNews')
        return div


data = [
    ["gcjs_zhaobiao_gg","http://www.bidding.gov.cn/gcjszbgg/index.htm",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiaohx_gg", "http://www.bidding.gov.cn/gcjsyzbgg/index.htm",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiao_gg", "http://www.bidding.gov.cn/gcjszbgg1/index.htm",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_yuzhaobiao_gg", "http://www.bidding.gov.cn/gcjszbwjygs/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'gglx':'招标文件预公示'}), f2],


    ["zfcg_zhaobiao_gg", "http://www.bidding.gov.cn/zfcgcggg/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_zhong_bian_gg", "http://www.bidding.gov.cn/zfcggggg/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_zhao_bu_gg", "http://www.bidding.gov.cn/zfcgcgyg/index.htm",
     ["name", "ggstart_time", "href", "info"], f1, f2],


    ["qsy_zhaobiao_gg", "http://www.bidding.gov.cn/clsbzbgg/index.htm",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'材料与设备'}),f2],

    ["qsy_zhongbiaohx_gg", "http://www.bidding.gov.cn/jsgcclsbzbgg/index.htm",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'材料与设备'}),f2],

    ["qsy_zhongbiao_gg", "http://www.bidding.gov.cn/clysbzbgg/index.htm",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'材料与设备'}),f2],

    ["qsy_gqita_yuzhaobiao_gg", "http://www.bidding.gov.cn/clysbzbwjygs/index.htm",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'材料与设备','gglx':'招标文件预公示'}), f2],


    ["jqita_zhaobiao_gg", "http://www.bidding.gov.cn/qtjygg/index.htm",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'其他公共资源交易'}),f2],

    ["jqita_zhongbiaohx_gg", "http://www.bidding.gov.cn/qtjyjggs/index.htm",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'其他公共资源交易'}),f2],

    ["jqita_zhongbiao_gg", "http://www.bidding.gov.cn/qtzbjg/index.htm",
     ["name", "ggstart_time", "href", "info"],add_info(f1,{'jylx':'其他公共资源交易'}),f2],


    ["jqita_gqita_zhao_bian_gc_gqzb5_gg", "http://www.nbgz.gov.cn/col/col9152/index.html?uid=37342&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'宁波市国有资产监督管理委员会市属国企'}), f2],

    ["jqita_zhongbiao_gc_gqzb5_gg", "http://www.nbgz.gov.cn/col/col9153/index.html?uid=37342&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'宁波市国有资产监督管理委员会市属国企'}), f2],

    ["jqita_gqita_zhao_bu_wz_gqzb5_gg", "http://www.nbgz.gov.cn/col/col9154/index.html?uid=37342&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'宁波市国有资产监督管理委员会市属国企'}), f2],

    ["jqita_zhongbiao_wz_gqzb5_gg", "http://www.nbgz.gov.cn/col/col9155/index.html?uid=37342&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'宁波市国有资产监督管理委员会市属国企'}), f2],

    ["jqita_gqita_zhao_zhong_gqzb5_gg", "http://www.nbgz.gov.cn/col/col9151/index.html?uid=36558&pageNum=1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'宁波市国有资产监督管理委员会市属国企'}), f2],


    ["jqita_zhaobiao_gqzb4_gg", "http://www.nbmetro.com/index.php?tender_report/index/1/1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'宁波轨道交通网'}), f2],

    ["jqita_zhongbiao_gqzb4_gg", "http://www.nbmetro.com/index.php?tender_report/index/2/1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'宁波轨道交通网'}), f2],

    ["jqita_gqita_bixuan_gqzb4_gg", "http://www.nbmetro.com/index.php?tender_report/index/10/1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'宁波轨道交通网','gglx':'比选公告'}), f2],

    ["jqita_gqita_bixuanjieguo_gqzb4_gg", "http://www.nbmetro.com/index.php?tender_report/index/11/1",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'宁波轨道交通网','gglx':'比选结果公示'}), f2],

    ["jqita_zhaobiao_gqzb3_gg", "http://www.ndig.com.cn/cat/cat26/index.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'宁波开发投资集团'}), f2],

    ["jqita_gqita_zhao_zhong_gqzb2_gg", "http://www.nbjttz.com/ztzl/cggs/index.jhtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'宁波交通投资控股有限公司'}), f2],

    ["jqita_gqita_zhao_zhong_gqzb1_gg", "http://www.nbuci.com/Newsinfo/list.aspx?path_id=000000100701082",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'jylx':'宁波城建投资控股有限公司'}), f2],

    ["jqita_zhongbiao_lishi_gg", "http://www.bidding.gov.cn/lszbggcx/index.htm",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx':'历史中标公告查询'}), f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="浙江省宁波市",**args)
    est_html(conp,f=f3,**args)

# 修改日期：2019/6/28
if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","zhejiang","ningbo"])




