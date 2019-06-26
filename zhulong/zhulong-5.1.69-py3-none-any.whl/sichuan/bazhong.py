import random
import pandas as pd
import re
import requests
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
from zhulong.util.fake_useragent import UserAgent

_name_="bazhong"


endTime = time.strftime('%Y-%m-%d',time.localtime(time.time()))



def f1(driver, num):
    url = driver.current_url
    mcode = re.findall(r'/mcode=(.*)', url)[0]
    stsrt_url = url.rsplit('/', maxsplit=1)[0]
    Data = {
        'mcode': mcode,
        'clicktype': '1',
        'pageNum': '{}'.format(num),
        'keyname': '',
        'areacode': '',
    }
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'User-Agent': user_agent,
    }
    res = requests.post(url=stsrt_url, headers=headers, data=Data)
    # 需要判断是否为登录后的页面
    if res.status_code == 200:
        page = res.text
        if page:
            json_data = json.loads(page)
            datas = json_data['data']
            content = datas['content']
            data_list = []
            for li in content:
                diqu = li['areaname']
                title = li['mctype']
                span = li['mckeys']
                link = 'http://117.172.156.43:82/pub/BZ_indexContent_' + li['id'] + '.html'
                if diqu:
                    info = json.dumps({'diqu':diqu}, ensure_ascii=False)
                else:info = None
                tmp = [title, span, link, info]
                data_list.append(tmp)
            df = pd.DataFrame(data_list)
            return df


def f2(driver):
    url = driver.current_url
    mcode = re.findall(r'/mcode=(.*)', url)[0]
    stsrt_url = url.rsplit('/', maxsplit=1)[0]
    Data = {
        'mcode': mcode,
        'clicktype': '1',
        'pageNum': '1',
        'keyname': '',
        'areacode':'',
    }
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'User-Agent': user_agent,
    }
    res = requests.post(url=stsrt_url, headers=headers, data=Data)
    # 需要判断是否为登录后的页面
    if res.status_code == 200:
        page = res.text
        if page:
            json_data = json.loads(page)
            datas = json_data['data']
            totalPages = datas['totalPages']
            num = totalPages
            driver.quit()
            return int(num)



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='detail-box'][string-length()>40]")
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
    div = soup.find('div', class_="detail-box")
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://117.172.156.43:82/pub/showMcontent/mcode=JYGCJS_ZBGG",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_bian_cheng_gg",
     "http://117.172.156.43:82/pub/showMcontent/mcode=JYGCJS_CQXG",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiaohx_gg",
     "http://117.172.156.43:82/pub/showMcontent/mcode=JYGCJS_ZBHX",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiao_gg",
     "http://117.172.156.43:82/pub/showMcontent/mcode=JYGCJS_ZBJG",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_liu_zhongz_gg",
     "http://117.172.156.43:82/pub/showMcontent/mcode=JYGCJS_LBZZ",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_yucai_gg",
     "http://117.172.156.43:82/pub/showMcontent/mcode=JYZFCG_XQLZ",
    ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_gqita_yuzhaobiao_gg",
     "http://117.172.156.43:82/pub/showMcontent/mcode=JYZFCG_CGNR",
    ["name", "ggstart_time", "href", "info"],add_info(f1, {'gglx':'采购内容'}),f2],

    ["zfcg_zhaobiao_gg",
     "http://117.172.156.43:82/pub/showMcontent/mcode=JYZFCG_CGGG",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "http://117.172.156.43:82/pub/showMcontent/mcode=JYZFCG_GZGG",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_zhong_liu_gg",
     "http://117.172.156.43:82/pub/showMcontent/mcode=JYZFCG_JGGG",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="四川省巴中市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","sichuan","bazhong"])

