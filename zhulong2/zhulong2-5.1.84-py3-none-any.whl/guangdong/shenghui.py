import random
import pandas as pd
import re
import requests
from lxml import etree
from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from zhulong2.util.etl import est_html, est_meta, add_info, est_meta_large
from zhulong2.util.fake_useragent import UserAgent
_name_ = "guangdong_shenghui"

n = 0
tt_url = None
tt = None
def f1_data(driver, num):
    try:
        locator = (By.XPATH, "//table[@class='m_m_dljg']/tbody/tr[2]/td[last()]/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    except:
        global n
        n += 1
        if n < 20:
            time.sleep(10*n)
            driver.refresh()
            return f1_data(driver, num)
        else:
            driver.refresh()
            locator = (By.XPATH, "//table[@class='m_m_dljg']/tbody/tr[2]/td[last()]/a")
            WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//span[@class='aspan1']")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        cnum = 1
    if num != int(cnum):
        val = driver.find_element_by_xpath("//table[@class='m_m_dljg']/tbody/tr[2]/td[last()]/a").get_attribute('href')[-30:]
        driver.execute_script("javascript:turnOverPage({})".format(num))
        locator = (By.XPATH, "//table[@class='m_m_dljg']/tbody/tr[2]/td[last()]/a[not(contains(@href, '%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    n = 0
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    tbody = soup.find("table", class_="m_m_dljg")
    trs = tbody.find_all("tr")
    data = []
    url = driver.current_url
    for tr in trs[1:]:
        a = tr.find_all('a')[-1]
        if ('queryAcceptanceList.do' in url) or ('queryCityAcceptanceList.do' in url):
            try:
                title = tr.find_all('td')[1]['title'].strip()
            except:
                title = tr.find_all('td')[1].text.strip()
        else:
            try:
                title = tr.find_all('td')[3]['title'].strip()
            except:
                title = tr.find_all('td')[3].text.strip()
        if 'queryPrjReqList.do' in url:
            td = tr.find_all('td')[-3].text.strip()
        elif ('queryAcceptanceList.do' in url) or ('queryCityAcceptanceList.do' in url):
            td = tr.find_all('td')[-5].text.strip()
        else:
            td = tr.find_all('td')[-4].text.strip()
        href = a['href'].strip()
        link = 'http://www.gdgpo.gov.cn' + href

        info = {'info_html': '{}'.format(tr)}
        info = json.dumps(info, ensure_ascii=False)
        tmp = [title, td, link, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f1(driver, num):
    time.sleep(random.uniform(1, 3))
    url = driver.current_url
    if ('queryPlanList.do' in url) or ('queryPrjReqList.do' in url) or ('queryAcceptanceList.do' in url) or ('queryCityPlanList.do' in url) or ('queryCityAcceptanceList.do' in url):
        df = f1_data(driver, num)
        return df
    else:
        try:
            proxies_data = webdriver.DesiredCapabilities.CHROME
            proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
            proxy = proxies_chromeOptions[0].split('=')[1]
            proxies = {'http': '%s' % proxy}
        except:
            proxies = ''
        user_agents = UserAgent()
        user_agent = user_agents.chrome
        headers = {
            # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            # # 'Connection': 'keep-live',
            # 'Content-Type': 'application/x-www-form-urlencoded',
            # 'Upgrade-Insecure-Requests': '1',
            # 'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent': user_agent,
        }
        payloadData = {
            'channelCode': tt,
            'pageIndex': num,
            'pageSize': 15,
            'pointPageIndexId': num-1,
        }
        # 下载超时
        timeOut = 120
        if proxies:
            res = requests.post(url=tt_url, headers=headers, data=payloadData, proxies=proxies, timeout=timeOut)
        else:
            res = requests.post(url=tt_url, headers=headers, data=payloadData, timeout=timeOut)
        # 需要判断是否为登录后的页面
        if res.status_code != 200:
            global n
            n += 1
            if n < 20:
                time.sleep(10 * n)
                return f1(driver, num)
            else:
                raise ConnectionError
        else:
            # print(html)
            try:
                html = res.text
                soup = BeautifulSoup(html, 'html.parser')
                uls = soup.find("ul", class_="m_m_c_list")
                lis = uls.find_all("li")
            except:
                global n
                n += 1
                if n < 20:
                    time.sleep(10*n)
                    return f1(driver, num)
                else:
                    raise ConnectionError
            data = []
            n = 0
            for tr in lis:
                a = tr.find_all('a')
                try:
                    title = a[-1]['title'].strip()
                except:
                    title = a[-1].text.strip()
                td = tr.find('em').text.strip()
                href = a[-1]['href'].strip()
                if 'http' in href:
                    link = href
                else:
                    link = 'http://www.gdgpo.gov.cn' + href
                span = tr.find('span').text.strip()
                info = {}
                try:
                    leixing = span.split('·')[0].split('[')[1].strip()
                    diqu = span.split('·')[1].split(']')[0].strip()
                    info['lx'] = leixing
                    info['diqu'] = diqu
                except:
                    diqu = span.split('[')[1].split(']')[0].strip()
                    info['diqu'] = diqu
                if info:
                    info = json.dumps(info, ensure_ascii=False)
                else:
                    info = 'none'
                tmp = [title, td, link, info]
                data.append(tmp)
            df = pd.DataFrame(data=data)
            return df




def f2(driver):
    url = driver.current_url
    if ('queryPlanList.do' in url) or ('queryPrjReqList.do' in url) or ('queryAcceptanceList.do' in url) or ('queryCityPlanList.do' in url) or ('queryCityAcceptanceList.do' in url):
        locator = (By.XPATH, "//table[@class='m_m_dljg']/tbody/tr[2]/td[last()]/a")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        try:
            locator = (By.XPATH, "(//span[@class='aspan'])[last()]")
            num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        except:
            num = 1
        driver.quit()
        return int(num)
    else:
        global tt_url,tt
        tt_url = None
        tt = None
        start_url = driver.current_url
        tt_url = start_url.rsplit('/', maxsplit=1)[0]
        tt = start_url.rsplit('/', maxsplit=1)[1]
        page_num = get_pageall(tt_url, tt)
        driver.quit()
        return int(page_num)


def get_pageall(tt_url, tt):
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        # # 'Connection': 'keep-live',
        # 'Content-Type': 'application/x-www-form-urlencoded',
        # 'Upgrade-Insecure-Requests': '1',
        # 'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': user_agent,
    }
    payloadData = {
        'channelCode': tt,
        'pageIndex': 1,
        'pageSize': 15,
        'pointPageIndexId': 1,
    }
    # 下载超时
    timeOut = 120
    res = requests.post(url=tt_url, headers=headers, data=payloadData, timeout=timeOut)
    # 需要判断是否为登录后的页面
    if res.status_code == 200:
        try:
            html = res.text
            soup = BeautifulSoup(html, 'html.parser')
            total = soup.find_all('span', class_='aspan')[-1].text.strip()
        except:
            global n
            n += 1
            if n < 10:
                time.sleep(10)
                return get_pageall(tt_url, tt)
            else:
                raise ConnectionError
        n = 0
        num = int(total)
        return num


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='zw_c_c_cont'][string-length()>10]")
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
    div = soup.find('div', class_='zw_c_cont')
    return div


data = [
    ["zfcg_yucai_gg", "http://www.gdgpo.gov.cn/queryPrjReqList.do",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_zhao_liu_pljz_gg", "http://www.gdgpo.gov.cn/queryMoreInfoList.do/-3",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '批量集中采购'}), f2],

    ["zfcg_gqita_zhong_liu_wsjj_gg", "http://www.gdgpo.gov.cn/queryMoreInfoList.do/-5",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '网上竞价'}), f2],

    ["zfcg_zhongbiao_ddcg_gg", "http://www.gdgpo.gov.cn/queryMoreInfoList.do/000815",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '定点采购'}), f2],

    ["zfcg_zhaobiao_danyilaiyuan_gg", "http://www.gdgpo.gov.cn/queryMoreInfoList.do/-4",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '单一来源'}), f2],

    ["zfcg_gqita_cgjh_shengji_gg", "http://www.gdgpo.gov.cn/queryPlanList.do",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '采购计划', 'dq': '省级'}), f2],

    ["zfcg_gqita_cgjh_shixian_gg", "http://www.gdgpo.gov.cn/queryCityPlanList.do",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'gglx': '地方采购计划', 'dq': '市县'}), f2],

    ["zfcg_yanshou_shengji_gg", "http://www.gdgpo.gov.cn/queryAcceptanceList.do",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'dq': '省级'}), f2],

    ["zfcg_yanshou_shixian_gg", "http://www.gdgpo.gov.cn/queryCityAcceptanceList.do",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'dq': '市县'}), f2],
    ###
    ["zfcg_zhaobiao_shengji_gg", "http://www.gdgpo.gov.cn/queryMoreInfoList.do/0005",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'dq': '省级'}), f2],

    ["zfcg_biangeng_shengji_gg", "http://www.gdgpo.gov.cn/queryMoreInfoList.do/0006",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'dq': '省级'}), f2],

    ["zfcg_zhongbiao_shengji_gg", "http://www.gdgpo.gov.cn/queryMoreInfoList.do/0008",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'dq': '省级'}), f2],

    ["zfcg_gqita_fanpai_shengji_gg", "http://www.gdgpo.gov.cn/queryMoreInfoList.do/0017",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'dq': '省级', 'gglx': '电子反拍公告'}), f2],
    ###
    ["zfcg_zhaobiao_shixian_gg", "http://www.gdgpo.gov.cn/queryMoreCityCountyInfoList2.do/0005",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'dq': '市县'}), f2],

    ["zfcg_biangeng_shixian_gg", "http://www.gdgpo.gov.cn/queryMoreCityCountyInfoList2.do/0006",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'dq': '市县'}), f2],

    ["zfcg_zhongbiao_shixian_gg", "http://www.gdgpo.gov.cn/queryMoreCityCountyInfoList2.do/0008",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'dq': '市县'}), f2],

    ["zfcg_gqita_fanpai_shixian_gg", "http://www.gdgpo.gov.cn/queryMoreCityCountyInfoList2.do/0017",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'dq': '市县', 'gglx': '电子反拍公告'}), f2],

]

def work(conp, **args):
    est_meta_large(conp, data=data, diqu="广东省省会", **args)
    est_html(conp, f=f3, **args)


# 页数太多，跑不完，总是会跳回首页，详情页加载慢
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "guangdong"],pageloadtimeout=120,interval_page=100,num=45)

    # driver=webdriver.Chrome()
    # url = "http://www.gdgpo.gov.cn/queryMoreInfoList.do/-4"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    # driver=webdriver.Chrome()
    # url = "http://www.gdgpo.gov.cn/queryMoreInfoList.do/-4"
    # driver.get(url)
    # for i in range(6, 10):
    #     df=f1(driver, i)
    #     print(df.values)
